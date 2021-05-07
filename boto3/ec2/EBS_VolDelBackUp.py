#!/usr/bin/python3


import argparse
import boto3
import json
import time


#### Helpful Content to display
argDescription="Takes the Tag:(Key,Value) and stores the snapshot of the instance. Please be noted that the instance will be shut down in this process."
generalDescription="Request you to provide the below as arguments for the file: \n\t %(prog)s --tag-key <foo> --tag-value <bar>"
epilog="And that's how you'd run a the script"

#### Initialization of Parser to collect Data
parseme = argparse.ArgumentParser(prog='StartStopInstances' ,  description=argDescription, usage=generalDescription , epilog=epilog )
parseme.add_argument('--tag-key', '-k', type=str, help='Takes the Tag:(Key)', required=True)
parseme.add_argument('--tag-value', '-v', type=str, help='Takes the Tag:(Value)', required=True)
arguments =  parseme.parse_args()

#### Get account id
sts_client = boto3.client('sts').get_caller_identity().

## Making a client
ec2client = boto3.client('ec2').get('Acount')

## Getting regions
response = ec2client.describe_regions()
regionNames = [region['RegionName'] for region in response['Regions']]
for region in regionNames:
    ec2_resource = boto3.resource('ec2' , region_name=region)
