from numpy.lib.function_base import append
from pandas._libs.tslibs import timestamps
import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import date, datetime
import datetime
import sqlite3


def check_if_valid_data(df: pd.DataFrame) -> bool:
    #Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False
    
    #Primary key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is violated")
    
    #Check for nulls
    if df.isnull().values.any():
        raise Exception("Null valued found")
    
    ## Check that all timestamps are of yesterday's date
    # yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    # yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # timestamps = df["timestamps"].tolist()
    # for timestamp in timestamps:
    #     if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
    #         raise Exception("At least one of the returned songs does not come from within the last 24 hours")
    
    return True


# Extract Data

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "juan-qui"
TOKEN = "BQDhjJYTDWIE8atDdSqMhGSiktQAUhAlwY41_J_2mLf0K_xiBeuRq9-GnBQyVOF62kj_AgfmPgBPT_NpXfIxTXHnaHijPuJEYEUDQBrkQLIQ8Q8r4LKptzEoSvrALbrp6Gf00PiZXTk7ECCqmg"

if __name__ == "__main__":
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=60)
    yesterday_unix_timestamp = int(yesterday.timestamp())*1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers= headers)
    data = r.json()

    song_name =[]
    artist_name =[]
    played_at_list =[]
    timestamps =[]

    for song in data["items"]:
        song_name.append(song["track"]["name"])
        artist_name.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict ={
        "song_name" : song_name,
        "artist_name" : artist_name,
        "played_at" : played_at_list,
        "timestamps" : timestamps
    }
    
    song_df = pd.DataFrame(song_dict, columns=["song_name","artist_name","played_at","timestamps"])

print(song_df)

# Validate
if check_if_valid_data(song_df):
    print("Valid data, let's proceed to loading!")

# Load

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('my_played_tracks.sqlite')
cursor = conn.cursor()

sql_query = """
CREATE TABLE IF NOT EXISTS my_played_tracks(
    song_name VARCHAR(200),
    artist_name VARCHAR(200),
    played_at VARCHAR(200),
    timestamps VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
)
"""

cursor.execute(sql_query)

try:
    song_df.to_sql('my_played_tracks',engine, index=False, if_exists='append')
except:
    print("There was an issue loading the data")

conn.close()
print("Close database successfully")

