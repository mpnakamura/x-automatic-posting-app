from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2  # 修正した関数名をインポート
import os

app = Flask(__name__)
tweets = []  
client = create_api_v2()  # v2 APIクライアントの作成

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        if action == 'ツイート':
            try:
                response = post_tweet_v2(client, tweet_content)  # v2 APIを使用してツイート投稿
                message = "ツイートが投稿されました: " + str(response)
            except Exception as e:
                message = "エラーが発生しました: " + str(e)
        elif action == '保存':
            tweets.append(tweet_content)
            message = "ツイートを保存しました"
        elif action == '削除':
            # リストから特定のツイートを削除
            tweet_to_delete = request.form.get('tweet_to_delete')
            if tweet_to_delete in tweets:
                tweets.remove(tweet_to_delete)
                message = "ツイートを削除しました"

    return render_template('index.html', message=message, tweets=tweets)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))









