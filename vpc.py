import pulumi
from pulumi_aws import ec2
from pulumi_aws import get_region, config

config = pulumi.Config()
vpc_cidr_block = config.require("vpc_cidr_block")
vpc_public_cidr_block = config.require("vpc_public_cidr_block")
vpc_private_cidr_block = config.require("vpc_private_cidr_block")
aws_config = pulumi.Config("aws")
aws_region = aws_config.require("region")


vpc = ec2.Vpc(
    f"vpc-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    cidr_block=vpc_cidr_block,
    tags={"Name": f"vpc-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }"},
)

elastic_ip = ec2.Eip(
    f"nat-eip-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    domain="vpc",
)

igw = ec2.InternetGateway(
    f"igw-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    vpc_id=vpc.id,
    tags={
        "Name": f"igw-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    },
)

private_subnet = ec2.Subnet(
    f"subnet-{aws_region}-private-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    vpc_id=vpc.id,
    cidr_block=vpc_private_cidr_block,
    availability_zone=f"{aws_region}a",
    tags={
        "Name": f"subnet-{aws_region}-private-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    },
)

public_subnet = ec2.Subnet(
    f"subnet-{aws_region}-public-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    vpc_id=vpc.id,
    cidr_block=vpc_public_cidr_block,
    availability_zone=f"{aws_region}a",
    tags={
        "Name": f"subnet-{aws_region}-public-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    },
)

nat_gateway = ec2.NatGateway(
    f"ngw-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    allocation_id=elastic_ip.id,
    subnet_id=public_subnet.id,
    opts=pulumi.ResourceOptions(depends_on=[igw]),
    tags={"Name": f"ngw-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }"},
)

# private_route_table = ec2.RouteTable(
#     f"rt-{aws_region}-private-{ pulumi.get_project() }-{ pulumi.get_stack() }",
#     vpc_id=vpc.id,
#     routes=[
#         ec2.RouteTableRouteArgs(cidr_block="0.0.0.0/0", nat_gateway_id=nat_gateway.id)
#     ],
#     tags={
#         "Name": f"rt-{aws_region}-private-{ pulumi.get_project() }-{ pulumi.get_stack() }"
#     }
# )

public_route_table = ec2.RouteTable(
    f"rt-{aws_region}-public-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    vpc_id=vpc.id,
    routes=[ec2.RouteTableRouteArgs(cidr_block="0.0.0.0/0", gateway_id=igw.id)],
    tags={
        "Name": f"rt-{aws_region}-private-{ pulumi.get_project() }-{ pulumi.get_stack() }"
    },
)

# ec2.RouteTableAssociation(
#     f"rta-{private_subnet._name}",
#     route_table_id=private_route_table.id,
#     subnet_id=private_subnet.id
# )

ec2.RouteTableAssociation(
    f"rta-{public_subnet._name}",
    route_table_id=public_route_table.id,
    subnet_id=public_subnet.id,
)
