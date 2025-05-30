# analyze-poc

## 目的

LINE ミニアプリから送信される注文ログをもとに、ユーザーセグメントを抽出・可視化する POC を週末 2 日間で構築。

### 習得したいスタック

- kafka による非同期処理
- cassandra によるデータ管理
- python によるバッチ集計処理

## ユースケース

- 注文ログをもとに、各ユーザーの嗜好（和食派/洋食派）をリアルタイム更新。それぞれに該当するユーザー ID をリスト表示できる。
- 和食の注文数、洋食の注文数について、日毎のデータを翌日に集計。
- 和食の注文数、洋食の注文数について、通算の割合を常に集計。

### 活用方法

- 洋食と和食のどちらが好まれているのか、そのトレンドを把握する
- ユーザーの嗜好に基づいたマーケティング施策の検討(嗜好に応じた適切なクーポンの配布)

## アーキテクチャ概要

```text
[ミニアプリ（ログ送信テストスクリプト）]
    ↓ POST /api/log { user_id, timestamp, menu_type }

[Log-Ingest Service]
    ↓ Kafka “order-logs” トピックへプロデュース

[Log-Consumer Service]
    ↓ Cassandra raw_orders に書き込み、user_cuisine_counts、cuisine_segment_counts をインクリメント

[バッチ集計 (CronJob)]
    ↓ 前日のraw_orders を集計
    • daily_cuisine_summary に書き込み

[Summary Service]
    • GET /api/segments
    {
        cuisines: [
            { segment: "washoku", count: 123, users: [u1, u2, ...] },
            { segment: "yoshoku", count: 87, users: [u3, u4, ...] }
        ]
    }
    • GET /api/summaries
    {
        summaries: [
            { date: "2025-05-30", segments: "washoku", total_count: 456 },
            { date: "2025-05-30", segment: "yoshoku", total_count: 321 }
        ]
    }
[Web UI (Vue.js or 静的HTML + Chart.js)]
    • /cuisine.html：和食／洋食注文円グラフ（トータル/日毎）。各セグメントに該当するユーザー ID リストも表示
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

-- ユーザー別カウンタ（嗜好変化をインクリメンタルに保持）
CREATE TABLE user_cuisine_counts (
  user_id      text PRIMARY KEY,
  washoku_cnt  counter,
  yoshoku_cnt  counter
);

-- セグメント全体カウンタ（現在の「和食派／洋食派」人数を即時取得）
CREATE TABLE cuisine_segment_counts (
  segment text PRIMARY KEY,   -- 'washoku' or 'yoshoku'
  cnt     counter
);

-- 日次サマリテーブル（各日付ごとの和食／洋食注文件数を集計）
CREATE TABLE daily_cuisine_summary (
  order_date  date,
  segment     text,   -- 'washoku' or 'yoshoku'
  cnt       int,
  PRIMARY KEY (order_date, segment)
);
```

## 開発手順

- Cassandra のスキーマを作成し、テーブルを準備
- Cassandra、Kafka、Zookeeper、Log-Ingest Service のコンテナを定義
- **Log-Ingest Service （Go, Echo）** を実装
  - ログの送信を受け付け、Kafka トピックへログを送信（プロデュース）する
- **Log-Consumer Service （Go, Echo）** を実装
  - Kafka トピックからログを消費し、Cassandra の raw_orders に書き込み、user_cuisine_counts、cuisine_segment_counts をインクリメントする
- **Log-Aggregator Service を実装（Python）**
  - 前日のログを集計し、daily_cuisine_summary テーブルを更新する。
- **Summary-API Service （Go, Echo）** を実装
  - 和食派／洋食派のユーザー ID リストを取得する API を実装
  - トータルの和食派／洋食派の人数を取得する API を実装
  - 日毎の和食／洋食注文数を取得する API を実装
- **Summary-Web Service (Vue.js or 静的 HTML + Chart.js)** を実装
  - 和食派／洋食派のユーザー ID リストを表示
  - トータルの和食注文数／洋食注文数を円グラフで表示
  - 日毎の和食注文数／洋食注文数を円グラフで表示
- 実際のログストリームを再現するテストスクリプトを作成

## 動作確認

- コンテナ起動 (Zookeeper/Kafka/Cassandra/Log-Ingest):
  ```bash
  docker-compose up -d zookeeper kafka cassandra log-ingest
  ```

````

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
      --topic order-logs --from-beginning --max-messages 1
  ```
- Web UI への反映: Summary Service 経由で取得し、グラフ表示を確認
````
