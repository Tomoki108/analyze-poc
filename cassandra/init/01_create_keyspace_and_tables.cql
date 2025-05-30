-- CQL init script: create keyspace and tables

CREATE KEYSPACE IF NOT EXISTS analyze_poc WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE analyze_poc;

CREATE TABLE IF NOT EXISTS raw_visits (
  user_id    text,
  ts         timestamp,
  menu_type  text,
  PRIMARY KEY (user_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

CREATE TABLE IF NOT EXISTS cuisine_segments (
  period     text,
  segment    text,
  count      int,
  PRIMARY KEY (period, segment)
);

CREATE TABLE IF NOT EXISTS freq_segments (
  period     text,
  segment    text,
  count      int,
  PRIMARY KEY (period, segment)
);
