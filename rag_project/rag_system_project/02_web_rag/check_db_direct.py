#!/usr/bin/env python
"""
PostgreSQLのテーブル内容を直接確認するスクリプト
"""
import os
import psycopg2
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def check_database():
    print("=== PostgreSQL直接確認 ===")
    
    # データベース接続情報
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'rag_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'test1234'),
        'port': int(os.getenv('DB_PORT', '5432'))
    }
    
    print(f"接続情報: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        # データベースに接続
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # テーブル存在確認
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'documents'
        """)
        
        tables = cursor.fetchall()
        print(f"documentsテーブル存在確認: {len(tables) > 0}")
        
        if len(tables) > 0:
            # テーブル構造確認
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'documents'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\nテーブル構造:")
            for col in columns:
                print(f"  {col[0]} ({col[1]}) - NULL可: {col[2]}")
            
            # 全レコード数確認
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_count = cursor.fetchone()[0]
            print(f"\n全レコード数: {total_count}")
            
            # 実際のレコード内容確認
            if total_count > 0:
                cursor.execute("SELECT id, title, content, created_at FROM documents ORDER BY created_at DESC LIMIT 5")
                records = cursor.fetchall()
                
                print("\n最新5件のレコード:")
                for record in records:
                    print(f"  ID: {record[0]}, タイトル: {record[1]}, 本文長: {len(record[2])}, 作成日時: {record[3]}")
        else:
            print("documentsテーブルが存在しません")
        
        cursor.close()
        conn.close()
        print("✅ データベース接続を閉じました")
        
    except Exception as e:
        print(f"❌ データベース確認中にエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
