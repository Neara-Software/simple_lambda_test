from pulumi import Config
import pulumi_aws as aws

# Initialize Pulumi config
config = Config()

# Basic AWS configuration
aws_region = aws.config.region

# Project configuration
project_name = config.require("project_name")

# Environment and Stage configuration
environment = config.require("environment")  # e.g., dev, staging, prod
stage = config.require("stage")  # e.g., test, beta, gamma

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidr = "10.0.2.0/24"
private_subnet_cidr = "10.0.1.0/24"

# API Gateway configuration
api_gateway_name = f"{project_name}-{stage}-api"
api_gateway_stage_name = stage
api_gateway_resource_path = "info"
api_gateway_http_method = "GET"

# Lambda configuration
lambda_function_name = f"{project_name}-{stage}-lambda"
lambda_runtime = "python3.9"
lambda_handler = "main.info_handler"

# CloudWatch Logs configuration
cloudwatch_log_group_name = f"/aws/lambda/{lambda_function_name}"

# Optionally, you can add more configurations here.