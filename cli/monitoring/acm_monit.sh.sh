#!/usr/bin/env bash

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

	# By Author: knagadevara
	# Date: Tue Apr 13 14:53:26 IST 2021
	# Scripting Language: bash
	# Copyright:: 2021, The Authors, All Rights Reserved. 

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

zab_trap_key="SSL_CERT_CHECKER_ACM"
zab_trap_host=$(uname -n)
zab_trap_port="10051"
zabbix_sender='/usr/bin/zabbix_sender'
zab_psudo_host='SSL_TESTING_PSUDO_HOST'
aws='/usr/local/bin/aws'
CurrentDate=$(date +%Y%m%d)
OutputFormat='--output json'
TempLoc='/tmp/TempCertDoc.json'

AllCertList=$($aws acm list-certificates $OutputFormat)
CertARN=$(echo ${AllCertList} | jq .CertificateSummaryList[].CertificateArn | tr -d \")

for crt_arn in ${CertARN}
 do
	$aws acm describe-certificate --certificate-arn ${crt_arn} $OutputFormat > $TempLoc.$CurrentDate
	DomainName=$(cat $TempLoc | jq .Certificate.DomainName | tr -d \" )
	CertExpiry=$(cat $TempLoc | jq .Certificate.NotAfter | tr -d \" | cut -d'T' -f1 | tr -d '-')
	CertValidityNum=$(($CertExpiry - $CurrentDate))

	if [[ $CertValidityNum -lt 30 ]]
	then
		$zabbix_sender -z $zab_trap_host -p $zab_trap_port -s $zab_psudo_host -k $zab_trap_key -o "DomainName:$DomainName - Validity:$CertExpiry - State: EXP"

	else
		$zabbix_sender -z $zab_trap_host -p $zab_trap_port -s $zab_psudo_host -k $zab_trap_key -o "DomainName:$DomainName - Validity:$CertExpiry - State: ALV"
	fi

 done

rm -rf $TempLoc.$CurrentDate
