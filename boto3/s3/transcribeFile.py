import json
import boto3
import botostubs
import os
import urllib.request

BUCKET_NAME = os.environ['DestinationBucket']

s3_client: botostubs.S3 = boto3.client('s3')
transcribe_client: botostubs.TranscribeService = boto3.client('transcribe')


def lambda_handler(event, context):
    job_name = event['detail']['TranscriptionJobName']
    job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    transcribe_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(transcribe_uri)
    content = urllib.request.urlopen(transcribe_uri).read().decode('UTF-8')
    data = json.loads(content)
    text = data['result']['transcripts'][0]['transcript']
    s3_object = s3_client.Object(BUCKET_NAME , job_name , '-asrOutput.txt')
    s3_object.put(Body=text)
