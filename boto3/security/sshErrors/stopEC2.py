import boto3
import botostubs
import json


ec2: botostubs.EC2 = boto3.client('ec2')


def lambda_handler(event, context):
    sns_event = event['Records'][0]['Sns']
    json_msg = json.loads(sns_event['Message'])

    # Extract ec2 instanceID
    instance_id = json_msg['AlarmDescription'].split()[-1]
    ec2.stop_instances(InstanceIds = [instance_id])
    print("Stopped Instance {0}".format(instance_id))
