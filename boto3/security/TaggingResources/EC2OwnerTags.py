import boto3
import botostubs
import json

ec2Client: botostubs.EC2.Ec2Resource = boto3.resource('ec2')


def lambda_handler(event, context):
    print("Event: \n{0}".format(json.dumps(event)))
    # Extract all the EC2 related resources like EC2instance_ID, AMI, EBS [Volumes and Snapshots], ENI...

    ec2_resource_ids = []

    try:
        # Gathering required Data
        region = event['region']
        detail = event['detail']
        event_name = detail['eventName']
        arn = detail['userIdentity']['arn']
        principal = detail['userIdentity']['principalID']
        user_type = detail['userIdentity']['type']
        if user_type == 'IAMUser':
            aws_user = detail['userIdentity']['userName']
        else:
            aws_user = principal.split(': ')[1]
        print("ARN: {0}\nUser: {1}\nRegion: {2}".format(arn, aws_user, region))
        print("PrincipalID: {0}".format(principal))
        print("EventName: {0}".format(event_name))
        print("Detail: {0}".format(detail))

        if not detail['responseElements']:
            print("No ResponseElement found")
            if detail['errorCode']:
                print("ErrorCode: {0}".format(detail['errorCode']))
            if detail['errorMessage']:
                print("ErrorMessage: {0}".format(detail['errorMessage']))
            return False
        else:
            # Dealing with all the event Names
            if event_name == 'CreateVolume':
                ec2_resource_ids.append(detail['responseElements']['volumeId'])
                print(ec2_resource_ids)
            elif event_name == 'RunInstances':
                instance_items = detail['responseElements']['instancesSet']['items']
                for item in instance_items:
                    ec2_resource_ids.append(item['instanceId'])
                print("No of Instances: {0}\nInstances: {1}".format(len(ec2_resource_ids), ec2_resource_ids))
                all_triggered_instances = ec2Client.instances.filter(InstanceIds=ec2_resource_ids)
                for instance in all_triggered_instances:
                    for volumes in instance.volumes.all():
                        ec2_resource_ids.append(volumes.id)
                    for enet_interface in instance.network_interfaces.all():
                        ec2_resource_ids.append(enet_interface.id)
            elif event_name == 'CreateImage':
                ec2_resource_ids.append(detail['responseElements']['imageId'])
                print(ec2_resource_ids)
            elif event_name == 'CreateSnapshot':
                ec2_resource_ids.append(detail['responseElements']['snapshotId'])
                print(ec2_resource_ids)
            else:
                print('Not Supported')

            if ec2_resource_ids:
                for ec2id in ec2_resource_ids:
                    print("Tagging the resource: {0}".format(ec2id))
                    ec2Client.create_tags(Resources=[ec2id],
                                          Tags=
                                          [
                                              {'Key': 'Owner', 'Value': aws_user},
                                              {'Key': 'PrincipalId', 'Value': principal}
                                          ])
                    print("Tagged")
                print("Tagging Complete!")
                return True

    except Exception as e:
        print(e)


