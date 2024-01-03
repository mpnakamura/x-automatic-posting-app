from flask import Flask, render_template, request, redirect, url_for,flash, session
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
app.secret_key = os.environ.get('SECRET_KEY')
client = create_api_v2()  # Twitter API v2クライアントの作成
gcs_client = GCSClient()  # GCSクライアントの作成


USERNAME = os.environ.get('MY_APP_USERNAME')
PASSWORD = os.environ.get('MY_APP_PASSWORD')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています。')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))


    message = ""
    tweet_to_delete = None

    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        images = request.files.getlist('image')  # 複数の画像ファイルを取得


        if action == 'ツイート':
            try:
                media_ids = []
                for image in images:
                    logger.info("画像がアップロードされました")

                    # 画像を一時的に保存
                    filename = secure_filename(image.filename)
                    image_path = os.path.join('/tmp', filename)
                    image.save(image_path)
                    logger.info(f"画像を一時保存しました: {image_path}")

                    # 画像をTwitter API v1.1を使用してアップロード
                    media_id = upload_media_v1(image_path)
                    media_ids.append(media_id)
                    logger.info(f"Media IDを取得しました: {media_id}")

                    # 一時ファイルを削除
                    os.remove(image_path)

                if media_ids:
                    # 画像付きツイートを投稿
                    post_tweet_v2(client, tweet_content, media_ids)
                    logger.info("画像付きツイートを投稿しました")
                else:
                    # 画像なしでツイートを投稿
                    post_tweet_v2(client, tweet_content)
                    logger.info("画像なしでツイートを投稿しました")

                message = "ツイートが投稿されました"
            except Exception as e:
                logger.error(f"エラーが発生しました: {e}")
                message = f"エラーが発生しました: {e}"

        if action == '保存':
            images = request.files.getlist('image')  # 複数の画像ファイルを取得
            image_urls = []

        for image in images:
             # 画像の拡張子を取得し、一意のファイル名を生成
            extension = os.path.splitext(image.filename)[1].lstrip('.')
            unique_filename = gcs_client.upload_file(image, extension)
        
                # GCSにアップロードした画像のURLを取得しリストに追加
            image_url = gcs_client.get_file_url(unique_filename)
            image_urls.append(image_url)

            # 画像URLリストをカンマ区切りの文字列に変換
            image_urls_str = ','.join(image_urls)

    # 新しいツイートをデータベースに保存
            new_tweet = Tweet(content=tweet_content, image_url=image_urls_str)
            db.session.add(new_tweet)
            db.session.commit()
            message = "ツイートを保存しました"


        if action == '削除':
            tweet_id = request.form.get('tweet_id')
            tweet_to_delete = Tweet.query.get(tweet_id)
            if tweet_to_delete:
        # GCSに保存されている画像も削除
                if tweet_to_delete.image_url:
            # カンマ区切りの画像URLをリストに変換
                    image_urls = tweet_to_delete.image_url.split(',')
                    for url in image_urls:
                        gcs_client.delete_file(url)
                        logger.info(f"GCSに保存されている画像を削除しました: {url}")

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
