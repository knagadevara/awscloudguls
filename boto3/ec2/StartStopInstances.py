#!/usr/bin/python3


import argparse
import boto3
import json


#### Helpful Content to display
argDesc='Starts or Stops EC2 instances in all the regions'
gen1="Request you to provide the below as arguments for the file: \n\t %(prog)s <stop/start>"
epilog="And that's how you'd run a the script"

#### Initialization of Parser to collect Data
parseme = argparse.ArgumentParser(prog='StartStopInstances' ,  description=argDesc, usage=gen1 , epilog=epilog )
parseme.add_argument('--InstanceAction', '-a', type=str, help='Takes only stop/start/terminate', required=True)
arguments =  parseme.parse_args()

def getSTATUS():
    if arguments.InstanceAction == "start":
        print("\t\tSTARTING")
        return instance.start
    elif arguments.InstanceAction == "stop":
        print("\t\tSTOPPING")
        return instance.stop
    elif arguments.InstanceAction == "terminate":
        print("\t\tTERMINATING")
        return instance.terminate
    else:
        print(gen1)



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
        PresentState=instance.state
        print("\t\tPlacement: {0}".format(PresentState))
        print("\t\tBlockDevices: {0} , VolumeID: {1}".format(instance.block_device_mappings[0]['DeviceName'] , instance.block_device_mappings[0]['Ebs']['VolumeId']))
        print("\t\tCPU: {0}".format(instance.cpu_options))
        runME = getSTATUS
        runME()
        print("\n\n")
