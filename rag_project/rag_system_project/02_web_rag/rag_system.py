import json
import os
import numpy as np
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
from db_utils import DatabaseManager
from config import Config

# .envファイルから環境変数を読み込み
load_dotenv()

class RAGSystem:
    """RAG (Retrieval-Augmented Generation) システムクラス"""
    def __init__(self, google_api_key: str = None):
        """RAGシステムを初期化します"""
        self.google_api_key = google_api_key or Config.GOOGLE_API_KEY
        if not self.google_api_key:
            raise ValueError("Google API キーが設定されていません。")
        
        genai.configure(api_key=self.google_api_key)
        self.db = DatabaseManager()
        self.embedding_model = Config.EMBEDDING_MODEL
        
        # 生成AIモデルの設定
        self.generation_config = Config.GENERATION_CONFIG
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=self.generation_config
        )
        
    def initialize_database(self):
        """データベースを初期化します"""
        try:
            print("データベース接続を試みています...")
            connection = self.db.connect()
            if connection:
                print("データベース接続に成功しました")
                print("documentsテーブルの作成を試みています...")
                result = self.db.create_documents_table()
                if result:
                    print("documentsテーブルの作成に成功しました")
                else:
                    print("documentsテーブルの作成に失敗しました")
                return result
            else:
                print("データベース接続に失敗しました")
                return False
        except Exception as e:
            print(f"データベース初期化中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """テキストの埋め込みベクトルを生成します"""
        try:
            print(f"埋め込みを生成中... テキスト長: {len(text)}")
            embedding = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            result = embedding["embedding"]
            print(f"埋め込み生成成功: ベクトル長 {len(result)}")
            return result
        except Exception as e:
            print(f"埋め込み生成中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            # テスト用にダミーベクトルを返す
            dummy_vector = [0.0] * 768
            print(f"ダミーベクトルを返します。長さ: {len(dummy_vector)}")
            return dummy_vector
    
    def add_document(self, title: str, content: str, metadata: Dict[str, Any] = None):
        """文書をRAGシステムに追加します"""
        if not self.db.connection:
            print("データベースに接続されていません。")
            return False
        
        # テキストの埋め込みを生成
        try:
            print(f"文書 '{title}' の埋め込みを生成中...")
            embedding = self.generate_embedding(content)
            if not embedding or len(embedding) == 0:
                print("埋め込みの生成に失敗しました。空のベクトルが返されました。")
                return False
            
            print(f"埋め込み生成完了: ベクトル長 {len(embedding)}")
            
            # データベースに保存
            return self.db.insert_document(title, content, embedding, metadata)
        except Exception as e:
            print(f"文書追加処理中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """コサイン類似度を計算します"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_a = np.linalg.norm(vec1)
            norm_b = np.linalg.norm(vec2)
            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0
    
    def search_similar_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """クエリに類似した文書を検索します"""
        if not self.db.connection:
            print("データベースに接続されていません。")
            return []
        
        # クエリの埋め込みを生成
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        # pgvectorが利用可能な場合は、データベースレベルで類似度検索
        if self.db.has_pgvector:
            return self.db.search_documents(query_embedding=query_embedding, limit=top_k)
        
        # pgvectorが利用できない場合は、Pythonで類似度計算
        documents = self.db.get_all_documents()
        results = []
        
        for doc in documents:
            # 埋め込みデータの処理
            embedding_data = doc["embedding"]
            if isinstance(embedding_data, str):
                doc_embedding = json.loads(embedding_data)
            else:
                doc_embedding = embedding_data
            
            # 類似度計算
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            doc["similarity"] = similarity
            results.append(doc)
        
        # 類似度でソート
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return results[:top_k]
    
    def answer_question(self, question: str, max_context_length: int = 2000) -> str:
        """質問に対して回答を生成します"""
        # 関連する文書を検索
        relevant_docs = self.search_similar_documents(question, top_k=3)
        
        if not relevant_docs:
            return "関連する文書が見つかりませんでした。"
        
        # コンテキストを作成（最大長を制限）
        context_parts = []
        total_length = 0
        
        for doc in relevant_docs:
            doc_text = f"Document: {doc['title']}\nContent: {doc['content']}\n"
            if total_length + len(doc_text) > max_context_length:
                break
            context_parts.append(doc_text)
            total_length += len(doc_text)
        
        context = "\n".join(context_parts)
        
        # プロンプト作成
        prompt = f"""以下のコンテキストに基づいて、質問に回答してください。
コンテキストに含まれていない情報については、「その情報はコンテキストにありません」と答えてください。
回答は簡潔で分かりやすくしてください。

コンテキスト:
{context}

質問: {question}

回答:"""
        
        try:
            # 回答を生成
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
    
    def get_document_count(self) -> int:
        """データベース内の文書数を取得します"""
        documents = self.db.get_all_documents()
        return len(documents)
    
    def list_all_documents(self) -> List[Dict]:
        """すべての文書のリストを取得します"""
        return self.db.get_all_documents()
    
    def close(self):
        """RAGシステムを終了します"""
        if self.db:
            self.db.disconnect()
