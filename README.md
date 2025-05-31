# analyze-poc

## 目的

LINE ミニアプリから送信される注文ログをもとに、ユーザーセグメントを抽出・可視化する POC を週末 2 日間で構築。

### 習得したいスタック

- kafka による非同期処理
- cassandra によるデータ管理
- python によるバッチ集計処理

## ユースケース

- 和食の注文数、洋食の注文数について日毎のデータを閲覧できる。（前日のログを集計）
- 注文ログをもとに、各ユーザーの嗜好（和食派/洋食派）を判定。それぞれの数、該当するユーザー ID をリスト表示できる。（前日のログを元に毎晩差分更新）

### 活用方法

- 洋食と和食のどちらが好まれているのか、そのトレンドを把握する
- ユーザーの嗜好に基づいたマーケティング施策の検討(嗜好に応じた適切なクーポンの配布)

## アーキテクチャ概要

```text
[log-stream-test.sh]
    ↓ loop: POST /api/log { user_id, timestamp, menu_type }

[services/log-ingest (Go, Echo)]
    ↓ Kafka “order-logs” トピックへプロデュース

[services/log-consumer (Go)]
    ↓ Cassandra raw_orders に書き込み、user_order_counts をインクリメント

[services/aggregator]
    ↓ 前日のraw_orders を集計、daily_order_summaries に書き込み
    ↓ 前日のraw_orders を集計、注文があったユーザーのuser_preferences を更新

[services/summary-api (Go, Echo)]
    • GET /api/daily_order_summaries?year_month=2025-05
    {
        summaries: [
            {
                date: "2025-05-30",
                counts: [
                    { menu_type: "washoku", count: 456 },
                    { menu_type: "yoshoku", count: 321 }
                ]
            },
            ...
        ]
    }
    • GET /api/user_segments
    {
        segments: [
            { menu_type: "washoku", count: 123, user_ids: [u1, u2, ...] },
            { menu_type: "yoshoku", count: 87, user_ids: [u3, u4, ...] }
        ]
    }
[services/summary-web (Vue.js 3, Chart.js)]
    • /daily_order_summaries.html
        日毎の和食／洋食注文数を円グラフで表示。セレクトボックスで年月を選択可能。
    • /user_segments.html
        和食派／洋食派のユーザー ID リストを表示。セレクトボックスで「和食派」「洋食派」を選択可能。
```

### [More] スケーリングリスク

- Cassandra のカウンタは分散カウンタとして実装されているものの、同一パーティション（user_id や segment）への高頻度アクセスが集中するとホットパーティションが発生し、書き込みスループット低下やタイムアウトの原因となる可能性がある
- カウンタは最終的整合性 (eventual consistency) モデルを採用しており、短時間での読み取り時に一時的に不整合な値が返る場合がある。

本番環境で高負荷を想定する場合は、以下のようなストリーム処理エンジンの導入を検討。

- Kafka Streams / ksqlDB
- Apache Flink など
- カウンタパーティションを分散化するパーティションキー設計の見直し

## データモデル (Cassandra)

```cql
-- 生ログ保存テーブル
CREATE TABLE raw_orders (
  user_id   text,
  ts        timestamp,
  menu_type text,
  PRIMARY KEY (user_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

-- ユーザー別注文カウンタ
CREATE TABLE user_order_counts (
  user_id      text PRIMARY KEY,
  menu_type  string, -- 'washoku' or 'yoshoku'
  cnt  counter
);

-- 日次サマリテーブル（各日付ごとの和食／洋食注文件数を集計）
CREATE TABLE daily_order_summaries (
  order_date  date,
  menu_type     text,   -- 'washoku' or 'yoshoku'
  cnt       int,
  PRIMARY KEY (order_date, menu_type)
);

-- ユーザー嗜好テーブル
CREATE TABLE user_preferences (
  prefered_menu_type     text,   -- 'washoku' or 'yoshoku'
  user_id     text,
  PRIMARY KEY (prefered_menu_type, user_id)
);
```

## 動作確認

- コンテナ起動 (Zookeeper/Kafka/Cassandra/Log-Ingest):
  ```bash
  docker-compose up -d zookeeper kafka cassandra log-ingest
  ```
- Kafka トピック作成：
  ```bash
  make create-topics
  ```
- Log-Ingest 起動ログ確認：
  ```bash
  docker-compose logs -f log-ingest
  ```
- ログ投入テスト：
  ```bash
  curl -X POST http://localhost:8080/api/log \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"u1","timestamp":"2025-05-30T12:00:00Z","menu_type":"washoku"}'
  ```
- Kafka に書き込まれたことを確認：
  ```bash
  docker-compose exec kafka \
    kafka-console-consumer --bootstrap-server kafka:9092 \
      --topic order-logs --from-beginning --max-messages 10
  ```
- Web UI への反映: Summary Service 経由で取得し、グラフ表示を確認
