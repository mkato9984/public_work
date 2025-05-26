#!/usr/bin/env python
# filepath: c:\public_work\rag_project\web_app.py
"""
RAGシステムのWebインターフェース
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, abort, send_from_directory
import rag_system
from config import Config

# .envファイルから環境変数を読み込み
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# RAGシステムのインスタンスを作成
rag = None

def initialize_rag():
    """RAGシステムを初期化"""
    global rag
    if rag is None:
        # APIキーの設定
        api_key = Config.GOOGLE_API_KEY        app.logger.info(f"APIキー設定状態: {'設定されています' if api_key else '設定されていません'}")
        
        if not api_key:
            app.logger.error("APIキーが設定されていません。環境変数GOOGLE_API_KEYを設定してください。")
            return False
        
        try:
            app.logger.info(f"RAGシステムを初期化します。APIキー: {api_key[:4]}...{api_key[-4:]}")
            rag = rag_system.RAGSystem(api_key)
            app.logger.info("RAGインスタンスを作成しました")
            
            app.logger.info("データベースに接続しています...")
            success = rag.initialize_database()
            if success:
                app.logger.info("RAGシステムが正常に初期化されました")
                return True
            else:
                app.logger.error("RAGシステムの初期化に失敗しました（データベース初期化エラー）")
                return False
        except Exception as e:
            app.logger.error(f"RAGシステムの初期化中にエラーが発生しました: {e}")
            return False

@app.before_request
def before_request():
    """リクエスト前の処理"""
    global rag
    if rag is None:
        initialize_rag()

@app.teardown_appcontext
def teardown_db(exception):
    """アプリケーション終了時の処理"""
    global rag
    if rag:
        rag.close()
        rag = None

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """質問応答API"""
    if not rag:
        if not initialize_rag():
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
    
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({
            'success': False,
            'error': '質問が指定されていません'
        }), 400
    
    try:
        answer = rag.answer_question(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        app.logger.error(f"回答生成中にエラーが発生しました: {e}")
        return jsonify({
            'success': False,
            'error': f'回答生成中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """文書一覧を取得"""
    if not rag:
        if not initialize_rag():
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
    
    try:
        documents = rag.list_all_documents()
        
        # 埋め込みベクトルを除外（レスポンスサイズを小さくするため）
        for doc in documents:
            doc.pop('embedding', None)
            # 日時オブジェクトをJSON対応形式に変換
            if 'created_at' in doc and isinstance(doc['created_at'], datetime):
                doc['created_at'] = doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
    except Exception as e:
        app.logger.error(f"文書取得中にエラーが発生しました: {e}")
        return jsonify({
            'success': False,
            'error': f'文書取得中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/documents', methods=['POST'])
def add_document():
    """新しい文書を追加"""
    if not rag:
        if not initialize_rag():
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
    
    data = request.json
    title = data.get('title', '')
    content = data.get('content', '')
    metadata = data.get('metadata', {})
    
    if not title or not content:
        return jsonify({
            'success': False,
            'error': 'タイトルと本文は必須です'
        }), 400
    
    try:
        success = rag.add_document(title, content, metadata)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'文書「{title}」が正常に追加されました'
            })
        else:
            return jsonify({
                'success': False,
                'error': '文書の追加に失敗しました'
            }), 500
    except Exception as e:
        app.logger.error(f"文書追加中にエラーが発生しました: {e}")
        return jsonify({
            'success': False,
            'error': f'文書追加中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """文書を削除"""
    if not rag:
        if not initialize_rag():
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
    
    try:
        success = rag.db.delete_document(doc_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'文書ID {doc_id} が正常に削除されました'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'文書ID {doc_id} が見つかりませんでした'
            }), 404
    except Exception as e:
        app.logger.error(f"文書削除中にエラーが発生しました: {e}")
        return jsonify({
            'success': False,
            'error': f'文書削除中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """静的ファイルを提供"""
    return send_from_directory(app.static_folder, filename)

def create_app():
    """アプリケーションファクトリ関数"""
    return app

if __name__ == '__main__':    # 環境変数の確認
    print(f"GOOGLE_API_KEY環境変数: {'設定されています' if os.getenv('GOOGLE_API_KEY') else '設定されていません'}")
    print(f"Config.GOOGLE_API_KEY: {'設定されています' if Config.GOOGLE_API_KEY else '設定されていません'}")
    
    if not Config.GOOGLE_API_KEY:
        print("警告: GOOGLE_API_KEYが設定されていません。.envファイルを確認してください。")
        
    # PostgreSQL接続情報の確認
    print(f"PostgreSQL接続情報:")
    print(f"  DB_HOST: {Config.DB_HOST}")
    print(f"  DB_NAME: {Config.DB_NAME}")
    print(f"  DB_USER: {Config.DB_USER}")
    print(f"  DB_PORT: {Config.DB_PORT}")      # プロダクションモードで実行（デバッグ無効）
    app.logger.setLevel('INFO')  # ログレベルをINFOに設定
    app.run(debug=False, host='0.0.0.0', port=5000)
