#!/usr/bin/python3

import boto3 , botostubs

## Listing the bucket Names and the files within

## Creating an S3 resource which has a higher abstraction and contol, returns an object.
s3 = boto3.resource('s3')
for buck_t in s3.buckets.all():
    bucket = s3.Bucket(buck_t.name)
    print("\n Bucket Name: {0}\t Bucket Creation: {1}\n".format(buck_t.name, bucket.creation_date))
    for obj in bucket.objects.all():
        print(" \t{0} \tsize:{1}".format(obj.key , obj.size))

## Creating a 'S3' client to get the names of the bucket and their creation date. Returns a direct string.
s3Client: botostubs.S3 = boto3.client('s3')
bucketList = s3Client.list_buckets()['Buckets']
for bucketName in bucketList:
    print("\n Bucket Name: {0}\t Bucket Creation: {1}\n".format(bucketName['Name'], bucketName['CreationDate']))