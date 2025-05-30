# analyze-poc

## 目的

LINE ミニアプリから送信される来店／注文ログをもとに、2 つのユーザーセグメントを抽出・可視化する POC を週末 2 日間で構築します。具体的には：

- **和食好みセグメント** と **洋食好みセグメント** を抽出し、円グラフで割合を表示
- **来店頻度セグメント**（月 1 回未満 / 月 1 ～ 3 回 / 週 1 回以上）を抽出し、円グラフで割合を表示

## ユースケース

1. **和食／洋食嗜好の把握**

   - 一定期間内の注文データを集計し、和食メニューを主に注文するユーザー数と洋食メニューを主に注文するユーザー数を算出。
   - ダッシュボード上の円グラフで、各セグメントの割合を直感的に把握。

2. **来店頻度の分類**

   - 一定期間内の来店回数に基づき、ユーザーを 3 つの頻度セグメントに分類：

     - 月 1 回未満（0 ～ 1 回）
     - 月 1 ～ 3 回（2 ～ 3 回）
     - 週 1 回以上（4 回以上）

   - ダッシュボード上の円グラフで、各頻度セグメントの割合を可視化。

3. **セグメント重ね合わせ配信**（発展）

   - 例えば「月 1 ～ 3 回来店」かつ「和食好み」のユーザーを特定し、LINE 配信 API へ連携。
   - ユーザー属性テーブルを用意し、複数条件を AND で絞り込み、配信対象を生成。

## アーキテクチャ概要

```text
[ミニアプリ]
    ↓ POST /api/log { user_id, timestamp, menu_type }
[Log-Ingest Service]
    ↓ Kafka “visit-logs” トピックへプロデュース
[Log-Consumer Service]
    ↓ Cassandra raw_visits テーブル に書き込み

[バッチ集計 (CronJob)]
    ↓ raw_visits を集計
    • cuisine_segments テーブル (washoku/yoshoku のカウント)
    • freq_segments テーブル (月1未満/月1～3/週1以上 のカウント)

[Summary Service]
    • GET /api/segments/cuisine → { washoku: 123, yoshoku: 87 }
    • GET /api/segments/frequency → { monthly0: 45, monthly1: 80, weekly1: 85 }

[Web UI (静的HTML + Chart.js)]
    • /cuisine.html：和食／洋食円グラフ
    • /frequency.html：来店頻度円グラフ
```

## データモデル例 (Cassandra)

```cql
CREATE TABLE raw_visits (
  user_id    text,
  ts         timestamp,
  menu_type  text,
  PRIMARY KEY (user_id, ts)
);

CREATE TABLE cuisine_segments (
  period     text,
  segment    text,
  count      int,
  PRIMARY KEY (period, segment)
);

CREATE TABLE freq_segments (
  period     text,
  segment    text,
  count      int,
  PRIMARY KEY (period, segment)
);
```

## 開発手順（次のアクション）

1. **CronJob バッチ雛形の実装**：raw_visits から cuisine_segments, freq_segments へアップサートするスクリプトを作成
2. **Summary Service の API 実装**：各セグメント用エンドポイントを追加
3. **Web UI テンプレート作成**：Chart.js で 2 つの円グラフを描画
4. **Kubernetes マニフェスト作成**：Deployment, Service, CronJob, Ingress などを整理
5. **動作確認**：curl/postman でログ投入 →UI 表示まで一連フローを検証

---

週末 POC としてシンプルかつ動作確認が速い構成です。上記をもとに 1 つずつ実装し、README に進捗をコミットしてください。
