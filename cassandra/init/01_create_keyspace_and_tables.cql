-- CQL init script: create keyspace and tables

CREATE KEYSPACE IF NOT EXISTS analyze_poc WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE analyze_poc;

-- 生ログ保存テーブル（日付ベースのパーティションキーを追加）
CREATE TABLE IF NOT EXISTS raw_orders (
  user_id    text,
  ts         timestamp,
  order_date date,  -- 日付ベースのパーティションキー
  menu_type  text,
  PRIMARY KEY ((user_id, order_date), ts)
) WITH CLUSTERING ORDER BY (ts DESC);

-- 日付のみのインデックス（日付範囲クエリ用）
CREATE INDEX IF NOT EXISTS idx_raw_orders_date ON raw_orders (order_date);

-- ユーザー嗜好テーブル（各ユーザーの好みを保持）
CREATE TABLE IF NOT EXISTS user_cuisine_counts (
  prefered_menu_type text,   -- 'washoku' or 'yoshoku'
  user_id            text,
  PRIMARY KEY (prefered_menu_type, user_id)
);

-- 日次サマリテーブル（各日付ごとの和食／洋食注文件数を集計）
CREATE TABLE IF NOT EXISTS daily_order_summaries (
  order_date date,
  menu_type  text,   -- 'washoku' or 'yoshoku'
  cnt        int,
  PRIMARY KEY (order_date, menu_type)
);

-- ユーザー別注文カウンタ
CREATE TABLE IF NOT EXISTS user_order_counts (
  user_id    text PRIMARY KEY,
  menu_type  text,  -- 'washoku' or 'yoshoku'
  cnt        counter
);
