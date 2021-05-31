-	1.a. Create the role from a file and get ARN

		roleArn=$(aws iam create-role --role-name vpcFlowLogsRole \
		--assume-role-policy-document file://assumeRoleTrustPolicy.json \
		--query "Role"."Arn" | tr -d \"[:space:][])


-	1.b. Attaching policy to a the created role

		aws iam put-role-policy --role-name vpcFlowLogsRole \
		--policy-name vpcFlowLogsPolicy \
		--policy-document file://vpcFlowLogsIamRole.json


-	1.c. When the lambda-function is invoked from the cli, with an 'aws:awn' as a parameter then "lambdaFlowLogPolicy.json" would assume that role while writing logs behalf of vpc.
-	1.d. Create a pattern recognition rule in CloudWatchEvents which will get triggered whenever a new VPC gets created, which can be traced through CloudTrail 'CreateVpc' event.
