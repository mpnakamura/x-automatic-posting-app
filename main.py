from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2, post_tweet_with_media
from app import create_app, db
from models import Tweet
from gcs_client import GCSClient
from scheduler import start_scheduler
import os
from flask_migrate import Migrate

app= Flask(__name__)
app = create_app()
migrate = Migrate(app, db)

client = create_api_v2()  # v2 APIクライアントの作成
gcs_client = GCSClient()  # GCSクライアントの作成

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        image = request.files.get('image')  # 画像ファイルの取得

        if action == 'ツイート':
            try:
                if image:
                    # 画像をGCSにアップロードし、URLを取得
                    file_name = "path/to/save/image"
                    gcs_client.upload_file(image, file_name)
                    image_url = gcs_client.get_file_url(file_name)

                    # 画像付きでツイートを投稿
                    post_tweet_with_media(client, tweet_content, image_url)
                else:
                    # 画像なしでツイートを投稿
                    post_tweet_v2(client, tweet_content)
                
                message = "ツイートが投稿されました"
            except Exception as e:
                message = f"エラーが発生しました: {e}"
        elif action == '保存':
            new_tweet = Tweet(content=tweet_content, image_url=image_url if image else None)
            db.session.add(new_tweet)
            db.session.commit()
            message = "ツイートを保存しました"
        # ... その他の処理 ...

    tweets = Tweet.query.order_by(Tweet.created_at.desc()).all()
    return render_template('index.html', tweets=tweets, message=message)

# ... その他のコード ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_scheduler(app, client)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))






