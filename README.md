# Data Warehouse Project for Udacity Cloud Data Warehouses Course

This repository is my submission for the Sparkify Data
Warehouse project, which is the final part of the
Udacity Cloud Data Warehouses course.

The files for the project can be divided into two
categories:

- Some files implement preliminary creation and
  deletion of infrastructure. These files are not
  needed by the reviewer, but I have included them in
  the repository for the sake of completeness.

- The remaining files implement the tasks assigned in
  the project.

The files in each category are further explained
below.

## Infrastructure Files

The following three files govern the creation and
deletion of AWS infrastructure:

- `infrastructure.cfg`
- `infrastructure_create.py`
- `infrastructure_delete.py`

The reviewer does not need to run these python
scripts, as the relevant infrastrucure will already be
active when the project is submitted. In fact, the
reviewer **cannot** run these python scripts, as they
read data from an additional configuration file called
`access_keys.cfg`, which I have excluded from this
public repository.

### Infrastructure Configuration

The file `infrastructure.cfg` defines settings for the
project's Redshift cluster and IAM role. To minimize
cost, I have used a single-node dc2.large cluster.

Some database-related settings are also read from the
configuration file `dwh.cfg`, which is part of the
project task files described later.

### Infrastructure Creation

The file `infrastructure_create.py` uses the Boto3 SDK
to create the infrastructure needed for the project.
It first creates an IAM role and gives it read-only
access to S3. It then creates a Redshift cluster.

### Infrastructure Deletion

The file `infrastructure_delete.py` uses the Boto3 SDK
to delete the IAM role and Redshift cluster created by
`infrastructure_create.py`.

## Project Task Files

The following files actually implement the tasks
assigned in the project:

- `dwh.cfg`
- `create_tables.py`
- `etl.py`
- `sql_queries.py`

Each of these files is based on the template code
provided with the project. In fact, no significant
changes to `create_tables.py` or `etl.py` were
necessary (though I have made minor adjustments to
their formatting).

### Configuration

The file `dwh.cfg` defines various settings. These
include settings for accessing the Redshift cluster
and its associated database and the ARN for the IAM
role. They also include the paths to the raw data
sources in the appropriate S3 bucket.

### Table Creation

The file `create_tables.py` imports two lists of SQL
queries from the file `sql_queries.py`. It then uses
the psycopg2 package to connect to the database and
execute each query.

One list contains queries that create the various
tables needed for the project. The other list contains
queries that drop these same tables if they already
exist. The drop queries are executed first to ensure a
"clean slate" before executing the create queries.

The actual contents of the queries themselves are
described below in the SQL Queries section.

### Extract, Transform, Load (ETL)

The file `etl.py` imports two lists of SQL queries
from the file `sql_queries.py`. It then uses the
psycopg2 package to connect to the database and
execute each query.

One list contains queries that copy the raw data from
the S3 buckets into staging tables. The other list
contains queries that take data from these staging
tables and insert it into the appropriate fact and
dimension tables.

The actual contents of the queries themselves are
described below in the SQL Queries section.

## SQL Queries

There are four types of SQL queries in the file
`sql_queries.py`:

- drop queries, which drop the tables created by the
  create queries if they already exist
- create queries, which create the various tables
  needed for the project
- copy queries, which copy raw data from S3 buckets
  into staging tables
- insert queries, which take data from the staging
  tables and insert it into the appropriate fact and
  dimension tables

These queries are described in more detail below.

### Drop Queries

These queries simply drop each of the seven tables
created by the create queries if they already exist.

### Create Queries

These queries create two intermediate staging tables
and five final tables.
- The two staging tables are used to store the raw
  data copied from S3.
- The five final tables consist of one fact table and
  four dimension tables organized in a star schema.
  These tables make up the data warehouse, i.e., the
  end goal of the project.

Each of the seven tables is described in further
detail below.

#### Staging Table: `staging_events`

The table `staging_events` stores the data copied from
the raw log dataset. Most of its column names and
types are self-explanatory, except for those noted
below.

- Since there is no obvious choice for a primary key,
  I have added a column `event_id` that automatically
  increments via `IDENTITY(0, 1)`.
- Most of the columns are of `VARCHAR` type with
  various lengths. These lengths were chosen by
  inspecting the raw data and choosing a length
  several times greater than the longest value.
- I have specified the `length` column as `REAL`
  rather than `DECIMAL` since exact fidelity to the
  decimal representation of the song's length is not
  required.
- The `registration` column is a bit awkward to
  handle, as the raw data appears to consist of
  several digits followed by a decimal point and
  another digit, e.g., `123456789.0`. Thus, I have
  specified this column's type as `DECIMAL(20, 1)`.
  This decision is not important since this column is
  not retained in the final tables anyway.
- The `ts` column, which is an integer representation
  of a timestamp, must be specified as `BIGINT` since
  it contains values too large to be contained in an
  ordinary four-byte `INTEGER`.

#### Staging Table: `staging_songs`

The table `staging_songs` stores the data copied from
the raw song dataset. Most of its column names and
types are self-explanatory, except for those noted
below.

- Most of the columns are of `VARCHAR` type with
  various lengths. These lengths were chosen by
  inspecting the raw data and choosing a length
  several times greater than the longest value.
- I have designated the `song_id` column as the
  table's primary key.
- I have specified the `duration` column as `REAL`
  rather than `DECIMAL` since exact fidelity to the
  decimal representation of the song's duration is not
  required.
- The `artist_latitude` and `artist_longitude` columns
  can be speficied as `REAL` since the distinctions
  between N/S and E/W can be represented through a
  value's sign.

#### Fact Table: `songplays`

The table `songplays` is the fact table at the
"center" of the star schema.

