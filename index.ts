import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

const stack = pulumi.getStack();

// Create VPC and private subnet
const vpc = new aws.ec2.Vpc("andy-vpc", { cidrBlock: "10.0.0.0/16" });

const subnet = new aws.ec2.Subnet("private-subnet", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
});

// Lambda definitions
const lambdaRole = new aws.iam.Role("info-handler-role", {
  assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal(
    aws.iam.Principals.LambdaPrincipal
  ),
});

const infoHandler = new aws.lambda.Function("info-handler", {
  role: lambdaRole.arn,
  runtime: aws.lambda.Runtime.Python3d9,
  code: new pulumi.asset.FileArchive("./lambda/main.py.zip"),
  handler: "main.info_handler", // fileName.methodName
});

// API Gateway
const securityGroup = new aws.ec2.SecurityGroup("api-gateway-security-group", {
  vpcId: vpc.id,
  ingress: [
    {
      description: "HTTP inbound",
      fromPort: 80,
      toPort: 80,
      protocol: "tcp",
      cidrBlocks: ["0.0.0.0/0"],
    },
  ],
});

const vpcLink = new aws.apigatewayv2.VpcLink("andy-vpc-link", {
  subnetIds: [subnet.id],
  securityGroupIds: [securityGroup.id],
});

const api = new aws.apigatewayv2.Api("andy-api-gateway", {
  protocolType: "HTTP",
});

const withApi = new aws.lambda.Permission(
  "lambdaPermission",
  {
    action: "lambda:InvokeFunction",
    principal: "apigateway.amazonaws.com",
    function: infoHandler,
    sourceArn: pulumi.interpolate`${api.executionArn}/*/*`,
  },
  { dependsOn: [api, infoHandler] }
);

const integration = new aws.apigatewayv2.Integration("andy-integration", {
  apiId: api.id,
  integrationType: "AWS_PROXY",
  integrationUri: infoHandler.arn,
  //integrationMethod: "GET",
});

const route = new aws.apigatewayv2.Route("get-info-route", {
  apiId: api.id,
  routeKey: "GET /info",
  target: integration.id.apply((id) => "integrations/" + id),
});

const stage = new aws.apigatewayv2.Stage("api-stage", {
  apiId: api.id,
  name: stack,
  autoDeploy: true,
});

// Log info
export const subnetCidr = subnet.cidrBlock;
export const lambdaFunctionArn = infoHandler.arn;
export const endpoint = api.apiEndpoint;
