import boto3
import os
import logging
from botocore.exceptions import ClientError

class S3Manager:
    def __init__(self, bucket_name, secret_key, access_key, s3_region):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=s3_region
        )
        self.bucket_name = bucket_name
    
    def download_file(self, key: str) -> str:
        local_path = f"/tmp/{os.path.basename(key)}"
        try:
            with open(local_path, "wb") as f:
                self.s3_client.download_fileobj(self.bucket_name, key, f)
            return local_path
        except ClientError as e:
            if e.response['Error']['Code'] == '403':
                print(f"Permission error (403) downloading file {key} from S3: {e}")
            else:
                print(f"Error downloading file {key} from S3: {e}")
            raise

    def upload_file(self, file_content: str, s3_key: str) -> str:
        try:
            self.s3_client.put_object(Body=file_content, Bucket=self.bucket_name, Key=s3_key)
            return f"s3://{self.bucket_name}/{s3_key}"
        except ClientError as e:
            print(f"Error uploading file {s3_key} to S3: {e}")
            raise
