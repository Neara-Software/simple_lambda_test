import pulumi_aws as aws
from config import environment, lambda_function_name

# Create a CloudWatch Log Group for the Lambda Function
lambda_log_group = aws.cloudwatch.LogGroup(
    "lambda-log-group",
    name=f"/aws/lambda/{lambda_function_name}",
    retention_in_days=14,
    tags={
        "Name": "LambdaFunctionLogGroup",
        "Environment": environment,
        "ManagedBy": "Pulumi",
    },
)