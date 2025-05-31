import os
from datetime import datetime, timedelta
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Cassandra接続設定
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT', '9042')
CASSANDRA_USER = os.getenv('CASSANDRA_USER', 'cassandra')
CASSANDRA_PASS = os.getenv('CASSANDRA_PASS', 'cassandra')
KEYSPACE = 'analyze_poc'

if __name__ == '__main__':
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    aggregate_orders(date_arg)

# Entry point for the aggregation service
def aggregate_orders(date_str=None):
    session = get_cassandra_session()
    
    # 日付が指定されていない場合は前日の日付を使う
    if date_str is None:
        yesterday = datetime.utcnow() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    else:
        # 日付フォーマットを検証
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD")
            return
    
    # 日次サマリ更新
    update_daily_summaries(session, date)
    
    # ユーザー嗜好更新
    update_user_preferences(session)
    
    print(f"Aggregated data for {date_str}")

# Cassandraセッションを取得するヘルパー関数
def get_cassandra_session():
    auth_provider = PlainTextAuthProvider(
        username=CASSANDRA_USER,
        password=CASSANDRA_PASS
    )
    cluster = Cluster(
        [CASSANDRA_HOST],
        port=int(CASSANDRA_PORT),
        auth_provider=auth_provider
    )
    return cluster.connect(KEYSPACE)

# 日次サマリを更新する関数
def update_daily_summaries(session, date):
    # 日付指定でraw_ordersから集計
    rows = session.execute(
        "SELECT order_date, menu_type, COUNT(*) as cnt "
        "FROM raw_orders WHERE order_date = %s "
        "GROUP BY order_date, menu_type",
        [date]
    )
    
    # daily_order_summariesに挿入/更新
    for row in rows:
        session.execute(
            "INSERT INTO daily_order_summaries (order_date, menu_type, cnt) "
            "VALUES (%s, %s, %s)",
            [row.order_date, row.menu_type, row.cnt]
        )

# ユーザー嗜好を更新する関数
def update_user_preferences(session):
    # ユーザーごとの注文件数を取得
    user_counts = {}
    rows = session.execute(
        "SELECT user_id, menu_type, COUNT(*) as cnt "
        "FROM raw_orders "
        "GROUP BY user_id, menu_type"
    )
    
    # ユーザーごとに集計
    for row in rows:
        if row.user_id not in user_counts:
            user_counts[row.user_id] = {'washoku': 0, 'yoshoku': 0}
        user_counts[row.user_id][row.menu_type] = row.cnt
    
    # 嗜好データを更新
    for user_id, counts in user_counts.items():
        new_pref = 'washoku' if counts['washoku'] > counts['yoshoku'] else 'yoshoku'
        
        # 現在の嗜好を取得
        current_pref = session.execute(
            "SELECT preferred_menu_type FROM user_preferences WHERE user_id = %s LIMIT 1",
            [user_id]
        ).one()
        
        if current_pref:
            if current_pref.preferred_menu_type != new_pref:
                # 嗜好が変更された場合のみ更新
                session.execute(
                    "DELETE FROM user_preferences "
                    "WHERE preferred_menu_type = %s AND user_id = %s",
                    [current_pref.preferred_menu_type, user_id]
                )
                session.execute(
                    "INSERT INTO user_preferences (preferred_menu_type, user_id) "
                    "VALUES (%s, %s)",
                    [new_pref, user_id]
                )
        else:
            # 新規登録
            session.execute(
                "INSERT INTO user_preferences (preferred_menu_type, user_id) "
                "VALUES (%s, %s)",
                [new_pref, user_id]
            )



