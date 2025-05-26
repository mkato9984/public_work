#!/usr/bin/env python
"""
文書追加と一覧表示の問題をデバッグするスクリプト
"""
import os
import sys
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# モジュールパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import RAGSystem

def main():
    print("=== 文書追加・一覧表示デバッグ ===")
    
    # RAGシステム初期化
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("GOOGLE_API_KEYが設定されていません。")
        return
    
    rag = RAGSystem(api_key)
    
    print("RAGシステムを初期化中...")
    if not rag.initialize_database():
        print("データベース初期化に失敗しました。")
        return
    
    print("✅ RAGシステム初期化完了")
    
    # 現在の文書数確認
    print("\n--- 現在の文書一覧 ---")
    documents = rag.list_all_documents()
    print(f"登録済み文書数: {len(documents)}")
    
    for i, doc in enumerate(documents, 1):
        print(f"{i}. {doc.get('title', 'タイトルなし')} (ID: {doc.get('id', 'N/A')})")
    
    # テスト文書を追加
    print("\n--- テスト文書を追加 ---")
    test_title = "デバッグテスト文書"
    test_content = "これはデバッグ用のテスト文書です。文書追加機能が正常に動作するかを確認しています。"
    test_metadata = {"category": "debug", "test": True}
    
    print(f"追加する文書: {test_title}")
    result = rag.add_document(test_title, test_content, test_metadata)
    
    if result:
        print("✅ 文書追加成功")
    else:
        print("❌ 文書追加失敗")
        return
    
    # 追加後の文書一覧確認
    print("\n--- 追加後の文書一覧 ---")
    documents_after = rag.list_all_documents()
    print(f"追加後の文書数: {len(documents_after)}")
    
    for i, doc in enumerate(documents_after, 1):
        print(f"{i}. {doc.get('title', 'タイトルなし')} (ID: {doc.get('id', 'N/A')})")
    
    # 文書数の変化を確認
    if len(documents_after) > len(documents):
        print(f"✅ 文書が正常に追加されました。追加数: {len(documents_after) - len(documents)}")
    else:
        print(f"❌ 文書数に変化がありません。追加前: {len(documents)}, 追加後: {len(documents_after)}")
    
    rag.close()

if __name__ == "__main__":
    main()
