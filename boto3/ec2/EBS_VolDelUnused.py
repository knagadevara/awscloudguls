#!/usr/bin/python3


import boto3 , botostubs

#regionNames = ['eu-north-1', 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
regionNames = ['us-east-1', 'us-east-2']
for region in regionNames:
    ec2Client: botostubs.EC2 = boto3.resource(service_name='ec2' , region_name=region)
    withVolumes = ec2Client.volumes.filter( Filters=[{ 'Name' : 'status' , 'Values': ['available'] }] )
    if withVolumes:
        for volDel in withVolumes:
            VolObj = ec2Client.Volume(volDel.volume_id)
            print("Deleting Volume Id: {0} Size: {1}".format( volDel.volume_id , volDel.size) )
            VolObj.delete()


