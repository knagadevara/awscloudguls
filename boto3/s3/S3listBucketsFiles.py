#!/usr/bin/python3

import boto3

s3 = boto3.resource('s3')
for buck_t in s3.buckets.all():
    bucket = s3.Bucket(buck_t.name)
    print("\n Bucket Name: {0}\t Bucket Creation: {1}\n".format(buck_t.name, bucket.creation_date))
    for obj in bucket.objects.all():
        print(" \t{0} \tsize:{1}".format(obj.key , obj.size))
