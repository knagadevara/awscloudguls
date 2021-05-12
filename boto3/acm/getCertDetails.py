#!/usr/bin/python3

import botostubs, boto3
import datetime
import hashlib

regionNames = [ 'us-east-1' , 'us-west-2' , 'eu-west-1' ]
dayToday = datetime.datetime.now().replace(tzinfo=None)

def hashMeUp(domainName , certFingerPrint):
    StringValue = domainName + " " + certFingerPrint
    hashed_StringValue = hashlib.md5(StringValue.encode("utf-8"))
    return "{0}".format(hashed_StringValue.hexdigest())

for region in regionNames:
    acmclient: botostubs.ACM = boto3.client( service_name='acm' , region_name = region )
    CertificateSummaryList = acmclient.list_certificates( CertificateStatuses=[ 'PENDING_VALIDATION' , 'ISSUED' , 'INACTIVE' ,'EXPIRED' , 'VALIDATION_TIMED_OUT' ,'REVOKED', 'FAILED' ] )['CertificateSummaryList']
    if CertificateSummaryList:
        for acmCert in CertificateSummaryList:
            CertificateArn =  acmCert['CertificateArn']
            CertDomainName =  acmCert['DomainName']
            CertDetails = acmclient.describe_certificate(CertificateArn=CertificateArn)
            CertValidityDay = CertDetails['Certificate']['NotAfter'].replace(tzinfo=None)
            CertSerial = CertDetails['Certificate']['Serial']
            CertRemainingDays = CertValidityDay - dayToday           
            if CertRemainingDays.days < 0:
                print("DomainName: {0}  Certificate is expired {1}".format(CertDomainName , CertRemainingDays))
            elif CertRemainingDays.days < 60:
                print("DomainName: {0}  Certificate will expire in {1}".format(CertDomainName , CertRemainingDays))
            else:
                print("all is good")