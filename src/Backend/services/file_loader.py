import os
import boto3
from fastapi import UploadFile, HTTPException


class FileLoader:
    @staticmethod
    async def load_from_local(file_path: str):
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        with open(file_path, "rb") as f:
            content = f.read()

        return content, os.path.basename(file_path)

    @staticmethod
    async def load_from_upload(file: UploadFile):
        content = await file.read()
        return content, file.filename

    @staticmethod
    async def load_from_s3(bucket: str, key: str, access_key: str, secret_key: str):
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )

            response = s3.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()

            return content, key
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading from S3: {str(e)}")