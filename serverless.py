import pulumi

import pulumi_aws as aws
from pulumi_aws import iam
from pulumi_aws import lambda_
from pulumi_aws import ec2
from vpc import vpc, private_subnet
from pulumi_aws import lambda_ as lambda_

import pulumi_aws_apigateway as apigateway

aws_config = pulumi.Config("aws")
aws_region = aws_config.require("region")

lambda_role = iam.Role(
    f"role-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }""",
)

lambda_role_policy_attachment = iam.policy_attachment = iam.RolePolicyAttachment(
    f"role-attachment-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    role=lambda_role,
    policy_arn=iam.ManagedPolicy.AWS_LAMBDA_VPC_ACCESS_EXECUTION_ROLE,
)

lambda_security_group = ec2.SecurityGroup(
    f"security-group-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    egress=[],
    ingress=[],
    vpc_id=vpc.id,
)

lambda_func = lambda_.Function(
    f"lambda-{aws_region}-{ pulumi.get_project() }-{ pulumi.get_stack() }",
    role=lambda_role.arn,
    runtime="python3.9",
    handler="main.info_handler",
    vpc_config={
        "subnetIds": [private_subnet.id],
        "securityGroupIds": [lambda_security_group],
    },
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./lambda")}),
)

rest_api = apigateway.RestAPI(
    f"{ pulumi.get_project() }-{aws_region}-{ pulumi.get_stack() }",
    routes=[apigateway.RouteArgs(path="/", method="GET", event_handler=lambda_func)],
    binary_media_types=["application/json"],
    stage_name="info",
)
