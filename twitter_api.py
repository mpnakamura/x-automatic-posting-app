import tweepy
import os

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

def post_tweet_v2(client, text):
    # Twitter API v2を使用してツイートを投稿
    response = client.create_tweet(text=text)
    return response

