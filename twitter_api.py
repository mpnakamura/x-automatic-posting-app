import tweepy

def create_api_v2():
    # 環境変数から認証情報を取得
    consumer_key = "FcN1YDVv0LLvybBvIqsEeJrzj"
    consumer_secret = "fPBBijNwPxSmaJm3sIz2Jsos86eWC1KxSMmMrYQtmNFkKz2MeG"
    access_token = '2540071454-YjRWbjYDZnT5BP8ateLFZJr69kjkvasaUyrEgI0'
    access_token_secret = 'lkayy64jpJu0na78I6NwSJqLmMhwpRVK2Ijpqr8KPDAY0'

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

