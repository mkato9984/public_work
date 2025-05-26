#!/usr/bin/env python
"""
RAGシステムのWebインターフェース - GitHub Codespaces デモ対応版
API Key未設定でも基本画面が表示される
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from config import Config

# .envファイルから環境変数を読み込み
load_dotenv()

def create_app():
    """アプリケーションファクトリパターン"""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Flask設定
    app.config['SECRET_KEY'] = Config.SECRET_KEY or 'demo-secret-key-for-codespaces'
    app.config['DEBUG'] = Config.DEBUG
    
    # デモモード設定
    demo_mode = not Config.GOOGLE_API_KEY
    rag_instance = None
    
    def get_rag_instance():
        """RAGシステムのインスタンスを取得（デモモード対応）"""
        nonlocal rag_instance
        if demo_mode:
            print("🎭 デモモード: GOOGLE_API_KEYが未設定のため、デモ機能で動作します")
            return None
            
        if rag_instance is None:
            try:
                import rag_system
                api_key = Config.GOOGLE_API_KEY
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
            'demo_mode': demo_mode,
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'api_key_configured': bool(Config.GOOGLE_API_KEY)
        })

    @app.route('/')
    def index():
        """メインページ"""
        return render_template('index.html', demo_mode=demo_mode)

    @app.route('/api/demo-status')
    def demo_status():
        """デモモード状態確認"""
        return jsonify({
            'demo_mode': demo_mode,
            'message': 'GOOGLE_API_KEYを設定すると完全な機能が利用できます' if demo_mode else '完全な機能が利用可能です',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        """文書一覧を取得"""
        if demo_mode:
            # デモ用のサンプルデータ
            return jsonify({
                'success': True,
                'demo_mode': True,
                'documents': [
                    {
                        'id': 1,
                        'title': '📋 デモ文書1: RAGシステムについて',
                        'content': 'これはデモ用のサンプル文書です。実際のRAGシステムでは、ここに実際の文書が表示されます。',
                        'created_at': '2025-05-26 12:00:00',
                        'metadata': {'type': 'demo', 'category': 'sample'}
                    },
                    {
                        'id': 2,
                        'title': '🤖 デモ文書2: AI応答機能',
                        'content': 'GOOGLE_API_KEYを設定することで、実際のAI応答機能が利用できるようになります。',
                        'created_at': '2025-05-26 12:05:00',
                        'metadata': {'type': 'demo', 'category': 'guide'}
                    },
                    {
                        'id': 3,
                        'title': '⚙️ デモ文書3: 設定ガイド',
                        'content': 'GitHub Codespacesで環境変数を設定する方法について説明します。',
                        'created_at': '2025-05-26 12:10:00',
                        'metadata': {'type': 'demo', 'category': 'tutorial'}
                    }
                ],
                'count': 3,
                'message': 'デモモードで実行中 - GOOGLE_API_KEYを設定すると実際のデータが表示されます'
            })
        
        rag_instance = get_rag_instance()
        if not rag_instance:
            return jsonify({
                'success': False,
                'demo_mode': demo_mode,
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
                'demo_mode': False,
                'documents': documents,
                'count': len(documents)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'demo_mode': demo_mode,
                'error': f'文書取得エラー: {str(e)}'
            }), 500

    @app.route('/api/documents', methods=['POST'])
    def add_document():
        """新しい文書を追加"""
        if demo_mode:
            return jsonify({
                'success': False,
                'demo_mode': True,
                'error': 'デモモードでは文書の追加はできません。GOOGLE_API_KEYを設定してください。',
                'message': 'GitHub Codespacesで環境変数を設定する方法: export GOOGLE_API_KEY="your-key"'
            }), 400
        
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
                'error': 'タイトルと内容は必須です'
            }), 400
        
        try:
            document_id = rag_instance.add_document(title, content, metadata)
            return jsonify({
                'success': True,
                'document_id': document_id,
                'message': '文書が正常に追加されました'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'文書追加エラー: {str(e)}'
            }), 500

    @app.route('/api/documents/<int:document_id>', methods=['DELETE'])
    def delete_document(document_id):
        """指定されたIDの文書を削除"""
        if demo_mode:
            return jsonify({
                'success': False,
                'demo_mode': True,
                'error': 'デモモードでは文書の削除はできません。GOOGLE_API_KEYを設定してください。'
            }), 400
        
        rag_instance = get_rag_instance()
        if not rag_instance:
            return jsonify({
                'success': False,
                'error': 'RAGシステムが初期化されていません'
            }), 500
        
        try:
            success = rag_instance.delete_document(document_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'文書ID {document_id} を削除しました'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '文書が見つからないか、削除に失敗しました'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'削除エラー: {str(e)}'
            }), 500

    @app.route('/api/ask', methods=['POST'])
    def ask_question():
        """質問に対する回答を生成"""
        if demo_mode:
            data = request.json
            question = data.get('question', '')
            
            # デモ用の応答
            demo_responses = {
                'rag': 'RAGシステムは、Retrieval-Augmented Generation（検索拡張生成）の略で、文書検索とAI生成を組み合わせたシステムです。',
                'システム': 'このシステムは、PostgreSQLとpgvectorを使用した高速なベクトル検索機能を提供します。',
                '設定': 'GOOGLE_API_KEYを設定することで、実際のAI応答機能が利用できます。GitHub Codespacesでは、export GOOGLE_API_KEY="your-key" を実行してください。',
                'codespaces': 'GitHub Codespacesは、クラウド上で完全な開発環境を提供するサービスです。PostgreSQLやpgvectorも自動的にセットアップされます。'
            }
            
            # キーワードに基づく簡単な応答選択
            response = "デモモードで実行中です。GOOGLE_API_KEYを設定すると、実際のAI応答が利用できます。"
            for keyword, demo_response in demo_responses.items():
                if keyword.lower() in question.lower():
                    response = demo_response
                    break
            
            return jsonify({
                'success': True,
                'demo_mode': True,
                'answer': f"🎭 [デモ応答] {response}",
                'question': question,
                'message': '実際のAI応答を利用するには GOOGLE_API_KEY を設定してください'
            })
        
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
                'error': '質問を入力してください'
            }), 400
        
        try:
            answer = rag_instance.answer_question(question)
            return jsonify({
                'success': True,
                'demo_mode': False,
                'answer': answer,
                'question': question
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'回答生成エラー: {str(e)}'
            }), 500

    @app.route('/api/test')
    def test_endpoint():
        """テスト用エンドポイント"""
        return jsonify({
            'status': 'ok',
            'demo_mode': demo_mode,
            'message': 'GitHub Codespaces RAGシステム - デモ対応版',
            'timestamp': datetime.now().isoformat(),
            'environment_info': {
                'python_version': os.sys.version,
                'api_key_set': bool(Config.GOOGLE_API_KEY),
                'demo_mode': demo_mode
            }
        })

    return app

def main():
    """メイン実行関数"""
    print("🚀 GitHub Codespaces対応 RAGシステムを起動中...")
    
    # 環境情報表示
    demo_mode = not Config.GOOGLE_API_KEY
    print(f"🎭 デモモード: {'有効' if demo_mode else '無効'}")
    
    if demo_mode:
        print("⚠️  GOOGLE_API_KEYが未設定です")
        print("📋 デモモードで基本機能を提供します")
        print("💡 完全な機能を利用するには以下を実行してください:")
        print("   export GOOGLE_API_KEY='your-actual-api-key'")
        print("")
    else:
        print("✅ GOOGLE_API_KEYが設定されています")
    
    app = create_app()
    
    # 起動情報表示    print("🌐 アクセス方法:")
    print("   ローカル: http://localhost:5000")
    print("   Codespaces: ポート転送されたURL (自動的に開きます)")
    print("")
    print("📊 利用可能なエンドポイント:")
    print("   / - メイン画面")
    print("   /health - ヘルスチェック")
    print("   /api/demo-status - デモモード状態")
    print("   /api/test - テストエンドポイント")
    print("")
    
    # デバッグモード無効で起動
    app.run(host='0.0.0.0', port=5000, debug=False)

# Gunicorn用のアプリインスタンス
app = create_app()

if __name__ == '__main__':
    main()
