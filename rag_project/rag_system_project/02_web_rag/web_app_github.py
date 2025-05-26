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
                print("✅ RAGシステムの初期化が完了しました")
                return rag_instance
            except Exception as e:
                print(f"❌ RAGシステムの初期化に失敗しました: {e}")
                return None
        return rag_instance
    
    # ヘルスチェックエンドポイント
    @app.route('/health')
    def health_check():
        """ヘルスチェック（GitHub Actions用）"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.1'
        })

    @app.route('/')
    def index():
        """メインページ"""
        return render_template('index.html')

    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        """文書一覧を取得"""
        rag = get_rag_instance()
        if not rag:
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
        
        try:
            documents = rag.get_all_documents()
            return jsonify({
                'success': True,
                'documents': documents,
                'count': len(documents)
            })
        except Exception as e:
            print(f"文書取得エラー: {e}")
            return jsonify({
                'success': False,
                'error': f'文書の取得に失敗しました: {str(e)}'
            }), 500

    @app.route('/api/documents', methods=['POST'])
    def add_document():
        """新しい文書を追加"""
        rag = get_rag_instance()
        if not rag:
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
        
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'タイトルと内容は必須です'
            }), 400
        
        try:
            document_id = rag.add_document(
                title=data['title'],
                content=data['content'],
                metadata=data.get('metadata', {})
            )
            
            return jsonify({
                'success': True,
                'message': f'文書「{data["title"]}」が正常に追加されました',
                'document_id': document_id
            })
        except Exception as e:
            print(f"文書追加エラー: {e}")
            return jsonify({
                'success': False,
                'error': f'文書の追加に失敗しました: {str(e)}'
            }), 500

    @app.route('/api/documents/<int:document_id>', methods=['DELETE'])
    def delete_document(document_id):
        """文書を削除"""
        rag = get_rag_instance()
        if not rag:
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
        
        try:
            success = rag.delete_document(document_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'文書 ID {document_id} が正常に削除されました'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'文書 ID {document_id} の削除に失敗しました'
                }), 404
        except Exception as e:
            print(f"文書削除エラー: {e}")
            return jsonify({
                'success': False,
                'error': f'文書の削除に失敗しました: {str(e)}'
            }), 500

    @app.route('/api/ask', methods=['POST'])
    def ask_question():
        """質問応答"""
        rag = get_rag_instance()
        if not rag:
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
        
        data = request.json
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': '質問が入力されていません'
            }), 400
        
        try:
            question = data['question']
            print(f"質問を受信: {question}")
            
            answer, sources = rag.ask(question)
            
            return jsonify({
                'success': True,
                'answer': answer,
                'sources': sources,
                'question': question,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            print(f"質問応答エラー: {e}")
            return jsonify({
                'success': False,
                'error': f'質問応答に失敗しました: {str(e)}'
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        """404エラーハンドラ"""
        return jsonify({
            'success': False,
            'error': 'ページが見つかりません'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500エラーハンドラ"""
        return jsonify({
            'success': False,
            'error': 'サーバー内部エラーが発生しました'
        }), 500

    return app

# アプリケーションの作成
app = create_app()

if __name__ == "__main__":
    # 設定検証
    if not Config.validate():
        print("❌ 設定エラー: 必要な環境変数が設定されていません")
        exit(1)
    
    print("🚀 RAGシステム Webアプリケーションを起動中...")
    print(f"🏠 ホスト: localhost")
    print(f"🚪 ポート: 5000")
    print(f"🌐 URL: http://localhost:5000")
    print(f"🔧 デバッグモード: {Config.DEBUG}")
    print(f"🏭 本番環境: {Config.IS_PRODUCTION}")
    
    # ポート設定（Heroku対応）
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if Config.IS_PRODUCTION else 'localhost'
    
    app.run(
        host=host,
        port=port,
        debug=Config.DEBUG,
        use_reloader=not Config.IS_PRODUCTION
    )
