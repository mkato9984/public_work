// VS Code Simple Browser用のデバッグ関数
function debugSimpleBrowser() {
    console.log('=== VS Code Simple Browser Debug Info ===');
    console.log('User Agent:', navigator.userAgent);
    console.log('Window Object:', typeof window);
    console.log('Document Object:', typeof document);
    console.log('fetch available:', typeof fetch);
    console.log('confirm available:', typeof confirm);
    console.log('addEventListener available:', typeof document.addEventListener);
    console.log('Event delegation test:', document.querySelector('body') !== null);
    console.log('Current URL:', window.location.href);
    console.log('=== End Debug Info ===');
}

// グローバル削除関数
function deleteDocument(documentId) {
    console.log(`削除関数が呼び出されました: 文書ID = ${documentId}`);
    console.log('削除関数のtypeof:', typeof documentId);
    console.log('削除関数のdocumentIdの値:', documentId);
    
    // 文字列として扱い、数値に変換を試す
    const numericId = parseInt(documentId, 10);
    if (isNaN(numericId) || numericId <= 0) {
        console.error('文書IDが無効です:', documentId);
        showNotification('エラー: 文書IDが無効です', 'error');
        return;
    }
    
    console.log('有効な文書ID確認:', numericId);
    
    // confirmの代わりにカスタム確認ダイアログを使用（VS Code Simple Browser対応）
    let shouldDelete = true;
    try {
        shouldDelete = confirm('この文書を削除してもよろしいですか？');
    } catch (e) {
        console.warn('confirm関数が利用できません。削除を続行します。');
        shouldDelete = true; // フォールバック
    }
    
    if (shouldDelete) {
        console.log('削除が確認されました。リクエストを送信中...');
        showLoading();
        
        const url = `/api/documents/${numericId}`;
        console.log('削除リクエストURL:', url);
        
        // fetchオプションを詳細に設定
        const fetchOptions = {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin' // VS Code Simple Browser用
        };
        
        console.log('フェッチオプション:', fetchOptions);
        
        fetch(url, fetchOptions)
        .then(response => {
            console.log('削除レスポンス受信:', response.status, response.statusText);
            console.log('レスポンスヘッダー:', [...response.headers.entries()]);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('削除レスポンスデータ:', data);
            hideLoading();
            
            if (data.success) {
                showNotification(data.message || '文書が正常に削除されました', 'success');
                console.log('削除成功、文書一覧を更新します');
                
                // 少し遅延を入れてからリストを更新
                setTimeout(() => {
                    fetchDocuments();
                }, 100);
            } else {
                showNotification('エラー: ' + (data.error || '削除に失敗しました'), 'error');
            }
        })
        .catch(error => {
            console.error('削除エラーの詳細:', error);
            hideLoading();
            showNotification('通信エラーが発生しました: ' + error.message, 'error');
        });
    } else {
        console.log('削除がキャンセルされました');
    }
}

