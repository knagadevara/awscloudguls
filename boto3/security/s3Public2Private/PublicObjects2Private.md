-   Aim is to identify and move all the public s3 buckets to private.

1.  Create an S3 bucket that will contain the private objects

        aws s3 mb s3://<account_number>-private-bucket
2.  Create an S3 bucket for CloudTrail trail logging and reporting
    
        aws s3 mb s3://<account-number>-object-scan-log-trail
3.  Apply the policy on the created logging bucket

        aws s3api put-bucket-policy \
        --bucket s3://<account-number>-object-scan-log-trail \
        --policy file://private_bucket_policy.json
4.  Create a new CloudTrail trail and feed the logging bucket

        aws cloudtrail create-trail \
        --name my-object-level-s3-trail \
        --s3-bucket-name s3://<account-number>-object-scan-log-trail
5.  Start the newly created trail

        aws cloudtrail start-logging \
        --name my-object-level-s3-trail
6.  Create an event selector to log all the s3 object-level create-read-write events to s3://<account-number>-object-scan-log-trail through CloudTrail.

        aws cloudtrail put-event-selector \
        --trial-name  my-object-level-s3-trail \
        --event-selectors file://event_selector.json
    
7.  Create an event pattern recognition rule which logs all the 'Put' events on S3 through CLoudTrail
    
        patternRuleArn=$(aws events put-rule --name ruleS3EventRemediate \
        --event-pattern file://eventPatternRule.json \
        --query "RuleArn" | tr -d \\"[:space:][])
8.  Create IAM policy to give the Lambda function to perform action on S3 and standard CloudWatch Logging.
    1. Creating a Role from trust_policy
            
            roleArn=$(aws iam create-role --role-name AllowLogsAndS2ACL \
            --assume-role-policy-document file://LambdaTrustPolicy.json \
            --query "Role"."Arn" | tr -d \"[:space:][])
    2.  Creating policy to allow Lambda to get/put objects on s3://<account_number>-private-bucket
            
            aws iam put-role-policy --role-name AllowLogsAndS2ACL \
            --policy-name AllowLogsAndS2ACL --policy-document file://GetPutObject.json
    3.  Zip the Lambda Code
    
            zip -r9 s3Public2Private.zip lambda_function.py
    4.  Create a lambda function and upload it to AWS.
    
            lambdaArn=$(aws lambda create-function --function-name s3Public2Private \
            --zip-file file://s3Public2Private.zip \
            --role $roleArn \
            --handler lambda_function.lambda_handler \
            --runtime python3.7 \
            --environment Variables={BUCKET_NAME=s3://<account_number>-private-bucket} \
            --query "FunctionArn" | tr -d \\"[:space:][])
9.  Add permissions to CloudwatchEvents to invoke the lambda_function when a pattern is matched
            
            aws lambda add-permission --function-name s3Public2Private \
            --statement-id AllowCloudwatchEventsToInvoke \
            --action 'lambda:InvokeFunction' \
            --principal events.amazonaws.com \
            --source-arn $patternRuleArn
10. Point the Lambda function as a target to the PatternRule
    
            aws events put-targets \
            --rule ruleS3EventRemediate \
            --targets Id=1,Arn=$lambdaArn
11. Test the function by uploading an object into S3.

        aws s3api put-object-acl \
        --bucket s3://<account_number>-private-bucket
        --key myS3File
        --acl public-read