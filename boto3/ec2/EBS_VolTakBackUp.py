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


def StartInstance(statCODE, instance):
    while statCODE != 16:
        time.sleep(25)
        instance.start()
        print("\t\tStarting Instance:{0}".format(instance.id))
        return instance.state

def StopInstance( statCODE , instance):
    while statCODE != 80:
        instance.stop()
        time.sleep(60)
        print("\t\tStopping Instance:{0}".format(instance.id))
        return instance.state

def TakeSnapShot(stateCODE , instance):
    if stateCODE != 80:
        PresentState=StopInstance(stateCODE , instance)
        TakeSnapShot(PresentState['Code'] , instance)
    else:
        print("\t\tAlready in {0} state".format(stateCODE))
        for volume in instance.volumes.all():
            descriptionSNAP = "Taking Backup of BlockDevices: {0} , VolumeID: {1}".format(instance.block_device_mappings[0]['DeviceName'] , volume.id)
            print("\t\t{0}".format(descriptionSNAP))
            snapshot = volume.create_snapshot(Description=descriptionSNAP, \
                TagSpecifications=[ { 'ResourceType': 'snapshot' , \
                'Tags': [ \
                {'Key': 'InstanceId', 'Value': instance.id }, \
                {'Key': 'VolumeId', 'Value': volume.id }, \
                {'Key': 'BlockDeviceName', 'Value': instance.block_device_mappings[0]['DeviceName'] } , \
                {'Key': 'SnapshotTime' , 'Value' : time.strftime("%a, %d %b %Y %H:%M:%S +0000 %Z" , time.gmtime()) } \
                 ] } ] )
            print("\t\tSnapshot Completed for snapshot_id: {0}".format(snapshot.id))
            StartInstance(instance.state['Code'] , instance)

         
## Making a client
ec2client = boto3.client('ec2')

## Getting regions
response = ec2client.describe_regions()
regionNames = [region['RegionName'] for region in response['Regions']]
for region in regionNames:
    ec2_resource = boto3.resource('ec2' , region_name=region)
    instances = ec2_resource.instances.filter(Filters=[{ 'Name' : "tag:{0}".format(arguments.tag_key) , 'Values': [ arguments.tag_value ]  }])
    print(region)
    print("--- --- " * 6)
    for instance in instances.all():
        print("\n\n")
        print("\tInstanceId: {0}".format(instance.id))
        print("\t\tInstanceType: {0}".format(instance.instance_type))
        print("\t\tPlacement: {0}".format(instance.placement))
        print("\t\tCPU: {0}".format(instance.cpu_options))
        PresentState=instance.state
        print("\t\tPresentState: {0}".format(PresentState))
        TakeSnapShot(PresentState['Code'] , instance)
