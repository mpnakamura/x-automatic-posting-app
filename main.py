from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2
from app import create_app, db
from models import Tweet
from gcs_client import GCSClient
from utils import generate_unique_filename
import os

app = Flask(__name__)
app= create_app()
client = create_api_v2()  # Twitter API v2クライアントの作成
gcs_client = GCSClient()  # GCSクライアントの作成

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    tweet_to_delete = None

    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        image = request.files.get('image')  # 画像ファイルの取得

        if action == 'ツイート':
            try:
                if image:
                    # 画像をGCSにアップロードし、URLを取得
                    extension = os.path.splitext(image.filename)[1].lstrip('.')
                    unique_filename = generate_unique_filename(extension)
                    gcs_client.upload_file(image, unique_filename)
                    image_url = gcs_client.get_file_url(unique_filename)

                    # 画像のURLをツイートの本文に含める
                    tweet_content_with_image = f"{tweet_content} {image_url}"
                    post_tweet_v2(client, tweet_content_with_image)
                else:
                    # 画像なしでツイートを投稿
                    post_tweet_v2(client, tweet_content)

                message = "ツイートが投稿されました"
            except Exception as e:
                message = f"エラーが発生しました: {e}"
        elif action == '保存':
            image_url = None
            if image:
                # 画像がある場合のみimage_urlを設定
                extension = os.path.splitext(image.filename)[1].lstrip('.')
                unique_filename = generate_unique_filename(extension)
                gcs_client.upload_file(image, unique_filename)
                image_url = gcs_client.get_file_url(unique_filename)

            new_tweet = Tweet(content=tweet_content, image_url=image_url)
            db.session.add(new_tweet)
            db.session.commit()
            message = "ツイートを保存しました"

        if action == '削除':
            tweet_id = request.form.get('tweet_id')
            tweet_to_delete = Tweet.query.get(tweet_id)
            if tweet_to_delete:
                db.session.delete(tweet_to_delete)
                db.session.commit()
                message = "ツイートを削除しました"
            else:
                message = "削除するツイートが見つかりませんでした"

    tweets = Tweet.query.order_by(Tweet.created_at.desc()).all()
    return render_template('index.html', tweets=tweets, message=message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