- Since there is no obvious choice for a primary key,
  I have added a column `songplay_id` that
  automatically increments via `IDENTITY(0, 1)`.
- The columns `level`, `song_id`, `artist_id`,
  `location`, and `user_agent` are specified as
  `VARCHAR` of an appropriate length.
- The columns `user_id` and `session_id` are specified
  as `INTEGER`. Note that the `userId` column in the
  `staging_events` table has type `VARCHAR(10)`, so it
  will be cast to an `INTEGER` when its value is
  inserted into this column.
- The column `start_time` is specified as `TIMESTAMP`.
  A conversion will need to be performed on the `ts`
  column in the `staging_events` table to obtain this
  column's values.

I have constrained the columns `start_time`,
`user_id`, `song_id`, and `artist_id` to be `NOT NULL`
since these columns are the foreign keys that link
this fact table to the dimension tables in the star
schema.

Also, the organization of the raw data into files by
date suggests that Sparkify may take particular
interest in the temporal domain, i.e., analyzing what
songs are being played at what dates and times. Thus,
it seems reasonable to specify `start_time` as both
the `DISTKEY` and the `SORTKEY` for this table.

#### Dimension Table: `users`

The table `users` is a dimension table that can be
joined to the fact table on the column `user_id`.

All columns of this table (except for the column
`user_id`, which is an `INTEGER`) are specified as
`VARCHAR` of an appropriate length.

#### Dimension Table: `songs`

The table `songs` is a dimension table that can be
joined to the fact table on the column `song_id`.

- The columns `song_id`, `artist_id`, and `title` are
  specified as `VARCHAR` of an appropriate length.
- The column `year` is specified as `INTEGER`.
- I have specified the `duration` column as `REAL`
  rather than `DECIMAL` since exact fidelity to the
  decimal representation of the song's duration is not
  required.

Note that this table can also be joined to the table
`artists` on the column `artist_id` (although such an
operation runs somewhat contrary to the spirit of a
star schema). Accordingly, the `artist_id` column is
constrained to be `NOT NULL`.

#### Dimension Table: `artists`

The table `artists` is a dimension table that can be
joined to the fact table on the column `artist_id`.

- The `name`, `location`, and `artist_id` columns are
  specified as `VARCHAR` of an appropriate length.
- The `latitude` and `longitude` columns can be
  speficied as `REAL` since the distinctions between
  N/S and E/W can be represented through a value's
  sign.

#### Dimension Table: `time`

The table `time` is a dimension table that can be
joined to the fact table on the column `start_time`.

> It would have been more logical to name this table
> `times`, rather than `time`, to be consistent with
> the pluralized names of the other tables. However,
> the project instructions clearly demand that this
> table be named `time`.

This table contains columns representing the
`start_time` column, which is a `TIMESTAMP`, broken
down into various components. These components are
`hour`, `day`, `week`, `month`, `year`, and `weekday`,
where `weekday` is a value from `0` (Sunday) to `6`
(Saturday). These columns are all specified as
`INTEGER` and constrained to be `NOT NULL`.

### Copy Queries

These queries use the `copy` command to load the raw
data from S3 into the two staging tables. Both queries
set the `region` parameter to `us-west-2` and the
`iam_role` parameter to the IAM role ARN defined in
the file `dwh.cfg`.

- The query that copies data into the `staging_events`
  table sets the data source as the log data defined
  in the file `dwh.cfg`. It also sets the `json`
  parameter to the JSONPath defined in `dwh.cfg`.
- The query that copies data into the `staging_songs`
  table sets the data source as the song data defined
  in the file `dwh.cfg`. It also sets the `json`
  parameter to `'auto'`.

### Insert Queries

These queries insert the data into the final tables
using the `INSERT INTO ... SELECT ...` syntax.

#### Insert Query: `songplays`

This query inserts data into the `songplays` fact
table that is taken from the two staging tables, which
must be joined on the song title and artist name.

The `ts` column of the `staging_events` table must be
converted before it can be inserted as the value of
`start_time`. Since `ts` is measured in milliseconds
since the epoch, it must first be divided by 1000, and
the resulting number of seconds is added to the epoch
to obtain the final result.

This query also includes a `WHERE` clause to exclude
events with a missing (null) song value.

#### Insert Query: `users`

This query inserts data into the `users` dimension
table that is taken from the `staging_events` table.
It uses `SELECT DISTINCT` to ensure that each user is
represented only once.

The `userId` column of `staging_events` has type
`VARCHAR(10)`, so it must be cast to an `INTEGER` when
inserted as `user_id` in `users`.

This query also includes a `WHERE` clause to exclude
events with a missing (null) song value.

#### Insert Query: `songs`

This query inserts data into the `songs` dimension
table that is taken from the `staging_songs` table.

#### Insert Query: `artists`

This query inserts data into the `artists` dimension
table that is taken from the `staging_songs` table. It
uses `SELECT DISTINCT` to ensure that each artist is
represented only once.

Artists may have multiple songs in the `staging_songs`
table, so this query uses `SELECT DISTINCT`.

#### Insert Query: `time`

This query inserts data into the `time` dimension
table that is taken from the `staging_events` table.
It uses `SELECT DISTINCT` to ensure that each time is
represented only once.

To do so, it first creates a temporary table named
`temporary_start_time`. This table simply selects all
distinct values of the appropriately converted
timestamps from the `staging_events` table. This lone
column in the temporary table is named `start_time`.

The main part of the query then inserts values into
the `time` table that are taken from `start_time` in
the temporary table. Specifically, `start_time` itself
is inserted, as are each of the six time components
defined in the `time` table. Each component is
calculated from `start_time` using the `EXTRACT`
function, e.g., `EXTRACT(HOUR FROM start_time)`.
