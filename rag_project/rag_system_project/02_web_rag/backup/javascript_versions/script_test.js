// 簡単なタブ切り替えテスト用のJavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM読み込み完了 - テスト版');
    
    // タブボタンとコンテンツを取得
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`発見されたタブボタン: ${tabButtons.length}`);
    console.log(`発見されたタブコンテンツ: ${tabContents.length}`);
    
    // 各タブボタンにクリックイベントリスナーを追加
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTabId = this.getAttribute('data-tab');
            console.log(`クリックされたタブ: ${targetTabId}`);
            
            // すべてのタブボタンからactiveクラスを削除
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // クリックされたボタンにactiveクラスを追加
            this.classList.add('active');
            
            // すべてのタブコンテンツからactiveクラスを削除
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 対応するタブコンテンツにactiveクラスを追加
            const targetContent = document.getElementById(`${targetTabId}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
                console.log(`タブコンテンツ ${targetTabId}-tab を表示しました`);
            } else {
                console.error(`タブコンテンツ ${targetTabId}-tab が見つかりません`);
            }
        });
    });
    
    console.log('タブ切り替え機能初期化完了');
});
