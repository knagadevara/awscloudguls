#!/usr/bin/python3


import argparse
import boto3
import json

session = boto3.Session()
client = session.client('acm')
response = client.list_certificates()
certDetails=response['CertificateSummaryList'][0]
print(certDetails)
