function countCharacters() {
  const textarea = document.getElementById('tweet');
  const remainingCount = document.getElementById('remaining');
  const maxCount = 280;
  let count = 0;

  for (let i = 0; i < textarea.value.length; i++) {
    if (textarea.value.charCodeAt(i) > 127) {
      count += 2; // 日本語の文字を2とカウント
    } else {
      count += 1; // その他の文字を1とカウント
    }
  }

  // 残りの文字数を計算し、表示
  const remaining = maxCount - count;
  remainingCount.textContent = remaining >= 0 ? remaining : 0;

  // 残り文字数が0以下になった場合は警告色を表示
  if (remaining < 0) {
    remainingCount.classList.add('text-danger');
  } else {
    remainingCount.classList.remove('text-danger');
  }
}

// ドキュメントが読み込まれたらイベントリスナーを設定
document.addEventListener('DOMContentLoaded', function() {
  const textarea = document.getElementById('tweet');
  textarea.addEventListener('input', countCharacters);

  // 初期ロード時の文字数カウントを更新
  countCharacters();
});
