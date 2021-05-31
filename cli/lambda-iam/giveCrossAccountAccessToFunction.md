
-	Gives access to a user from a different account to invoke a lambda-function in a host account [applies the given profile name], needs to be run with ownership on the function-host account.

		aws lambda add-permission \
		--function-name <lambda-function-name> \
		--statement-id <unique-descriptive-string-about-this-function> \
		--action 'lambda:InvokeFunction' \
		--principal 'arn:aws:iam::<account-no>:user/<user-name>' \
		--region us-west2 \
		--profile sadmin

-	To check the affect/details of the policies attached to the lambda-function
		
		aws lambda get-policy \
		--function-name <lambda-function-name> \
		--region <region> \
		--profile <sadmin>

-	To remove the policy attached to the lambda-function.

		aws lambda remove-permission \
                --function-name <lambda-function-name> \
                --statement-id <unique-descriptive-string-about-this-function> \
                --region <region> \
                --profile <sadmin>

-	To invoke the lambda-function from a newly created account[profile]

		aws lambda invoke \
                --function-name 'arn:aws:lambda:<region>:<account-no>:function:<function-name>' \
		--payload '{ "Event-Key-Name" : "Value" }' \
		--invocation-type RequestResponse \
                --region <region> \
                --profile <sadmin> \
		cmd_call_output.txt


		
