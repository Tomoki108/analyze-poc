-- CQL init script: create keyspace and tables

CREATE KEYSPACE IF NOT EXISTS analyze_poc WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE analyze_poc;

-- 生ログ保存テーブル
CREATE TABLE IF NOT EXISTS raw_orders (
  user_id    text,
  ts         timestamp,
  order_date date,
  menu_type  text,
  PRIMARY KEY ((order_date), user_id, ts)
);

-- ユーザー嗜好テーブル
CREATE TABLE IF NOT EXISTS user_preferences (
  preferred_menu_type text,   -- 'washoku' or 'yoshoku'
  user_id            text,
  PRIMARY KEY (preferred_menu_type, user_id)
);

-- 日次サマリテーブル（各日付ごとの和食／洋食注文件数を集計）
CREATE TABLE IF NOT EXISTS daily_order_summaries (
  order_date date,
  menu_type  text,   -- 'washoku' or 'yoshoku'
  cnt        int,
  PRIMARY KEY (order_date, menu_type)
);


-- ユーザー別注文カウンタ
-- NOTE: Cassandraの制約でcounter型のカラムとそれ以外のカラムを同時に含められないので、menu_type, cntという構成にはしない
CREATE TABLE IF NOT EXISTS user_order_counts (
  user_id    text PRIMARY KEY,
  washoku_cnt counter,
  yoshoku_cnt counter
);
