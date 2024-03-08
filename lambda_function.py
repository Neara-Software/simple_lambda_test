from pulumi_aws import iam, lambda_
from pulumi import export, Output, AssetArchive, FileArchive
from config import lambda_function_name, lambda_runtime, lambda_handler, environment

# IAM Role for Lambda Function
lambda_role = iam.Role(
    "lambdaRole",
    assume_role_policy=Output.all().apply(
        lambda args: """{
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }]
    }"""
    ),
)

# IAM Policy for Lambda Execution and logging to CloudWatch
policy = iam.RolePolicy(
    "lambdaPolicy",
    role=lambda_role.id,
    policy=Output.all().apply(
        lambda args: """{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*",
                "Effect": "Allow"
            }
        ]
    }"""
    ),
)

# Lambda Function using pulumi.AssetArchive for the code
lambda_function = lambda_.Function(
    lambda_function_name,
    role=lambda_role.arn,
    runtime=lambda_runtime,
    handler=lambda_handler,
    code=AssetArchive({".": FileArchive("./lambda")}),
    timeout=60,
    tags={
        "Environment": environment,
        "ManagedBy": "Pulumi",
    },
)

lambda_invoke_arn = lambda_function.arn

# Output the ARN of the Lambda function
export("lambda_function_arn", lambda_invoke_arn)