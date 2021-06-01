import boto3
import botostubs
import json

ssmClient: botostubs.SSM = boto3.client('ssm')
inspectorClient: botostubs.Inspector = boto3.client('inspector')


def lambda_handler(event, context):
    print(json.dump(event))

    # getting the message sent from Inspector
    inspector_message = event['Record'][0]['Sns']['Message']
    # getting the type of inspector notification example 'scan_started' or 'scan_completed' or 'findings_reported'
    inspector_notification_type = json.loads(inspector_message)['event']
    print("Notification Type: {0}".format(inspector_notification_type))

    if inspector_notification_type == 'FINDING_REPORTED':
        inspector_finding_arn = json.loads(inspector_message)['finding']
        print('Inspector:FindingReported ARN: {0}'.format(inspector_finding_arn))
        complete_response = inspectorClient.describe_findings(
            findingArns = inspector_finding_arn,
            locale = 'EN_US')
        describe_findings_response = complete_response['findings'][0]
        if (describe_findings_response['title'] == "Unsupported Operating System or Version"
            or describe_findings_response['title'] == "No potential security issues found") \
                and describe_findings_response['service'] != 'Inspector' \
                and describe_findings_response['assetType'] != 'ec2-Instance':
            print("Skipping Irrelevant Inspector:FindingReported")
            return 1
        else:
            report_cve_id = ''
            for cve_attribute in describe_findings_response['attributes']:
                if cve_attribute['key'] == 'CVE_ID':
                    report_cve_id = cve_attribute['value']
                    break
                else:
                    print('CVE_ID NotFound')
            print('CVE_ID: {0}'.format(report_cve_id))
            ec2_instance_id = describe_findings_response['assetAttributes']['agentId']
            if ec2_instance_id.startswith('i-'):
                print("InstanceId: {0}".format(ec2_instance_id))
            else:
                print("InvalidInstanceId: {0}".format(ec2_instance_id))

            # query SSM for information about Instance
            instance_filter_list = [{'key': 'InstanceIds', 'valueSet': [ec2_instance_id]}]
            describe_instance_information_response = ssmClient.describe_instance_information(
                MaxResults = 50,
                InstanceInformationFilterList = instance_filter_list
            )
            ec2_instance_information = describe_instance_information_response['InstanceInformationList'][0]
            SSMPingStatus = ec2_instance_information['PingStatus']
            OSPlatformType = ec2_instance_information['PlatformType']
            OSPlatformVersion = ec2_instance_information['PlatformVersion']
            OSPlatformName = ec2_instance_information['PlatformName']

            if SSMPingStatus == 'Online' and OSPlatformType == 'Linux':
                print("SSMPingStatus: {0}".format(SSMPingStatus))
                print("OSPlatformType: {0}".format(OSPlatformType))

                if OSPlatformName.startswith('Ubuntu') \
                        or OSPlatformName.startswith('debian'):
                    print("Supported Linux Distribution")
                    print("DEBIAN based OSPlatformVersion: {0}".format(OSPlatformVersion))
                    print("DEBIAN basedOSPlatformName: {0}".format(OSPlatformName))
                    commandPatchLine = "apt-get update -qq -y && apt-get upgrade -y"
                elif OSPlatformName.startswith('Centos') \
                        or OSPlatformName.startswith('Amazon Linux'):
                    print("Supported Linux Distribution")
                    print("REDHAT based OSPlatformVersion: {0}".format(OSPlatformVersion))
                    print("REDHAT based OSPlatformName: {0}".format(OSPlatformName))
                    commandPatchLine = "yum  update -q -y && yum upgrade -y"
                else:
                    print("Unsupported Linux Distribution")
                    print("OSPlatformVersion: {0}".format(OSPlatformVersion))
                    print("OSPlatformName: {0}".format(OSPlatformName))
                    return 1
                print("Command to be Executed:\n\t{0}".format(commandPatchLine))
                send_command_response = ssmClient.send_command(
                    InstanceIds = [ec2_instance_id],
                    DocumentName = 'AWS-RunShellScript',
                    Parameters = {'commands': commandPatchLine},
                    Comment = 'Lambda-Function is performing an auto patch on '
                              'ec2_instance_id: {0} based on CVE_ID:{1}'.format(ec2_instance_id , report_cve_id)
                )
                print("SSM send_command response:\n\t{0}".format(send_command_response))
            else:
                print("SSM Agent is not reachable, please check if the instance is UP and running "
                      "Also, check if the SSM agent service is Active and Enabled."
                      "Or this could also be a case where the Operating System is not LINUX")
    else:
        print('Skipping notification that is not Inspector:FindingReported')
        return 1