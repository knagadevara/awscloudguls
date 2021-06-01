1. Create a Role named CWA_Admin with below policies in IAM
            
            CloudWatchAgentAdminPolicy
            AmazonEC2RoleforSSM
            AmazonSSMFullAccess
            AmazonInspectorFullAccess
2. The newly created IAM role has to be attached to all the EC2 instances where AWS-Inspector does a 'scan and report'.   
3. Create an SNS topic named **vulInspector** for AWSInspectorNotifications
4. Give access to AWSInspectorUser by editing topic policy.
    1. check the sns-topic 
    2. In 'Basic View' select 'Only These AWS Users' radio button.
    3. Give the user-arn belonging tho that region [These users are owned and managed by AWS]
    4. Click 'Update Policy'
5. Create a Role for the Lambda Function
         
         roleArn=$(aws iam create-role --role-name LambdaInspector
         --assume-role-policy-document file://LambdaInspectorRole.json
         --query "Role"."Arn" | tr -d \\\\"[:space:][])
      1. Attach the policy InspectorDescribeFinding.json to role LambdaInspector
   
               aws iam put-role-policy --role-name LambdaInspector \\
               --policy-name InspectorDescribeFinding \\
               --policy-document file://InspectorDescribeFinding.json
         
      2. Attach policy to role LambdaInspector
         
               aws iam put-role-policy --role-name LambdaInspector \\
               --policy-name AmazonSSMFullAccess
               aws iam put-role-policy --role-name LambdaInspector \\
               --policy-name AWSLambdaBasicExecutionRole
   
6. Write a Lambda function which will be triggered by the SNS-Topic **It will invoke SSM-Agent to write into ec2 through 'sessions manager'/'run command'**
   1. Attach the role LambdaInspector to Lambda-Function.
   2. Set up a trigger and point it to the SNS topic which was earlier created by providing it arn.
    
7. Go to AWS-Inspector Dashboard [uses SSM to interact with EC2]
    1.  Targets [set of EC2 instances on which scan needs to be run.]
        1. Create-New-Target:
            1.  Name: 'Distinctive Identifier'
            2.  All Instances: mark unchecked
            3.  Use Tags: 'add key and value'
            4.  Install Agent: mark checked
            5.  SAVE
    2.  Templates [the security vulnerability which needs to scanned for.]
        1.  Create-New-Template:
            1.  Name: 'Distinctive Identifier'
            2.  Target Name: 'The above created Target Name'
            3.  Rules Packages: 'Select All Options'
            4.  Duration: 'Run Full Hour'
            5.  SNS Topic: 
                1.  Name: 'Give the details of Topic which was created earlier'
                2.  Event: 'Finding Reported'
            6.  Assessment Schedule: 'As per the production requirements and change windows'
    3.  Runs [instance of aws-inspector's executions which use the template to scan the targets]