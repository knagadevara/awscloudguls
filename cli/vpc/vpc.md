-----------------
#### VPC Build-UP
-----------------

It is a good Practice to save the details of user profile to a variable.

		profile_region='--profile admin --region us-east-1'

- create a vpc, save the vpcid and create tags

		vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 $profile_region --query "Vpc"."VpcId" | tr -d \"[:space:][]) && aws ec2 create-tags --resources $vpc_id --tags Key=Name,Value=DC-MAIN-VPC $profile_region

