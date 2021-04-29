#!/usr/bin/env bash

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

        # By Author: knagadevara
        # Date: Tue Apr 13 14:53:26 IST 2021
        # Scripting Language: bash
        # Copyright:: 2021, The Authors, All Rights Reserved.

#--- --- --- --- --- --- --- --- --- ---##--- --- --- --- --- --- --- --- --- ---#

zab_trap_key='ssl_cert_ok'
zab_trap_host=$(uname -n)
zabbix_sender='/usr/bin/zabbix_sender'
zab_psudo_host='SSL_TESTING_PSUDO_HOST'
zab_out="${1}"

#$zabbix_sender -z "${zab_trap_host}" -s "${zab_psudo_host}" -k "${zab_trap_key}" -o "${zab_out}"
echo $zab_out
