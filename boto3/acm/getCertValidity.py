import boto3
import datetime
import hashlib
import json

regionNames = [ 'us-east-1' , 'us-west-2' , 'eu-west-1' ]
dayToday = datetime.datetime.now().replace(tzinfo=None)
topic_name = ''
CertDictionary = {}
snsClient = boto3.client(service_name ='sns' , region_name = 'us-west-2' )

#### Get account id
aws_sts = boto3.client('sts')
account_id = aws_sts.get_caller_identity().get('Account')

def hashMeUp(domainName , certFingerPrint):
    StringValue = domainName + " " + certFingerPrint
    hashed_StringValue = hashlib.md5(StringValue.encode("utf-8"))
    return "{0}".format(hashed_StringValue.hexdigest())

def lambda_handler(event, lambda_context):
    for region in regionNames:
        acmclient = boto3.client(service_name ='acm' , region_name = region)
        CertificateSummaryList = acmclient.list_certificates( CertificateStatuses=[ 'PENDING_VALIDATION' , 'ISSUED' , 'INACTIVE' ,'EXPIRED' , 'VALIDATION_TIMED_OUT' ,'REVOKED', 'FAILED' ] )['CertificateSummaryList']
        if CertificateSummaryList:
            for acmCert in CertificateSummaryList:
                CertDetails = acmclient.describe_certificate(CertificateArn=acmCert['CertificateArn'])
                CertValidityDay = CertDetails['Certificate']['NotAfter'].replace(tzinfo=None)
                CertRemainingDays = CertValidityDay - dayToday
                message_key = "{0}".format(hashMeUp( acmCert['DomainName'] , CertDetails['Certificate']['Serial']))
                CertDictionary[message_key] = {}
                if CertRemainingDays.days < 0:
                    CertDictionary[message_key]['AlertMessage'] = "EXPIRED DomainName: {0}  Certificate is expired {1} in region {2}".format(acmCert['DomainName'] , CertRemainingDays , region)
                    CertDictionary[message_key]['AlertSeverity'] = 1
                elif CertRemainingDays.days < 60:
                    CertDictionary[message_key]['AlertMessage'] = "AboveTo DomainName: {0}  Certificate will expire in {1} in region {2}".format(acmCert['DomainName'] , CertRemainingDays , region)
                    CertDictionary[message_key]['AlertSeverity'] = 2
                else:
                    print("ValidDomainName: {0}  Certificate will expire in {1}".format(acmCert['DomainName'] , CertRemainingDays))

    ## Sending HashKey as message_key
    if CertDictionary.keys():
        for HashKey in CertDictionary.keys():
            CertPublishToSNS( CertDictionary[HashKey]['AlertMessage'] , CertDictionary[HashKey]['AlertSeverity'] , snsClient , region)

def CertPublishToSNS( description, alert_severity , snsClient, region):
    snsClient = snsClient
    payload = { "Notification": [{   \
     "severity" : alert_severity,  \
     "description": description,   \
     "additional_info" : "AWS ACM Cert in region {0}".format(region)  } ] }
    sns_response = snsClient.publish(
    Message = json.dumps(payload),
    TopicArn='arn:aws:sns:us-west-2:{0}:{1}'.format(account_id , topic_name),
    Subject='ACM Notification',
    MessageAttributes={
        'ACM Notification': {
            'DataType': 'String',
            'StringValue': 'Certificate Validity'
        }
    })
    return sns_response