// インラインクリックハンドラ用の関数
function handleDeleteClick(documentId) {
    console.log(`handleDeleteClick呼び出し: ID = ${documentId}`);
    deleteDocument(documentId);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM読み込み完了');
    
    // VS Code Simple Browser環境のデバッグ
    debugSimpleBrowser();
    
    // 複数のイベントハンドリング方法でVS Code Simple Browser対応
    
    // 方法1: イベントデリゲーション（標準）
    document.addEventListener('click', function(event) {
        console.log('documentクリックイベント:', event.target);
        
        if (event.target && event.target.classList.contains('delete-btn')) {
            console.log('削除ボタンクリック検出（イベントデリゲーション）');
            event.preventDefault();
            event.stopPropagation();
            
            const documentId = event.target.getAttribute('data-id');
            console.log(`イベントデリゲーションで削除ボタンクリック検出: ID = ${documentId}`);
            
            if (documentId) {
                deleteDocument(documentId);
            } else {
                console.error('削除ボタンにdata-id属性が見つかりません');
                console.log('削除ボタンのattributes:', event.target.attributes);
            }
        }
    });
    
    // 方法2: documents-container特化のイベントデリゲーション
    const documentsContainer = document.getElementById('documents-container');
    if (documentsContainer) {
        documentsContainer.addEventListener('click', function(event) {
            console.log('documentsContainerクリックイベント:', event.target);
            
            if (event.target && event.target.classList.contains('delete-btn')) {
                console.log('削除ボタンクリック検出（コンテナイベント）');
                event.preventDefault();
                event.stopPropagation();
                
                const documentId = event.target.getAttribute('data-id');
                console.log(`コンテナイベントで削除ボタンクリック検出: ID = ${documentId}`);
                
                if (documentId) {
                    deleteDocument(documentId);
                }
            }
        });
    }

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
                        docCard.setAttribute('data-doc-id', doc.id); // 削除用の識別子
                        
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
                        }                        docCard.innerHTML = `
                            <div class="document-title">${doc.title}</div>
                            <div class="document-content">${doc.content}</div>
                            ${metadataHtml}
                            <div class="document-actions">
                                <button class="delete-btn" data-id="${doc.id}" data-title="${doc.title}" type="button" 
                                        onclick="simpleBrowserDelete(${doc.id})" 
                                        onmousedown="simpleBrowserDelete(${doc.id})">削除</button>
                            </div>
                        `;
                          console.log(`文書カード作成完了: ID=${doc.id}, Title=${doc.title}`);
                        documentsContainer.appendChild(docCard);
                        
                        // VS Code Simple Browser用の追加的なイベントリスナー設定
                        const deleteBtn = docCard.querySelector('.delete-btn');
                        if (deleteBtn) {
                            console.log(`削除ボタンにイベントリスナーを設定: ID=${doc.id}`);
                            console.log('削除ボタンの属性確認:', deleteBtn.attributes);
                            console.log('削除ボタンのdata-id:', deleteBtn.getAttribute('data-id'));
                            
                            // 複数の方法でイベントリスナーを設定
                            deleteBtn.addEventListener('click', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log(`削除ボタン直接クリック（addEventListener）: ID=${doc.id}`);
                                deleteDocument(doc.id);
                            });
                              // フォールバック用のonclickも設定
                            deleteBtn.onclick = function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log(`削除ボタン直接クリック（onclick）: ID=${doc.id}`);
                                
                                // 複数の削除方法を順次試行
                                try {
                                    deleteDocument(doc.id);
                                } catch (error1) {
                                    console.warn('deleteDocument失敗:', error1);
                                    try {
                                        simpleBrowserDelete(doc.id);
                                    } catch (error2) {
                                        console.error('simpleBrowserDelete失敗:', error2);
                                        // 最終手段: 直接確認後に削除
                                        if (window.confirm && window.confirm('この文書を削除しますか？')) {
                                            simpleBrowserDelete(doc.id);
                                        }
                                    }
                                }
                                return false;
                            };
                            
                            // タッチイベントも追加（モバイル対応）
                            deleteBtn.addEventListener('touchstart', function(e) {
                                e.preventDefault();
                                console.log(`削除ボタンタッチ: ID=${doc.id}`);
                                deleteDocument(doc.id);
                            });
                        } else {
                            console.error(`削除ボタンが見つかりません: ID=${doc.id}`);
                        }
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
    
    // VS Code Simple Browser用のフォールバック削除機能
    window.simpleBrowserDelete = function(documentId) {
        console.log('Simple Browser用削除機能が呼び出されました:', documentId);
        
        // ローディング表示
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'block';
        }
        
        // XMLHttpRequestを使用（fetchの代替）
        const xhr = new XMLHttpRequest();
        xhr.open('DELETE', `/api/documents/${documentId}`, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('XHR Status:', xhr.status);
                console.log('XHR Response:', xhr.responseText);
                
                // ローディング非表示
                if (loadingDiv) {
                    loadingDiv.style.display = 'none';
                }
                
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            alert('文書が削除されました');
                            // 削除されたカードを即座に削除
                            const docCard = document.querySelector(`[data-doc-id="${documentId}"]`);
                            if (docCard) {
                                docCard.remove();
                            }
                            // リストを再読み込み
                            setTimeout(() => {
                                if (typeof fetchDocuments === 'function') {
                                    fetchDocuments();
                                }
                            }, 500);
                        } else {
                            alert('削除に失敗しました: ' + response.error);
                        }
                    } catch (e) {
                        console.error('JSON解析エラー:', e);
                        alert('レスポンスの解析に失敗しました');
                    }
                } else {
                    alert('削除リクエストが失敗しました: ' + xhr.status);
                }
            }
        };
        
        xhr.onerror = function() {
            console.error('XHRエラー');
            if (loadingDiv) {
                loadingDiv.style.display = 'none';
            }
            alert('通信エラーが発生しました');
        };
        
        xhr.send();
    };

    // グローバルエラーハンドリング
window.addEventListener('error', function(e) {
    console.error('グローバルエラー:', e.error);
    console.error('エラーメッセージ:', e.message);
    console.error('ファイル:', e.filename);
    console.error('行番号:', e.lineno);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('未処理のPromise拒否:', e.reason);
});

    // デバッグ用のテスト関数
    function testDeleteFunction() {
        console.log('=== Delete Function Test ===');
        console.log('deleteDocument type:', typeof deleteDocument);
        console.log('simpleBrowserDelete type:', typeof simpleBrowserDelete);
        console.log('handleDeleteClick type:', typeof handleDeleteClick);
        
        // フェッチテスト
        fetch('/api/documents')
            .then(response => {
                console.log('Fetch test successful:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('API response test:', data);
            })
            .catch(error => {
                console.error('Fetch test failed:', error);
            });
    }

    // 削除ボタンのクリック状況をテスト
    function testDeleteButton() {
        const deleteButtons = document.querySelectorAll('.delete-btn');
        console.log('削除ボタンの数:', deleteButtons.length);
        
        deleteButtons.forEach((btn, index) => {
            console.log(`削除ボタン ${index + 1}:`);
            console.log('  data-id:', btn.getAttribute('data-id'));
            console.log('  onclick:', btn.onclick);
            console.log('  イベントリスナー数:', getEventListeners ? getEventListeners(btn) : '不明');
        });
    }

    // ウィンドウにテスト関数を公開
    window.testDeleteFunction = testDeleteFunction;
    window.testDeleteButton = testDeleteButton;

    // ユーティリティ関数
    function showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }
    
    function hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }
    
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // 5秒後に自動的に消える
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
      // グローバルスコープで関数を使用可能にする
    window.showLoading = showLoading;
    window.hideLoading = hideLoading;
    window.showNotification = showNotification;
    window.fetchDocuments = fetchDocuments;
    window.deleteDocument = deleteDocument;
    window.handleDeleteClick = handleDeleteClick;
    
    // 初期表示: 質問応答タブを表示
    document.querySelector('.tab-btn[data-tab="qa"]').click();
});
