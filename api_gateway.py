import pulumi_aws as aws
from pulumi import Output, export
from config import (
    aws_region,
    api_gateway_stage_name,
    api_gateway_resource_path,
    api_gateway_http_method,
    environment,
)
from lambda_function import lambda_function, lambda_invoke_arn


# Create a single Swagger spec route handler for a Lambda function.
def swagger_route_handler(arn):
    return {
        "x-amazon-apigateway-any-method": {
            "x-amazon-apigateway-integration": {
                "uri": Output.format(
                    "arn:aws:apigateway:{0}:lambda:path/2015-03-31/functions/{1}/invocations",
                    aws_region,
                    arn,
                ),
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy",
            },
        },
    }


# Create the API Gateway Rest API, using a swagger spec.
rest_api = aws.apigateway.RestApi(
    "api",
    body=Output.json_dumps(
        {
            "swagger": "2.0",
            "info": {"title": "api", "version": "1.0"},
            "paths": {"/{proxy+}": swagger_route_handler(lambda_invoke_arn)},
        }
    ),
    tags={
        "Environment": environment,
        "ManagedBy": "Pulumi",
    },
)

# Create a resource attached to the Rest API for the info path
rest_resource = aws.apigateway.Resource(
    "apiResource",
    rest_api=rest_api.id,
    parent_id=rest_api.root_resource_id,
    path_part=api_gateway_resource_path,
)

# Create a method for the resource. This assumes you want to use HTTP GET
rest_method = aws.apigateway.Method(
    "apiMethod",
    rest_api=rest_api.id,
    resource_id=rest_resource.id,
    http_method=api_gateway_http_method,
    authorization="NONE",
)

# Create an integration to connect the method to the Lambda function
rest_integration = aws.apigateway.Integration(
    "apiIntegration",
    rest_api=rest_api.id,
    resource_id=rest_resource.id,
    http_method=rest_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function.invoke_arn,
)

# Create a deployment to enable invoking the REST API's endpoint
rest_deployment = aws.apigateway.Deployment(
    "apiDeployment",
    rest_api=rest_api.id,
    # Note: Set to empty to avoid creating an implicit stage, we'll create it
    # explicitly below instead.
    stage_name="",
)

# Create a stage to define the deployment
rest_stage = aws.apigateway.Stage(
    "apiStage",
    rest_api=rest_api.id,
    deployment=rest_deployment.id,
    stage_name=api_gateway_stage_name,
)

# Set up permissions for the API Gateway to invoke the Lambda
rest_lambda_permission = aws.lambda_.Permission(
    "apiLambdaPermission",
    action="lambda:InvokeFunction",
    function=lambda_function.arn,
    principal="apigateway.amazonaws.com",
    source_arn=rest_deployment.execution_arn.apply(lambda arn: f"{arn}/*"),
)

# Create an HTTP API and attach the lambda function to it
http_api = aws.apigatewayv2.Api("httpApi", protocol_type="HTTP")

# Create an integration for the HTTP API to the Lambda function
http_integration = aws.apigatewayv2.Integration(
    "httpApiIntegration",
    api_id=http_api.id,
    integration_type="AWS_PROXY",
    integration_method="POST",
    # Make sure to use the correct invoke ARN for the Lambda function
    integration_uri=lambda_invoke_arn,
    payload_format_version="2.0",
    connection_type="INTERNET",
)

# Wait for the integration to be created before creating the route
integration_ready = Output.all(http_api.id, http_integration.id).apply(
    lambda ids: ids[1]
)

# Create a route for the HTTP API
http_route = aws.apigatewayv2.Route(
    "httpApiRoute",
    api_id=http_api.id,
    route_key="$default",
    # The target should include the correct integration ID
    target=integration_ready.apply(lambda id: f"integrations/{id}"),
)

http_stage = aws.apigatewayv2.Stage(
    "httpApiStage", api_id=http_api.id, name=api_gateway_stage_name, auto_deploy=True
)

http_lambda_permission = aws.lambda_.Permission(
    "httpApiLambdaPermission",
    action="lambda:InvokeFunction",
    function=lambda_function.arn,
    principal="apigateway.amazonaws.com",
)

# Export the https endpoint of the running Rest API
export(
    "apigateway-rest-endpoint",
    rest_deployment.invoke_url.apply(
        lambda url: url + api_gateway_stage_name + "/{proxy+}"
    ),
)

# Output the invoke URL for the HTTP API
export(
    "apigatewayv2-http-endpoint",
    Output.all(http_api.api_endpoint, http_stage.name).apply(
        lambda values: values[0] + "/" + values[1] + "/"
    ),
)