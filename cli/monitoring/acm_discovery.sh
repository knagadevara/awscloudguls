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
declare -a EXP_data=()
declare -a INC_data=()
declare -a PRS_data=()
declare -a ALV_data=()

for crt_arn in ${CertARN}
 do
        aws acm describe-certificate --certificate-arn ${crt_arn} $OutputFormat > $TempLoc.$CurrentDate
        DomainName=$(cat $TempLoc.$CurrentDate | jq .Certificate.DomainName | tr -d \" | sed 's/*/wildcard/' )
        CertExpiry=$(cat $TempLoc.$CurrentDate | jq .Certificate.NotAfter | tr -d \"- | cut -d'T' -f1)
        ExpiredDate=$(date --date @${CertExpiry} +%Y%m%d)
        CertValidityNum=$(( ($(date --date="$ExpiredDate" +%s) - $(date --date="$CurrentDate" +%s) )/(60*60*24) ))
	echo $CertValidityNum
        if [[ $CertValidityNum -lt 0 ]]
        then
                HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName_$DomainName\" }  , ")
                EXP_data+="DomainName:$DomainName Validity:$ExpiredDate $CertValidityNum:EXP"

        elif [[ $CertValidityNum -lt 10 ]]
        then

                HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName_$DomainName\" }  , ")
                INC_data+="DomainName:$DomainName Validity:$ExpiredDate $CertValidityNum:INC"

        elif [[ $CertValidityNum -lt 60 ]]
        then

                HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName_$DomainName\" }  , ")
                PRS_data+="DomainName:$DomainName Validity:$ExpiredDate $CertValidityNum:PRS"

        else

                HostArrays+=$(  echo -en "{ \"{#DOMAINNAME}\" : \"DomainName_$DomainName\" }  , ")
                ALV_data+="DomainName:$DomainName Validity:$ExpiredDate $CertValidityNum:ALV"
        fi

 done


## Outputting a Single Value

function send_discovery_data() {

        SYSData=$(  echo -n "{ \"data\" : [ $HostArrays [] ]}" )
        echo -ne ${SYSData} | jq '.'
}

function call_sender() {
        echo $EXP_data > /tmp/EXP_data.$CurrentDate
        echo $ALV_data > /tmp/ALV_data.$CurrentDate
        echo $PRS_data > /tmp/PRS_data.$CurrentDate
        echo $ALV_data > /tmp/ALV_data.$CurrentDate
}

function cleanup_files() {

        rm -rf $TempLoc.$CurrentDate
        rm -rf /tmp/EXP_data.$CurrentDate
        rm -rf /tmp/ALV_data.$CurrentDate
        rm -rf /tmp/PRS_data.$CurrentDate
        rm -rf /tmp/ALV_data.$CurrentDate
}

call_sender
