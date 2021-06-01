import boto3
import botostubs
import os


s3Client: botostubs.S3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']


def is_object_private(s3_bucket_name , s3_object_name_key):
    """Checks if supplied s3 object is private"""
    # Gets all the data related to object ACL
    s3_object_acl = s3Client.get_object_acl(Bucket = s3_bucket_name , Key = s3_object_name_key)

    # Private object should ideally have only one Grant which belongs to object owner
    # object is public in cases like
    # if it is more than 1 then the
    # if the owner and grant id are not match
    s3_object_owner_id = s3_object_acl['Owner']['ID']
    s3_object_grant_id = s3_object_acl['Grants'][0]['Grantee']['ID']
    if len(s3_object_acl['Grants']) > 1 or s3_object_owner_id != s3_object_grant_id:
        return False
    else:
        return True


def make_object_private(s3_bucket_name , s3_object_name_key):
    """Makes the bucket private"""
    s3Client.put_object_acl(Bucket = s3_bucket_name, Key = s3_object_name_key , ACL = 'private')
    print("\t\t s3://{0}/{1} is now private".format(s3_bucket_name, s3_object_name_key))


def lambda_handler(event, context):
    """Gets the details from event and process it, maipulates s3-acl if they are public, makes them private"""
    s3_bucket_name = event['detail']['requestParameters']['bucketName']
    # ensuring that we are operating on the bucket we are supposed to
    if s3_bucket_name != BUCKET_NAME:
        print("Doing Nothing for {0}".format(s3_bucket_name))
        return
    # Get Key Name from the event which is the name of the s3-object
    s3_object_name_key = event['detail']['requestParameters']['key']

    if is_object_private(s3_bucket_name = s3_bucket_name , s3_object_name_key = s3_object_name_key):
        print("\t\t s3://{0}/{1} is already private".format(s3_bucket_name, s3_object_name_key))
    else:
        make_object_private(s3_bucket_name = s3_bucket_name , s3_object_name_key = s3_object_name_key)