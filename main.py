from flask import Flask, render_template, request, redirect, url_for
from twitter_api import create_api_v2, post_tweet_v2, upload_media_v1
from app import create_app, db
from models import Tweet
from gcs_client import GCSClient
import os
from werkzeug.utils import secure_filename
import logging
from scheduler import start_scheduler



# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                    logger.info("画像がアップロードされました")

                    # 画像を一時的に保存
                    filename = secure_filename(image.filename)
                    image_path = os.path.join('/tmp', filename)  # 適切な一時ファイルパスを選択
                    image.save(image_path)
                    logger.info(f"画像を一時保存しました: {image_path}")

                    # 画像をTwitter API v1.1を使用してアップロード
                    media_id = upload_media_v1(image_path)
                    logger.info(f"Media IDを取得しました: {media_id}")

                    # ツイートを投稿
                    post_tweet_v2(client, tweet_content, media_id)
                    logger.info("画像付きツイートを投稿しました")

                    # 一時ファイルを削除
                    os.remove(image_path)
                    logger.info("一時ファイルを削除しました")
                else:
                    post_tweet_v2(client, tweet_content)
                    logger.info("画像なしでツイートを投稿しました")

                message = "ツイートが投稿されました"
            except Exception as e:
                logger.error(f"エラーが発生しました: {e}")
                message = f"エラーが発生しました: {e}"


        if action == '保存':
            if image:
                # 画像の拡張子を取得し、一意のファイル名を生成
                extension = os.path.splitext(image.filename)[1].lstrip('.')
                unique_filename = gcs_client.upload_file(image, extension)
                
                # GCSにアップロードした画像のURLを取得
                image_url = gcs_client.get_file_url(unique_filename)
                
                # 新しいツイートをデータベースに保存
                new_tweet = Tweet(content=tweet_content, image_url=image_url)
                db.session.add(new_tweet)
                db.session.commit()
                message = "ツイートを保存しました"
            else:
                new_tweet = Tweet(content=tweet_content)
                db.session.add(new_tweet)
                db.session.commit()
                message = "ツイートを保存しました"


        if action == '削除':
            tweet_id = request.form.get('tweet_id')
            tweet_to_delete = Tweet.query.get(tweet_id)
            if tweet_to_delete:
                # GCSに保存されている画像も削除
                if tweet_to_delete.image_url:
                    gcs_client.delete_file(tweet_to_delete.image_url)
                    logger.info(f"GCSに保存されている画像を削除しました: {tweet_to_delete.image_url}")
                db.session.delete(tweet_to_delete)
                db.session.commit()
                message = "ツイートを削除しました"
            else:
                message = "削除するツイートが見つかりませんでした"

                return redirect(url_for('index'))

    tweets = Tweet.query.order_by(Tweet.created_at.desc()).all()
    return render_template('index.html', tweets=tweets, message=message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        start_scheduler(app, client)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
