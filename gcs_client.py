# gcs_client.py
import os
import json
from google.cloud import storage
from google.oauth2 import service_account

class GCSClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
        )
        self.client = storage.Client(credentials=credentials, project=os.environ.get('GOOGLE_CLOUD_PROJECT'))
        self.bucket = self.client.bucket(os.environ.get('GCS_BUCKET'))

    def upload_file(self, file_stream, file_name):
        """
        ファイルをGCSバケットにアップロードする
        """
        blob = self.bucket.blob(file_name)
        blob.upload_from_string(file_stream.read(), content_type=file_stream.content_type)

    def get_file_url(self, file_name):
        """
        GCSバケット内のファイルのURLを取得する
        """
        blob = self.bucket.blob(file_name)
        return blob.public_url
