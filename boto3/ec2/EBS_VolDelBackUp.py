#!/usr/bin/python3


import argparse
import botostubs, boto3 , botocore
# import json
# import time

#### Helpful Content to display
argDescription="Takes the Tag:(Key,Value) and stores the snapshot of the instance. Please be noted that the instance will be shut down in this process."
generalDescription="Request you to provide the below as arguments for the file: \n\t %(prog)s --tag-key <foo> --tag-value <bar>"
epilog="And that's how you'd run a the script"

#### Initialization of Parser to collect Data
parseme = argparse.ArgumentParser(prog='StartStopInstances' ,  description=argDescription, usage=generalDescription , epilog=epilog )
parseme.add_argument('--tag-key', '-k', type=str, help='Takes the Tag:(Key)', required=True)
parseme.add_argument('--tag-value', '-v', type=str, help='Takes the Tag:(Value)', required=True)
arguments =  parseme.parse_args()

#### Creating a Session [ really to get the details of the present user details and accountID]
# MySession = boto3.session.Session(profile_name='admin')
# ec2regionNames = MySession.get_available_regions('ec2')
# print(type(ec2regionNames))
# print(ec2regionNames)
#### Get account id
aws_sts : botostubs.STS = boto3.client('sts')# type: botostubs to get the deature of autocomplete
account_id = aws_sts.get_caller_identity().get('Account')

regionNames = ['eu-north-1', 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

for region in regionNames:
    print("\n\n")
    ec2_client_region: botostubs.EC2 = boto3.client('ec2' , region_name=region)
    snapshots = ec2_client_region.describe_snapshots(OwnerIds=[account_id])["Snapshots"]
    print("REGION: {0}".format(region))
    print("--- --- " * 6)
    if snapshots and len(snapshots) != 1:
        print("\n\t Retaining the newest Snapshot and deleting rest, found: {0}".format(len(snapshots)))
        ## Sorting based on Time
        snapshots.sort(key=lambda x: x['StartTime'])
        ## Deleting the most recent snap drom the list by making a slice
        snapshots = snapshots[:-1]
        for snapshot in snapshots:
            print("\n\t\t Deleting Snapshot: {0}".format(snapshot))
            try:
                ec2_client_region.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            except Exception as e:
                print(e)
                continue
    else:
        print("\n\n\t Skipping, Not deleting the Primary or No Snapshot Found")