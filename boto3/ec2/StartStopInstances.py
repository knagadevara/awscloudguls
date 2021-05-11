#!/usr/bin/python3


import argparse
import boto3
import sys


#### Helpful Content to display
argDesc='Starts or Stops EC2 instances in all the regions'
gen1="Request you to provide the below as arguments for the file: \n\t %(prog)s <stop/start>"
epilog="And that's how you'd run a the script"
stateCODE =  0

#### Initialization of Parser to collect Data
parseme = argparse.ArgumentParser(prog='StartStopInstances' ,  description=argDesc, usage=gen1 , epilog=epilog )
parseme.add_argument('--InstanceAction', '-a', type=str, help='Takes only stop/start', required=True)
arguments =  parseme.parse_args()


def getSTATUS(instance):
    global stateCODE
    if arguments.InstanceAction == "start":
        stateCODE = 16
        return instance.start
    elif arguments.InstanceAction == "stop":
        stateCODE = 80
        return instance.stop
    elif arguments.InstanceAction == "terminate":
        stateCODE = 48
        return instance.terminate
    else:
        sys.exit(gen1)


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
    print("--- --- " * 6)
    for instance in instances:
        print("\n\n")
        print("\tInstanceId: {0}".format(instance.id))
        print("\t\tInstanceType: {0}".format(instance.instance_type))
        print("\t\tPlacement: {0}".format(instance.placement))
        PresentState=instance.state
        print("\t\tPresentState: {0}".format(PresentState))
        runME = getSTATUS(instance)
        if PresentState['Code'] != stateCODE:
            runME()
            print("\t\tExecuting {0}".format(arguments.InstanceAction))
        else:
            print("\t\tAlready in {0} state".format(PresentState))
