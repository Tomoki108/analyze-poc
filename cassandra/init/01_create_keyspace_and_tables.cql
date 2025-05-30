-- CQL init script: create keyspace and tables

CREATE KEYSPACE IF NOT EXISTS analyze_poc WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE analyze_poc;

-- 生ログ保存テーブル
CREATE TABLE IF NOT EXISTS raw_orders (
  user_id   text,
  ts        timestamp,
  menu_type text,
  PRIMARY KEY (user_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

-- ユーザー別カウンタ（嗜好変化をインクリメンタルに保持）
CREATE TABLE IF NOT EXISTS user_cuisine_counts (
  user_id      text PRIMARY KEY,
  washoku_cnt  counter,
  yoshoku_cnt  counter
);

-- セグメント全体カウンタ（現在の「和食派／洋食派」人数を即時取得）
CREATE TABLE IF NOT EXISTS cuisine_segment_counts (
  segment text PRIMARY KEY,
  cnt     counter
);

-- 日次サマリテーブル（各日付ごとの和食／洋食注文件数を集計）
CREATE TABLE IF NOT EXISTS daily_cuisine_summary (
  order_date date,
  segment    text,
  cnt        int,
  PRIMARY KEY (order_date, segment)
);
