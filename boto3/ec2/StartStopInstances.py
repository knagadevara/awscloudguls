#!/usr/bin/python3

import boto3
import json

## Making a client
ec2client = boto3.client('ec2')

## Getting regions
response = ec2client.describe_regions()
regionNames = [region['RegionName'] for region in response['Regions']]
for region in regionNames:
    ec2_resource = boto3.resource('ec2' , region_name=region)
    ## To print instances which are running
    #instances = ec2_resource.instances.filter( Filters=[{ 'Name' : 'instance-state-name' , 'Values': ['running']  }] )
    instances = ec2_resource.instances.all()
    print(region)
    print("-----" * 6)
    for instance in instances:
        print("\tInstanceId: {0}".format(instance.id))
        print("\t\tInstanceType: {0}".format(instance.instance_type))
        print("\t\tPlacement: {0}".format(instance.placement))
        print("\t\tPresentState: {0}".format(instance.state))
        print("\t\tBlockDevices: {0} , VolumeID: {1}".format(instance.block_device_mappings[0]['DeviceName'] , instance.block_device_mappings[0]['Ebs']['VolumeId']))
        print("\t\tCPU: {0}".format(instance.cpu_options))
        print("\t\t STOPPING INSTANCE" , instance.stop())
        print("\n\n")
