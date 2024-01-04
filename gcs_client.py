import os
import json
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
import uuid


class GCSClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
        )
        self.client = storage.Client(credentials=credentials, project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
        self.bucket = self.client.bucket(os.environ.get('GCS_BUCKET'))

    def generate_unique_filename(self, extension):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = uuid.uuid4().hex
        return f"{timestamp}_{random_str}.{extension}"

    def upload_file(self, file_stream, extension):
        """
        ファイルをGCSバケットにアップロードする
        """
        unique_filename = self.generate_unique_filename(extension)
        blob = self.bucket.blob(unique_filename)
        blob.upload_from_string(file_stream.read(), content_type=file_stream.content_type)
        return unique_filename

    def get_file_url(self, file_name):
        """
        GCSバケット内のファイルのURLを取得する
        """
        blob = self.bucket.blob(file_name)
        return blob.public_url
    
    def delete_files(self, file_urls):
        """
        GCSバケットから複数のファイルを削除する
        """
        for file_url in file_urls:
            # ファイル名をURLから抽出
            file_name = file_url.split('/')[-1]

            # ファイルを削除
            blob = self.bucket.blob(file_name)
            blob.delete()

