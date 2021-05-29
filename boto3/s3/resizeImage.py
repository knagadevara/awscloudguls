#!/usr/bin/python3
import boto3
import os, tempfile
from PIL import Image
import botostubs

DEST_BUCKET = os.environ['DEST_BUCKET']
SIZE = 128 , 128
s3Client: botostubs.S3 = boto3.client('s3')

def genreate_thumb(sourcePath, destPath):
    print("Generating Thumbnail from {0}".format(sourcePath))
    with Image.open(sourcePath) as img:
        img.thumbnail(SIZE)
        img.save(destPath)

def lambda_handler(event , context):
    for record in event['Records']:
        print(record)
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        thumb = 'thumb-' + key
        with tempfile.TemporaryDirectory() as tempDIR:
            download_path = os.path.join(tempDIR , key)
            upload_path = os.path.join(tempDIR , thumb)
            s3Client.download_file(Bucket=source_bucket , Key=key , Filename=download_path)
            genreate_thumb(download_path , upload_path)
            s3Client.upload_file(Filename=upload_path , Bucket=DEST_BUCKET , Key=thumb)
        print("Saved Image")