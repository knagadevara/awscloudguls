-----------------
#### VPC Build-UP
-----------------

It is a good Practice to save the details of user profile to a variable.

		profile_region='--profile admin --region us-east-1'

- Create a vpc, save the vpcid and create tags

		vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 $profile_region --query "Vpc"."VpcId" | tr -d \"[:space:][]) && aws ec2 create-tags --resources $vpc_id --tags Key=Name,Value=DC-MAIN-VPC $profile_region

- Create a Subnet and attach it to the VPC

		subnet_id=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24 --availability-zone us-east-1a $profile_region --query Subnet.SubnetId | tr -d \"[:space:][]{})  && aws ec2 create-tags --resources $subnet_id --tags Key=Name,Value=AZ-EUA-MAIN $profile_region

- Create IGW

		igw_id=$(aws ec2 create-internet-gateway $profile_region --query InternetGateway.InternetGatewayId | tr -d \"[:space:][]{} ) && aws ec2 create-tags --resources $igw_id --tags Key=Name,Value=OutRouteMAIN $profile_region

- Attach IGW with VPC

		aws ec2 attach-internet-gateway --internet-gateway-id $igw_id --vpc-id $vpc_id $profile_region

- Create Route Table

		route_tab_id=$(aws ec2 create-route-table --vpc-id $vpc_id $profile_region --query RouteTable.RouteTableId | tr -d \"[:space:][]{} ) && aws ec2 create-tags --resources $route_tab_id --tags Key=Name,Value=RouteTableMAIN $profile_region

- Creating a default route in Route Table.

		aws ec2 create-route --route-table-id $route_tab_id --destination-cidr-block 0.0.0.0/0 --gateway-id $igw_id $profile_region

- Associate Route Table 1 to PublicSubnet 
		
		BaseSubnetRouteAsscnID=$(aws ec2 associate-route-table --route-table-id $route_tab_id --subnet-id $subnet_id $profile_region --query AssociationId | tr -d \"[:space:][]{} )

- Create a Security Group
		
		web_sec_grp=$(aws ec2 create-security-group --group-name "WEB_APP" --description "Web Frontend entry for traffic" --vpc-id $vpc_id $profile_region --query GroupId | tr -d \"[:space:][]{}) &&aws ec2 create-tags --resources $web_sec_grp --tags Key=Name,Value=HTTP-HTTPS $profile_region

		ssh_sec_grp=$(aws ec2 create-security-group --group-name "SSH_22" --description "Login Shell for admin" --vpc-id $vpc_id $profile_region --query GroupId | tr -d \"[:space:][]{}) &&aws ec2 create-tags --resources $ssh_sec_grp --tags Key=Name,Value=SSH-SFTP $profile_region

- Adding ports to the Security Group

		aws ec2 authorize-security-group-ingress --group-id  $web_sec_grp --protocol tcp --port 80 --cidr 0.0.0.0/0 $profile_region
		aws ec2 authorize-security-group-ingress --group-id  $web_sec_grp --protocol tcp --port 443 --cidr 0.0.0.0/0 $profile_region

- Removing ports from the Security Group
		
		aws ec2 revoke-security-group-ingress  --group-id  $web_sec_grp --protocol tcp --port 80 --cidr 0.0.0.0/0 $profile_region

- Adding your IP in SSH
		
		aws ec2 authorize-security-group-ingress --group-id  $ssh_sec_grp --protocol tcp --port 22 --cidr $(echo $(curl -s https://checkip.amazonaws.com) /32 | tr -d \"[:space:][]) $profile_region

- Creating a Key Pair for ssh

		aws ec2 create-key-pair --key-name KarthikAdmin $profile_region --query KeyMaterial | tr -d \"' > KarthikAdmin.pem


### Process to delete the VPC.

#### Step 1: Disassociate all the route tables with Subnets using association ID

		Note: One cannot diassociate the default route-associations

- To get the associations of route table

		$aws ec2 describe-route-tables $OutputFormat --query "RouteTables"[]."Associations"[]."RouteTableAssociationId"

- To disassociate

		$aws ec2 disassociate-route-table --association-id "<route-acn-id>" $OutputFormat

- To delete the route table

		$aws ec2 delete-route-table --route-table-id rtb-0cfd8e87a069d97f8 $OutputFormat

- To get the route table ID's

		$aws ec2 describe-route-tables $OutputFormat --query "RouteTables"[]."Associations"[]."RouteTableId"


#### Step 2: Get the associated subnets

- Get the subnets

		$aws ec2 describe-subnets $OutputFormat --query "Subnets"[]."SubnetId"

- Delete the subnet

		$aws ec2 delete-subnet --subnet-id "subnet-0cea43cee9a98b7b8" $OutputFormat

#### Step 3: Get the VPC - Internet - Gateway association

- Get the details of VPC

		aws ec2 describe-vpcs $OutputFormat 

- Get the details of the CIDR block

		$aws ec2 describe-vpcs $OutputFormat --query "Vpcs"[]."CidrBlockAssociationSet"[]."AssociationId" | tr -d [:space:][]{}

- Get the details of the Internet Gate way

		$aws ec2 describe-internet-gateways $OutputFormat

- Detach the IGW with VPC.

		$aws ec2 detach-internet-gateway --internet-gateway-id igw-0b2d7d7013b4531c6  --vpc-id vpc-0f6ff424900f5e944 $OutputFormat

#### Step 4: Remove the security groups.

- Remove the security groups

		$aws ec2 delete-security-group --group-id "sg-01afc41cb5247123c" $OutputFormat

#### Step 5: Delete IGW and VPC

- Delete IGW

		$aws ec2 delete-internet-gateway --internet-gateway-id igw-0b2d7d7013b4531c6 $OutputFormat

- Delete VPC
		
		$aws ec2 delete-vpc --vpc-id vpc-0f6ff424900f5e944 $OutputForma
