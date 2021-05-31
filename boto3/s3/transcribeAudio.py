import boto3
import botostubs

s3Client = boto3.client('s3')   # type: botostubs.S3
transcribeClient: botostubs.TranscribeService = boto3.client('transcribe')


def lambda_handler(event, context):

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        object_url = "https://s3.amazonaws.com/{0}/{1}".format(source_bucket, key)
        s3_response = transcribeClient.start_transcription_job(
            TranscriptionJobName = key,
            Media = {'MediaFileUri': object_url},
            MediaFormat='mp3'
        )
        print(s3_response)
