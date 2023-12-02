from apscheduler.schedulers.background import BackgroundScheduler
from models import Tweet
from app import db
from twitter_api import post_tweet_v2, upload_media_v1, post_tweet_with_media

def tweet_job(app, client):
    with app.app_context():
        tweet = Tweet.query.filter_by(posted=False).order_by(Tweet.created_at.desc()).first()
        if tweet:
            if tweet.image_url:
                # 画像付きツイート
                media_id = upload_media_v1(client, tweet.image_url)
                post_tweet_with_media(client, tweet.content, media_id)
            else:
                # テキストのみのツイート
                post_tweet_v2(client, tweet.content)
            tweet.posted = True
            db.session.commit()
        else:
            # 全てのツイートが投稿された場合、投稿フラグをリセット
            Tweet.query.update({Tweet.posted: False})
            db.session.commit()

def start_scheduler(app, client):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: tweet_job(app, client), trigger="interval", minutes=45)
    scheduler.start()
