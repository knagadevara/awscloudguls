import boto3
import botostubs
import os
from botocore.exceptions import ClientError

# Environment Variable to be created in lambda-function:wq!
ROLE_ARN = os.environ['ROLE_ARN']

ec2Client: botostubs.EC2 = boto3.client('ec2')
logsClient: botostubs.CloudWatchLogs = boto3.client('logs')


def lambda_handler(event, context):

    try:
        # Extracting VPC_ID Logs
        vpc_id = event['detail']['responseElements']['vpc']['vpcId']
        # Contains all the network interfaces
        flow_log_groups = 'VPCFlowLogs' + vpc_id
        print("VPC: {0}".format(vpc_id))
        try:
            create_log_group_response = logsClient.create_log_group(logGroupName=flow_log_groups)
        except ClientError as ce:
            print("{0} flow log group already exists".format(flow_log_groups))

        # Check if flow logs on VPC is already enabled.
        describe_flow_logs_response = ec2Client.describe_flow_logs(
            Filter=[
                {
                    'Name': 'resource-id',
                    'Values': [vpc_id]
                }
            ]
        )
        if len(describe_flow_logs_response['FlowLogs']) > 0:
            print('VPC Flow logs are ENABLED')
        else:
            print('VPC Flow logs are DISABLED, CREATING!')
            """Now the role which has been created earlier will be passed on to the new flow log group, which after 
            assuming it can create logs in CloudWatchLogs. """
            create_flow_logs_response = ec2Client.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType='VPC', # Can also be a network interface
                TrafficType='ALL', # can be filtered further
                LogGroupName=flow_log_groups,
                DeliverLogsPermissionArn = ROLE_ARN
            )
            print('VPC Flow logs are Created and ENABLING NOW: {0}'.format(create_flow_logs_response['FlowLogs'][0]))
    except Exception as e:
        print('ERROR {0}'.format(e))