import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

// Create VPC and private subnet
const vpc = new aws.ec2.Vpc("andy-vpc", { cidrBlock: "10.0.0.0/16" });

const subnet = new aws.ec2.Subnet("private-subnet", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
});

// Lambda definitions
const role = new aws.iam.Role("info-handler-role", {
  assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal(
    aws.iam.Principals.LambdaPrincipal
  ),
});

const infoHandler = new aws.lambda.Function("info-handler", {
  role: role.arn,
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

const route = new aws.apigatewayv2.Route("get-info-route", {
  apiId: api.id,
  routeKey: "GET /info",
});

// Log info
export const subnetCidr = subnet.cidrBlock;
export const lambdaFunctionArn = infoHandler.arn;
