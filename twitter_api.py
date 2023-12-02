import tweepy
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



def create_api_v2():
    # 環境変数から認証情報を取得
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')


    # Tweepyの新しいクライアントクラスを使用
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return client

def post_tweet_v2(client, text, media_id=None):
    """
    ツイートを投稿する。画像がある場合はmedia_idを使用する。
    """
    try:
        if media_id:
            # 画像付きツイートを投稿
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            # テキストのみのツイートを投稿
            response = client.create_tweet(text=text)
        logger.info(f"Tweet posted successfully: {response.data['id']}")
        return response
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        raise e


def upload_media_v1(image_path):
    try:
        auth = tweepy.OAuthHandler(os.environ.get('CONSUMER_KEY'), os.environ.get('CONSUMER_SECRET'))
        auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))
        api_v1 = tweepy.API(auth)

        media = api_v1.media_upload(image_path)
        logger.info(f"Media uploaded successfully: {media.media_id_string}")
        return media.media_id_string
    except Exception as e:
        logger.error(f"Error uploading media: {e}")
        raise e

def post_tweet_with_media(client, text, media_id):
    try:
        response = client.create_tweet(text=text, media_ids=[media_id])
        logger.info(f"Tweet posted successfully with media ID: {media_id}")
        return response
    except Exception as e:
        logger.error(f"Error posting tweet with media: {e}")
        raise e
