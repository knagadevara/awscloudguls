AIM: Automating Tagging and lock the permissions of the resources which are created by a specific user with the help of CloudTrail, CloudWatchEvents and LambdaFunction.

-   A user while creating an instance will invoke the below EC2-API calls.
        
            RunInstance
            CreateVolume
            CreateImage
            CreateSnapshot

-  These API-Call events can be captured  by configuring rules in EventBridge/CloudWatchEvents.
-  The applied rules can recognize patterns and act as a trigger to kickoff Lambda-Function.
-  The Lambda-Function will tag the instances with user/owner-id details, 
    which later can be used to restrict other users from conducting any operations on it.
   

#### Steps
1.  IAM Related
        
    1.  Attach the OwnerDemarkRestrictionPolicy IAM policy to group.
        
            aws iam put-group-policy --group-name DeveloperOperation \
            --policy-name OwnerDemarkRestrictionPolicy \
            --policy-document file://OwnerDemarkRestrictionPolicy.json  \
            --description "Restricts operations on instances which are created by Owner of the resource"
    
    3.  Create a TrustRole for Lambda-Function.
    
            roleArn=$(aws iam create-role --role-name LambdaCreateTag \
            --assume-role-policy-document file://LambdaCreateTagTrustRole.json \
            --query "Role"."Arn" | tr -d \"[:space:][])
        
    3.  Attach an inline Policy to Lambda role
    
            aws iam  put-role-policy --role-name LambdaCreateTag \
            --policy-name LambdaCreateTags
            --policy-document file://CreateTags.json  \
            --description "Lambda-Function Creates Tags on EC2 instances"

2. Zip the lambda function [EC2OwnerTag.py] with other related packages.
   
        mv EC2OwnerTag.py lambda_function.py && zip -r9 EC2OwnerTag.zip lambda_function.py
    
3. Create the Lambda function.
   
            lambdaArn=$(aws lambda create-function --function-name EC2OwnerTag \
            --zip-file file://EC2OwnerTag.zip \
            --role $roleArn \
            --handler lambda_function.lambda_handler \
            --runtime python3.7 \
            --query "FunctionArn" | tr -d \\"[:space:][])

4. Create an EventPattern Rule
   
        patternRuleArn=$(aws events put-rule --name TriggerLambdaOnEC2Event \
        --event-pattern file://eventPatternRule.json \
        --query "RuleArn" | tr -d \\"[:space:][])  

5. Point the Lambda function as a target to the PatternRule
    
            aws events put-targets \
            --rule TriggerLambdaOnEC2Event \
            --targets Id=1,Arn=$lambdaArn
    
6. Add permissions to CloudwatchEvents to invoke the lambda_function when a pattern is matched
            
            aws lambda add-permission --function-name EC2OwnerTag \
            --statement-id AllowCloudwatchEventsToInvoke \
            --action 'lambda:InvokeFunction' \
            --principal events.amazonaws.com \
            --source-arn $patternRuleArn
