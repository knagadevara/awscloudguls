#!/usr/bin/env bash

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

	# By Author: knagadevara
	# Date: Tue Apr 13 14:53:26 IST 2021
	# Scripting Language: bash
	# Copyright:: 2021, The Authors, All Rights Reserved. 

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

aws='/usr/local/bin/aws'
aws_profile='admin'
aws_region='us-east-1'
CurrentDate=$(date +%Y%m%d)
OutputFormat="--profile ${aws_profile} --region ${aws_region} --output json"
TempLoc='/tmp/TempCertDoc.json'

AllCertList=$($aws acm list-certificates $OutputFormat)
CertARN=$(echo ${AllCertList} | jq .CertificateSummaryList[].CertificateArn | tr -d \")

declare -a HostArrays=()
declare -a SYSData=()

for crt_arn in ${CertARN}
 do
	$aws acm describe-certificate --certificate-arn ${crt_arn} $OutputFormat > $TempLoc.$CurrentDate
	DomainName=$(cat $TempLoc | jq .Certificate.DomainName | tr -d \" )
	CertExpiry=$(cat $TempLoc | jq .Certificate.NotAfter | tr -d \"- | cut -d'T' -f1)
	CertValidityNum=$(($CertExpiry - $CurrentDate))

	if [[ $CertValidityNum -lt 30 ]]
	then
		HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName:$DomainName - Validity:$CertExpiry - State: EXP\" }  , ")
	else
		HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName:$DomainName - Validity:$CertExpiry - State: ALV\" }  , ")
	fi

 done

## Outputting a Single Value
SYSData=$(  echo -n "{ \"data\" : [ $HostArrays [] ]}" )
echo -ne ${SYSData} | jq '.'

rm -rf $TempLoc.$CurrentDate
