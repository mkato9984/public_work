#!/usr/bin/env python
"""
RAGシステムのWebインターフェース - GitHub/クラウド対応版
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import rag_system
from config import Config

# .envファイルから環境変数を読み込み
load_dotenv()

def create_app():
    """アプリケーションファクトリパターン"""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Flask設定
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    
    # RAGシステムのインスタンス（アプリケーション内で共有）
    rag_instance = None
    
    def get_rag_instance():
        """RAGシステムのインスタンスを取得（初期化済みでない場合は初期化）"""
        nonlocal rag_instance
        if rag_instance is None:
            api_key = Config.GOOGLE_API_KEY
            if not api_key:
                print("エラー: GOOGLE_API_KEYが設定されていません")
                return None
              try:
                print(f"RAGシステムを初期化中... API Key: {api_key[:4] if len(api_key) > 8 else 'SHORT'}...")
                rag_instance = rag_system.RAGSystem(api_key)
                
                if rag_instance.initialize_database():
                    print("RAGシステムが正常に初期化されました")
                    return rag_instance
                else:
                    print("データベース初期化に失敗しました")
                    rag_instance = None
                    return None
            except Exception as e:
                print(f"RAGシステム初期化エラー: {e}")
                rag_instance = None
                return None
        
        return rag_instance

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """文書一覧を取得"""
    rag_instance = get_rag_instance()
    if not rag_instance:
        return jsonify({
            'success': False,
            'error': 'RAGシステムが初期化されていません'
        }), 500
    
    try:
        documents = rag_instance.list_all_documents()
        
        # 埋め込みベクトルを除外して日時を文字列に変換
        for doc in documents:
            doc.pop('embedding', None)
            if 'created_at' in doc and isinstance(doc['created_at'], datetime):
                doc['created_at'] = doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文書取得エラー: {str(e)}'
        }), 500

@app.route('/api/documents', methods=['POST'])
def add_document():
    """新しい文書を追加"""
    rag_instance = get_rag_instance()
    if not rag_instance:
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
        success = rag_instance.add_document(title, content, metadata)
        
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
        return jsonify({
            'success': False,
            'error': f'文書追加エラー: {str(e)}'
        }), 500

@app.route('/api/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """指定されたIDの文書を削除"""
    rag_instance = get_rag_instance()
    if not rag_instance:
        return jsonify({
            'success': False,
            'error': 'RAGシステムが初期化されていません'
        }), 500
    
    try:
        success = rag_instance.db.delete_document(document_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'文書ID {document_id} が正常に削除されました'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'文書ID {document_id} が見つからないか、削除に失敗しました'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文書削除エラー: {str(e)}'
        }), 500

@app.route('/api/query', methods=['POST'])
def query():
    """質問に対する回答を生成"""
    rag_instance = get_rag_instance()
    if not rag_instance:
        return jsonify({
            'success': False,
            'error': 'RAGシステムが初期化されていません'
        }), 500
    
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({
            'success': False,
            'error': '質問が入力されていません'
        }), 400
    
    try:
        print(f"質問を受信: {question}")
        answer = rag_instance.answer_question(question)
        print(f"回答を生成: {answer[:100]}...")  # 最初の100文字をログ出力
        return jsonify({
            'success': True,
            'answer': answer,
            'question': question,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        print(f"質問応答エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'回答生成エラー: {str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """テスト用エンドポイント"""
    rag_instance = get_rag_instance()
    
    return jsonify({
        'success': True,
        'message': 'APIが正常に動作しています',
        'rag_initialized': rag_instance is not None,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    print("============================================================")
    print("🚀 RAG System - Webアプリケーション (完全版)")
    print("============================================================")
    
    # 設定確認
    if Config.GOOGLE_API_KEY:
        print(f"✅ GOOGLE_API_KEY: 設定済み ({Config.GOOGLE_API_KEY[:4]}...{Config.GOOGLE_API_KEY[-4:]})")
    else:
        print("❌ GOOGLE_API_KEY: 未設定")
        
    print(f"📊 DB設定: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    print(f"📁 作業ディレクトリ: {os.getcwd()}")
    print(f"🌐 URL: http://localhost:5000")
    print("============================================================")
    
    # デバッグモード無効で起動
    app.run(debug=False, host='0.0.0.0', port=5000)