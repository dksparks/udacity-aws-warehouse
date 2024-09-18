import configparser

# CONFIG

config = configparser.ConfigParser()
config.read("dwh.cfg")

iam_role_arn = config.get("IAM_ROLE", "ARN")
log_data = config.get("S3", "LOG_DATA")
log_jsonpath = config.get("S3", "LOG_JSONPATH")
song_data = config.get("S3", "SONG_DATA")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create = """
CREATE TABLE staging_events (
    event_id INTEGER IDENTITY(0, 1) PRIMARY KEY,
    artist VARCHAR(200),
    auth VARCHAR(50),
    firstName VARCHAR(50),
    gender VARCHAR(10),
    itemInSession INTEGER,
    lastName VARCHAR(50),
    length REAL,
    level VARCHAR(20),
    location VARCHAR(200),
    method VARCHAR(20),
    page VARCHAR(100),
    registration DECIMAL(20, 1),
    sessionId INTEGER,
    song VARCHAR(200),
    status INTEGER,
    ts BIGINT,
    userAgent VARCHAR(500),
    userId VARCHAR(10)
)
"""

staging_songs_table_create = """
CREATE TABLE staging_songs (
    artist_id VARCHAR(50),
    artist_latitude REAL,
    artist_location VARCHAR(200),
    artist_longitude REAL,
    artist_name VARCHAR(200),
    duration REAL,
    num_songs INTEGER,
    song_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200),
    year INTEGER
)
"""

songplay_table_create = """
CREATE TABLE songplays (
    songplay_id INTEGER IDENTITY(0, 1) PRIMARY KEY,
    start_time TIMESTAMP NOT NULL DISTKEY SORTKEY,
    user_id INTEGER NOT NULL,
    level VARCHAR(20),
    song_id VARCHAR(50) NOT NULL,
    artist_id VARCHAR(50) NOT NULL,
    session_id INTEGER,
    location VARCHAR(200),
    user_agent VARCHAR(500)
)
"""

user_table_create = """
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender VARCHAR(10),
    level VARCHAR(20)
)
"""

song_table_create = """
CREATE TABLE songs (
    song_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200),
    artist_id VARCHAR(50) NOT NULL,
    year INTEGER,
    duration REAL
)
"""

artist_table_create = """
CREATE TABLE artists(
    artist_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200),
    location VARCHAR(200),
    latitude REAL,
    longitude REAL
)
"""

time_table_create = """
CREATE TABLE time (
    start_time TIMESTAMP PRIMARY KEY,
    hour INTEGER NOT NULL,
    day INTEGER NOT NULL,
    week INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    weekday INTEGER NOT NULL
)
"""

# STAGING TABLES

staging_events_copy = """
copy staging_events from {} iam_role {} region='us-west-2' json {}
""".format(
    log_data, iam_role_arn, log_jsonpath
)

staging_songs_copy = """
copy staging_songs from {} iam_role {} region='us-west-2' json 'auto'
""".format(
    song_data, iam_role_arn
)

# FINAL TABLES

songplay_table_insert = """
INSERT INTO songplays (
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent
) SELECT
    TO_TIMESTAMP(e.ts / 1000),
    e.userId,
    e.level,
    s.song_id,
    s.artist_id,
    e.sessionId,
    e.location,
    e.userAgent
FROM staging_events e JOIN staging_songs s
ON e.song = s.title AND e.artist = s.artist_name
"""

user_table_insert = """
INSERT INTO users (
    user_id, first_name, last_name, gender, level
) SELECT
    -- staging_events.userId is a varchar(10), but it will be
    -- implicitly cast to an integer when inserted as users.user_id
    userId, firstName, lastName, gender, level
FROM staging_events
"""

song_table_insert = """
INSERT INTO songs (
    song_id, title, artist_id, year, duration
) SELECT
    song_id, title, artist_id, year, duration 
FROM staging_songs
"""

artist_table_insert = """
INSERT INTO artists (
    artist_id, name, location, latitude, longitude
) SELECT DISTINCT
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_longitude
FROM staging_songs
"""

time_table_insert = """
WITH temporary_start_time AS (
    SELECT DISTINCT
        TO_TIMESTAMP(ts / 1000) AS start_time
    FROM staging_events
) INSERT INTO time (
    start_time, hour, day, week, month, year, weekday
) SELECT DISTINCT
    start_time,
    EXTRACT(hour from start_time),
    EXTRACT(day from start_time),
    EXTRACT(week from start_time),
    EXTRACT(month from start_time),
    EXTRACT(year from start_time),
    EXTRACT(dow from start_time)
FROM temporary_start_time 
"""

# QUERY LISTS

create_table_queries = [
    staging_events_table_create,
    staging_songs_table_create,
    songplay_table_create,
    user_table_create,
    song_table_create,
    artist_table_create,
    time_table_create,
]
drop_table_queries = [
    staging_events_table_drop,
    staging_songs_table_drop,
    songplay_table_drop,
    user_table_drop,
    song_table_drop,
    artist_table_drop,
    time_table_drop,
]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [
    songplay_table_insert,
    user_table_insert,
    song_table_insert,
    artist_table_insert,
    time_table_insert,
]
