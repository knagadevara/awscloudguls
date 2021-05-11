---------
##### EC2
---------

- Creating an ec2 instance and associate it with created vpc

	aws ec2 run-instances --image-id  ami-09d19e919d57453f8  --count 1 --instance-type t2.micro --key-name KarthikAdmin  --security-group-ids  $ssh_sec_grp --subnet-id  $subnet_id --associate-public-ip-address $profile_region

- To disable delete on termination on instances root volume

	touch mapping.json
	echo '[{ "DeviceName" : "/dev/xvda" , "Ebs" : { "DeleteOnTermination" : false}}]' > mapping.json

	aws ec2 modify-instance-attribute --instance-id  <instance_id> --block-device-mappings file://mapping.json


- if the termination is erroring out, use the below command in aws-cli

	aws ec2 modify-instance-attribute --instance-id  <instance_id>  --no-disable-api-termination