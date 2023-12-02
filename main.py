from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2, upload_media_v1
from app import create_app, db
from models import Tweet
from gcs_client import GCSClient
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app = create_app()
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
                    # 画像を一時的に保存
                    filename = secure_filename(image.filename)
                    image_path = os.path.join('/tmp', filename)  # 適切な一時ファイルパスを選択
                    image.save(image_path)

                    # 画像をTwitter API v1.1を使用してアップロード
                    media_id = upload_media_v1(client, image_path)

                    # ツイートを投稿
                    post_tweet_v2(client, tweet_content, media_id)

                    # 一時ファイルを削除
                    os.remove(image_path)
                else:
                    post_tweet_v2(client, tweet_content)
                message = "ツイートが投稿されました"
            except Exception as e:
                message = f"エラーが発生しました: {e}"
        elif action == '保存':
            if image:
                extension = os.path.splitext(image.filename)[1].lstrip('.')
                unique_filename = gcs_client.upload_file(image, extension)
                image_url = gcs_client.get_file_url(unique_filename)
                new_tweet = Tweet(content=tweet_content, image_url=image_url)
            else:
                new_tweet = Tweet(content=tweet_content)
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
