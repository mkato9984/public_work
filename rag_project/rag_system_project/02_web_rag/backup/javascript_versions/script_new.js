// グローバル削除関数
function deleteDocument(documentId) {
    console.log(`削除関数が呼び出されました: 文書ID = ${documentId}`);
    
    if (!documentId) {
        console.error('文書IDが無効です');
        showNotification('エラー: 文書IDが無効です', 'error');
        return;
    }
    
    if (confirm('この文書を削除してもよろしいですか？')) {
        console.log('削除が確認されました。リクエストを送信中...');
        showLoading();
        
        fetch(`/api/documents/${documentId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('削除レスポンス受信:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('削除レスポンスデータ:', data);
            hideLoading();
            
            if (data.success) {
                showNotification(data.message, 'success');
                console.log('削除成功、文書一覧を更新します');
                fetchDocuments(); // 文書一覧を更新
            } else {
                showNotification('エラー: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('削除エラー:', error);
            hideLoading();
            showNotification('通信エラーが発生しました: ' + error.message, 'error');
        });
    } else {
        console.log('削除がキャンセルされました');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // タブ切り替え機能
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // タブボタンのアクティブ状態を切り替え
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // タブコンテンツの表示切り替え
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
            
            // 文書管理タブを選択した場合、文書リストを更新
            if (tabId === 'documents') {
                fetchDocuments();
            }
        });
    });
    
    // 質問送信機能
    const questionInput = document.getElementById('question-input');
    const askButton = document.getElementById('ask-btn');
    const qaResults = document.getElementById('qa-results');
    
    askButton.addEventListener('click', () => {
        const question = questionInput.value.trim();
        if (!question) return;
        
        // ローディング表示
        showLoading();
        
        // APIリクエスト
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                // 質問と回答を表示
                const qaItem = document.createElement('div');
                qaItem.className = 'qa-item';
                qaItem.innerHTML = `
                    <div class="qa-question">質問: ${data.question}</div>
                    <div class="qa-answer">${data.answer}</div>
                    <div class="qa-timestamp">${data.timestamp}</div>
                `;
                
                // 最新の質問を先頭に表示
                qaResults.insertBefore(qaItem, qaResults.firstChild);
                
                // 入力フィールドをクリア
                questionInput.value = '';
            } else {
                showNotification('エラー: ' + data.error, 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('通信エラーが発生しました: ' + error, 'error');
        });
    });
    
    // エンターキーで質問送信
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            askButton.click();
        }
    });
    
    // 文書追加機能
    const docTitleInput = document.getElementById('doc-title');
    const docContentInput = document.getElementById('doc-content');
    const docMetadataInput = document.getElementById('doc-metadata');
    const addDocumentBtn = document.getElementById('add-document-btn');
    
    addDocumentBtn.addEventListener('click', () => {
        const title = docTitleInput.value.trim();
        const content = docContentInput.value.trim();
        let metadata = {};
        
        // メタデータのパース
        try {
            const metadataText = docMetadataInput.value.trim();
            if (metadataText) {
                metadata = JSON.parse(metadataText);
            }
        } catch (error) {
            showNotification('メタデータのJSON形式が不正です', 'error');
            return;
        }
        
        if (!title || !content) {
            showNotification('タイトルと内容は必須です', 'error');
            return;
        }
        
        // ローディング表示
        showLoading();
        
        // APIリクエスト
        fetch('/api/documents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content, metadata })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                // 入力フィールドをクリア
                docTitleInput.value = '';
                docContentInput.value = '';
                docMetadataInput.value = '';
                
                // 文書リスト更新
                fetchDocuments();
                
                showNotification(data.message, 'success');
            } else {
                showNotification('エラー: ' + data.error, 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('通信エラーが発生しました: ' + error, 'error');
        });
    });
    
    // 文書一覧取得・表示機能
    function fetchDocuments() {
        showLoading();
        
        fetch('/api/documents')
            .then(response => response.json())
            .then(data => {
                hideLoading();
                
                if (data.success) {
                    const documentsContainer = document.getElementById('documents-container');
                    const docCount = document.getElementById('doc-count');
                    
                    // 文書数表示
                    docCount.textContent = data.count;
                    
                    // 文書リストを表示
                    documentsContainer.innerHTML = '';
                    
                    console.log(`文書を表示中: ${data.documents.length} 件の文書`);
                    
                    data.documents.forEach((doc, index) => {
                        console.log(`文書 ${index + 1}: ID=${doc.id}, Title=${doc.title}`);
                        
                        const docCard = document.createElement('div');
                        docCard.className = 'document-card';
                        
                        // メタデータのフォーマット
                        let metadataHtml = '';
                        if (doc.metadata) {
                            try {
                                const metadata = typeof doc.metadata === 'string' 
                                    ? JSON.parse(doc.metadata) 
                                    : doc.metadata;
                                
                                const metadataStr = Object.entries(metadata)
                                    .map(([key, value]) => `${key}: ${value}`)
                                    .join(', ');
                                
                                metadataHtml = `<div class="document-metadata">メタデータ: ${metadataStr}</div>`;
                            } catch (e) {
                                metadataHtml = '';
                            }
                        }
                        
                        docCard.innerHTML = `
                            <div class="document-title">${doc.title}</div>
                            <div class="document-content">${doc.content}</div>
                            ${metadataHtml}
                            <div class="document-actions">
                                <button class="delete-btn" onclick="deleteDocument(${doc.id})" data-id="${doc.id}">削除</button>
                            </div>
                        `;
                        
                        console.log(`削除ボタンのdata-id: ${doc.id}`);
                        documentsContainer.appendChild(docCard);
                    });
                } else {
                    showNotification('エラー: ' + data.error, 'error');
                }
            })
            .catch(error => {
                hideLoading();
                showNotification('通信エラーが発生しました: ' + error, 'error');
            });
    }
    
    // ユーティリティ関数をグローバルスコープで再定義
    window.showLoading = function() {
        document.getElementById('loading-overlay').style.display = 'flex';
    };
    
    window.hideLoading = function() {
        document.getElementById('loading-overlay').style.display = 'none';
    };
    
    window.showNotification = function(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // 5秒後に自動的に消える
        setTimeout(() => {
            notification.remove();
        }, 5000);
    };
    
    window.fetchDocuments = fetchDocuments;
    
    // 初期表示: 質問応答タブを表示
    document.querySelector('.tab-btn[data-tab="qa"]').click();
});
