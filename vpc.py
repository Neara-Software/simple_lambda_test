import pulumi_aws as aws
from pulumi import export
from config import (
    aws_region,
    vpc_cidr,
    public_subnet_cidr,
    private_subnet_cidr,
    environment,
)

# Create a new VPC
vpc = aws.ec2.Vpc(
    "vpc",
    cidr_block=vpc_cidr,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "my-vpc", "Environment": environment},
)

# Create an internet gateway for the VPC
internet_gateway = aws.ec2.InternetGateway(
    "vpc-ig", vpc_id=vpc.id, tags={"Name": "my-vpc-ig", "Environment": environment}
)

# Create a public subnet
public_subnet = aws.ec2.Subnet(
    "public-subnet",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidr,
    map_public_ip_on_launch=True,
    availability_zone=f"{aws_region}a",
    tags={"Name": "my-public-subnet", "Environment": environment},
)

# Create a NAT gateway in the public subnet
nat_gateway = aws.ec2.NatGateway(
    "nat-gateway",
    allocation_id=aws.ec2.Eip("nat-eip").id,
    subnet_id=public_subnet.id,
    tags={"Name": "my-nat-gateway", "Environment": environment},
)

# Create a private subnet
private_subnet = aws.ec2.Subnet(
    "private-subnet",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidr,
    availability_zone=f"{aws_region}a",
    tags={"Name": "my-private-subnet", "Environment": environment},
)

# Create a route table for the public subnet
public_route_table = aws.ec2.RouteTable(
    "public-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
        )
    ],
    tags={"Name": "my-public-route-table", "Environment": environment},
)

# Associate the public route table with the public subnet
aws.ec2.RouteTableAssociation(
    "public-rta", subnet_id=public_subnet.id, route_table_id=public_route_table.id
)

# Create a route table for the private subnet
private_route_table = aws.ec2.RouteTable(
    "private-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gateway.id,
        )
    ],
    tags={"Name": "my-private-route-table", "Environment": environment},
)

# Associate the private route table with the private subnet
aws.ec2.RouteTableAssociation(
    "private-rta", subnet_id=private_subnet.id, route_table_id=private_route_table.id
)

# Exporting IDs of the created resources so they can be used in other modules
export("vpc_id", vpc.id)
export("public_subnet_id", public_subnet.id)
export("private_subnet_id", private_subnet.id)
export("nat_gateway_id", nat_gateway.id)