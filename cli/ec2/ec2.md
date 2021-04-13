---------
##### EC2
---------

- Creating an ec2 instance and associate it with created vpc

	aws ec2 run-instances --image-id ami-8c1be5f6 --count 1 --instance-type t2.micro --key-name KarthikAdmin  --security-group-ids  $ssh_sec_grp --subnet-id  $subnet_id --associate-public-ip-address $profile_region
