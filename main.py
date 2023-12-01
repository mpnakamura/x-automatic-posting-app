from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2
from app import create_app, db
from models import Tweet # モデルのインポート
from scheduler import start_scheduler
import os

app = Flask(__name__)
app = create_app()
uri = os.getenv("DATABASE_URL")  # HerokuのデータベースURLを取得
if uri.startswith("postgres://"):
      uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

client = create_api_v2()  # v2 APIクライアントの作成

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        
        if action == 'ツイート':
            try:
                post_tweet_v2(client, tweet_content)
                message = "ツイートが投稿されました"
            except Exception as e:
                message = f"エラーが発生しました: {e}"
        elif action == '保存':
            new_tweet = Tweet(content=tweet_content)
            db.session.add(new_tweet)
            db.session.commit()
            message = "ツイートを保存しました"
        elif action == '削除':
            tweet_id = request.form.get('tweet_id')
            tweet_to_delete = Tweet.query.get(tweet_id)
            if tweet_to_delete:
                db.session.delete(tweet_to_delete)
                db.session.commit()
                message = "ツイートを削除しました"

    tweets = Tweet.query.order_by(Tweet.created_at.desc()).all()
    return render_template('index.html', tweets=tweets, message=message)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_scheduler(app, client)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))






