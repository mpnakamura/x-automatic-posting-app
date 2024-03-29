from apscheduler.schedulers.background import BackgroundScheduler
from models import Tweet,Image
from app import db
from twitter_api import post_tweet_v2, upload_media_v1, post_tweet_with_media
import requests
import os
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        # 一時ファイルとして画像を保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        raise Exception(f"Failed to download image from {image_url}")

def tweet_job(app, client):
    with app.app_context():
        # 最新で未投稿のツイートを取得
        tweet = Tweet.query.filter_by(posted=False).order_by(Tweet.created_at.desc()).first()
        if tweet:
            try:
                # 関連する画像を取得
                images = Image.query.filter_by(tweet_id=tweet.id).all()
                media_ids = []

                if images:
                    # 各画像に対して処理
                    for image in images:
                        image_path = download_image(image.url)
                        media_id = upload_media_v1(image_path)
                        media_ids.append(media_id)
                        os.remove(image_path)

                    # 画像付きツイートを投稿
                    post_tweet_v2(client, tweet.content, media_ids)
                else:
                    # テキストのみのツイート
                    post_tweet_v2(client, tweet.content)

                tweet.posted = True
                db.session.commit()
            except Exception as e:
                logger.error(f"Error in scheduled tweet job: {e}")
        else:
            # 全てのツイートが投稿された場合、投稿フラグをリセット
            Tweet.query.update({Tweet.posted: False})
            db.session.commit()



def start_scheduler(app, client):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: tweet_job(app, client), trigger="interval", minutes=160)
    scheduler.start()
