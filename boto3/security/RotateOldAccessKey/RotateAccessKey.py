import boto3
import botostubs
from os import environ
from datetime import datetime, timezone
from botocore.exceptions import ClientError, ConnectionError, ConnectTimeoutError

# Particular's of Email
AWS_EMAIL_REGION = environ['AWS_EMAIL_REGION']
AWS_EMAIL_FROM = environ['AWS_EMAIL_FROM']  # This has to be a SES pre-verified address.
AWS_EMAIL_TO = environ['AWS_EMAIL_TO']
IAM_MAX_KEY_AGE = environ['IAM_MAX_KEY_AGE']

# Connection to the Service
iam_resource: botostubs.IAM = boto3.client('iam')
ses_client: botostubs.SES = boto3.client('ses', region = AWS_EMAIL_REGION)


def days_old(my_time):
    now = datetime.now(timezone.utc)
    age_in_days = now - my_time
    return age_in_days


def send_email_notification(aws_email_to, user_name, age_in_days, user_access_key_id):
    email_subject_data = "Your AWS IAM Key Deactivated"
    email_body_data = f"UserName: {user_name} with " \
                      f"UserAccessKeyId: {user_access_key_id} " \
                      f"has been suspended automatically as it is {age_in_days} days old"
    try:
        send_email_response = ses_client.send_email(
            Source = AWS_EMAIL_FROM,
            Destination = {'ToAddresses': [aws_email_to]},
            Message = {
                'Subject': {'Data': email_subject_data},
                'Body': {'Text': {'Data': email_body_data}}
            })
    except ClientError as ce:
        print(ce.response['Error']['Message'])
    except ConnectTimeoutError as cte:
        print(cte)
    except ConnectionError as cr:
        print(cr)
    else:
        print(f"Notified user through email, response: {send_email_response['MessageId']}")


def lambda_handler(event, context):

    # Using Paginator read extensive responses
    list_users_paginator = iam_resource.get_paginator('list_users')

    for list_users_response in list_users_paginator.paginate():
        for listed_user in list_users_response['Users']:
            user_name = listed_user['UserName']
            list_access_keys_response = iam_resource.list_access_keys(UserName = user_name)
            for user_access_key in list_access_keys_response['AccessKeyMetadata']:
                user_access_key_id = user_access_key['AccessKeyId']
                key_creation_date = user_access_key['CreateDate']
                print(f"UserName: {user_name}, "
                      f"UserAccessKeyId: {user_access_key_id}, "
                      f"KeyCreationDate: {key_creation_date}")

                user_access_key_age = days_old(key_creation_date)
                if user_access_key_age < IAM_MAX_KEY_AGE:
                    continue
                else:
                    print(f"UserName: {user_name}, "
                          f"UserAccessKeyId: {user_access_key_id}, "
                          f"KeyCreationDate: {user_access_key_age} is EXPIRED")
                    update_access_key_response = iam_resource.update_access_key(
                        UserName = user_name,
                        AccessKeyId = user_access_key_id,
                        Status = 'Inactive')
                    send_email_notification(AWS_EMAIL_TO, user_name, user_access_key_age, user_access_key_id)
