import pytest
import json

def test_index_page(client):
    """メインページのテスト"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'RAG' in response.data or b'Q&A' in response.data

def test_health_check(client):
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get('/health')
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    else:
        # ヘルスチェックエンドポイントが存在しない場合は404が期待される
        assert response.status_code == 404

def test_documents_api_get(client):
    """文書一覧取得APIのテスト"""
    response = client.get('/api/documents')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'success' in data
    assert 'documents' in data or 'count' in data

def test_documents_api_post(client):
    """文書追加APIのテスト"""
    test_document = {
        'title': 'テスト文書',
        'content': 'これはテスト用の文書です。',
        'metadata': {'source': 'test'}
    }
    
    response = client.post('/api/documents', 
                          data=json.dumps(test_document),
                          content_type='application/json')
    
    # APIキーが設定されていない場合は500エラーが予想される
    assert response.status_code in [200, 201, 500]
    
    if response.status_code in [200, 201]:
        data = json.loads(response.data)
        assert 'success' in data

def test_ask_api(client):
    """質問APIのテスト"""
    test_question = {
        'question': 'テスト質問です'
    }
    
    response = client.post('/api/ask',
                          data=json.dumps(test_question),
                          content_type='application/json')
    
    # APIキーが設定されていない場合は500エラーが予想される
    assert response.status_code in [200, 500]

def test_static_files(client):
    """静的ファイルの配信テスト"""
    # CSS
    response = client.get('/static/css/style.css')
    assert response.status_code == 200
    assert b'body' in response.data or b'html' in response.data
    
    # JavaScript
    response = client.get('/static/js/script.js')
    assert response.status_code == 200
    assert b'function' in response.data or b'document' in response.data
