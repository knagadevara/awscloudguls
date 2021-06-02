AIM: Notify the users whose AccessKey is older than 60 days via email and deactivate it.

1.  IAM
    1.  Create a TrustRole for Lambda-Function.
    
            roleArn=$(aws iam create-role --role-name LambdaRotateAccessKeyRole \
            --assume-role-policy-document file://LambdaRotateAccessKeyRole.json \
            --query "Role"."Arn" | tr -d \"[:space:][]}
        
    2.  Attach an inline Policy to Lambda role
    
            aws iam  put-role-policy --role-name LambdaRotateAccessKeyRole \
            --policy-name RotateAccessKeyPolicy
            --policy-document file://RotateAccessKeyPolicy.json  \
            --description "Lambda-Function Creates Tags on EC2 instances"
    
2.  Verify 'AWS_EMAIL_FROM' email address.
    
        aws ses verify-email-identity --email-address sender@example.com
        (or)
        aws sesv2 create-email-identity --email-identity sender@example.com

3. Zip the lambda function [RotateAccessKey.py] with other related packages.
   
        mv RotateAccessKey.py lambda_function.py && zip -r9 RotateAccessKey.zip lambda_function.py
    
4. Create the Lambda function.
   
            lambdaArn=$(aws lambda create-function --function-name RotateAccessKey \
            --zip-file file://RotateAccessKey.py.zip \
            --role $roleArn \
            --handler lambda_function.lambda_handler \
            --runtime python3.7 \
            --timeout 90 \
            --environment Variables={AWS_EMAIL_REGION=useast-1, \
                            AWS_EMAIL_FROM=sender@example.com, \
                            AWS_EMAIL_TO=reciever@example.com, \
                            IAM_MAX_KEY_AGE=60}
            --query "FunctionArn" | tr -d \\"[:space:][])

5. Create an EventPattern Rule
   
        patternRuleArn=$(aws events put-rule --name RotateAccessKeyOldEvent \
        --schedule-expression  "rate(5 days)" \
        --query "RuleArn" | tr -d \\"[:space:][])  

6. Point the Lambda function as a target to the PatternRule
    
            aws events put-targets \
            --rule RotateAccessKeyOld \
            --targets Id=1,Arn=$lambdaArn
    
7. Add permissions to CloudwatchEvents to invoke the lambda_function when a pattern is matched
            
            aws lambda add-permission --function-name RotateAccessKey \
            --statement-id AllowCloudwatchEventsToInvoke \
            --action 'lambda:InvokeFunction' \
            --principal events.amazonaws.com \
            --source-arn $patternRuleArn