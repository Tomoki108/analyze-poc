# 学んだこと

## Cassandra

- 分散型の NoSQL データベースで、スケーラビリティと可用性に優れる。
- Read より Write のパフォーマンスが高い。
- **パーティションキー（どのノードにデータを保存するかを決定）** と **クラスタリングキー（パーティション内でのデータの順序）** を使用してデータを構造化。どちらも複合キーが可能で、合わせて一意になれば良い。
- パーティションキーとクラスタリングキーによって、クエリに制約が生まれる。パーティションキーで絞り込むことは必須で、クラスタリングキーはオプション。
  - **クエリファーストでスキーマ設計する必要がある**。クエリへの柔軟性やパフォーマンス、データ量などのトレードオフを考慮した設計が難しい。
- counter 型のカラムを使用して、効率の良いインクリメント操作が可能。結果整合性を持つ。

## Kafka

高スループットかつ分散型のストリーミングプラットフォーム

### Kafka ブローカーとは

- Kafka クラスターを構成するサーバー（ノード）
- メッセージの受信・保存・配信を担当

#### 主な役割

- **データ保持**
  - トピックのパーティションをディスクに永続化
- **プロデューサーとの通信**
  - メッセージを受信し、対応するパーティションに書き込み
- **コンシューマーとの通信**
  - オフセットに応じたメッセージを返却
- **レプリケーション管理**
  - リーダー・フォロワー間で同期を実行し、高可用性を確保
- **リーダー選出**
  - Controller（ZooKeeper または KRaft）と協調して、各パーティションのリーダーを決定
