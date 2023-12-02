from flask import Flask, render_template, request
from twitter_api import create_api_v2, post_tweet_v2, post_tweet_with_media,upload_media
from app import create_app, db
from models import Tweet
from gcs_client import GCSClient
from scheduler import start_scheduler
import os


app= Flask(__name__)
app = create_app()


client = create_api_v2()  # v2 APIクライアントの作成
gcs_client = GCSClient()  # GCSクライアントの作成

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    image_url = None  # image_urlの初期化を関数の外で行う

    if request.method == 'POST':
        action = request.form.get('action')
        tweet_content = request.form.get('tweet')
        image = request.files.get('image')  # 画像ファイルの取得

        if action == 'ツイート':
            try:
                if image:
                    # 画像をGCSにアップロードし、URLを取得
                    file_name = "path/to/save/image"  # 適切なファイル名を指定
                    gcs_client.upload_file(image, file_name)
                    image_url = gcs_client.get_file_url(file_name)

                    # 画像のメディアIDを取得
                    media_id = upload_media(client, image)  # upload_mediaはメディアIDを返す関数

                    # 画像付きでツイートを投稿
                    post_tweet_with_media(client, tweet_content, media_id)
                else:
                    # 画像なしでツイートを投稿
                    post_tweet_v2(client, tweet_content)
                
                message = "ツイートが投稿されました"
            except Exception as e:
                message = f"エラーが発生しました: {e}"
        elif action == '保存':
            # 画像がある場合のみimage_urlを設定
            if image:
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


# ... その他のコード ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_scheduler(app, client)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))






