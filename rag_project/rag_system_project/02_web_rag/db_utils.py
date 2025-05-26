import psycopg2
import json
import os
from typing import List, Dict, Any, Optional
from psycopg2.extras import execute_values
from config import Config

# PostgreSQL データベースへの接続情報を設定します。
# config.pyまたは環境変数で設定してください
DB_HOST = Config.DB_HOST
DB_NAME = Config.DB_NAME
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD

class DatabaseManager:
    """RAGシステム用のデータベース管理クラス"""
    
    def __init__(self, host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """データベースに接続します"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            print("PostgreSQL への接続に成功しました。")
              # pgvector 拡張機能があるかチェックして登録を試みます
            try:
                from pgvector.psycopg2 import register_vector
                register_vector(self.connection)
                print("pgvector 拡張機能が登録されました。")
                self.has_pgvector = True
            except (ImportError, Exception) as e:
                print(f"pgvectorエラー: {e}")
                print("pgvectorが利用できません。JSONBを使用してベクトルを保存します。")
                self.has_pgvector = False
            
            return self.connection
        except psycopg2.Error as e:
            print(f"PostgreSQL への接続中にエラーが発生しました: {e}")
            return None
    
    def disconnect(self):
        """データベース接続を閉じます"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("PostgreSQL との接続を閉じました。")
    
    def create_documents_table(self):
        """文書保存用のテーブルを作成します"""
        if not self.connection:
            print("データベースに接続されていません。")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            if self.has_pgvector:
                # pgvectorを使用する場合
                cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
                """)
                
                cursor.execute("""
                DROP TABLE IF EXISTS documents;
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(768),  -- Gemini embedding dimensions
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
            else:
                # JSONBを使用する場合
                cursor.execute("""
                DROP TABLE IF EXISTS documents;
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding JSONB,  -- ベクトル埋め込みをJSONBとして保存
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)            # インデックスを作成（検索性能向上のため）
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
            CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING GIN(metadata);
            """)
            
            self.connection.commit()
            cursor.close()
            print("documentsテーブルが正常に作成されました。")
            return True
        except psycopg2.Error as e:
            print(f"テーブル作成中にエラーが発生しました: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def insert_document(self, title: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """文書をデータベースに挿入します"""
        if not self.connection:
            print("データベースに接続されていません。")
            return False
        
        try:
            cursor = self.connection.cursor()
            metadata = metadata or {}
            
            print(f"文書 '{title}' を追加します。ベクトルの長さ: {len(embedding) if embedding else 0}")
            
            if self.has_pgvector:
                cursor.execute("""
                INSERT INTO documents (title, content, embedding, metadata)
                VALUES (%s, %s, %s, %s::jsonb)
                """, (title, content, embedding, json.dumps(metadata)))
            else:
                # JSONBとして埋め込みベクトルを保存
                cursor.execute("""
                INSERT INTO documents (title, content, embedding, metadata)
                VALUES (%s, %s, %s::jsonb, %s::jsonb)
                """, (title, content, json.dumps(embedding), json.dumps(metadata)))
            
            self.connection.commit()
            cursor.close()
            print(f"文書 '{title}' をデータベースに追加しました。")
            return True
            
        except psycopg2.Error as e:
            print(f"文書挿入中にエラーが発生しました: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def search_documents(self, query_embedding: List[float] = None, title_filter: str = None, 
                        metadata_filter: Dict[str, Any] = None, limit: int = 10):
        """文書を検索します"""
        if not self.connection:
            print("データベースに接続されていません。")
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # 基本のSELECT文
            query = "SELECT id, title, content, embedding, metadata, created_at FROM documents"
            conditions = []
            params = []
            
            # フィルター条件を構築
            if title_filter:
                conditions.append("title ILIKE %s")
                params.append(f"%{title_filter}%")
            
            if metadata_filter:
                for key, value in metadata_filter.items():
                    conditions.append("metadata->>%s = %s")
                    params.extend([key, str(value)])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # pgvectorを使用できる場合は類似度検索も追加
            if query_embedding and self.has_pgvector:
                if conditions:
                    query += f" ORDER BY embedding <-> %s LIMIT %s"
                else:
                    query += f" ORDER BY embedding <-> %s LIMIT %s"
                params.extend([query_embedding, limit])
            else:
                query += f" ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            # 結果を辞書形式で返す
            documents = []
            for row in results:
                doc = {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "embedding": row[3],
                    "metadata": row[4],
                    "created_at": row[5]
                }
                documents.append(doc)
            
            return documents
            
        except psycopg2.Error as e:
            print(f"文書検索中にエラーが発生しました: {e}")
            return []
    
    def get_all_documents(self):
        """すべての文書を取得します"""
        return self.search_documents(limit=1000)
    
    def delete_document(self, document_id: int):
        """指定されたIDの文書を削除します"""
        if not self.connection:
            print("データベースに接続されていません。")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            
            if cursor.rowcount > 0:
                self.connection.commit()
                print(f"文書 ID {document_id} を削除しました。")
                result = True
            else:
                print(f"文書 ID {document_id} が見つかりませんでした。")
                result = False
            
            cursor.close()
            return result
            
        except psycopg2.Error as e:
            print(f"文書削除中にエラーが発生しました: {e}")
            if self.connection:
                self.connection.rollback()
            return False

# 使用例とテスト関数
def test_database_operations():
    """データベース操作のテスト"""
    db = DatabaseManager()
    
    # 接続
    if db.connect():
        # テーブル作成
        db.create_documents_table()
        
        # サンプルデータ挿入
        sample_embedding = [0.1] * 768  # サンプルの768次元ベクトル
        db.insert_document(
            title="テスト文書1",
            content="これはテスト用の文書です。",
            embedding=sample_embedding,
            metadata={"category": "test", "author": "system"}
        )
        
        # 文書検索
        documents = db.get_all_documents()
        print(f"データベースに {len(documents)} 件の文書があります。")
        
        # 接続終了
        db.disconnect()

if __name__ == "__main__":
    test_database_operations()
