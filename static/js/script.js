document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  form.addEventListener('submit', function(event) {
    // フォームの送信時に特定の動作をする
    alert('ツイートが送信されました！');
  });
});
