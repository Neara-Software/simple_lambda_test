# Neara Software Engineer Infra test

In this practical, hands on test, we want to see how write infrastructure as code. The interview would have assessed existing knowledge and this is the actual implentation of a cut down, MVP version of the solution you worked on.

With this collaboration process, you will get some guidance from one of our team members on how to improve your code as if you worked here. You'll also learn the basics of some AWS networking and lambdas that get used in production.

It's a bit more time invested but it should give you a better experience in learning and how things would work.

## Requirements

### Tech Stack
- Python 3.9
- [Pulumi for AWS](https://www.pulumi.com/docs/get-started/aws/)
- an AWS account (on the free tier, nothing here should cost you)
- provide instructions on how to run your code

### Objective
Build the following architecture in Pulumi:

![architecture](./architecture.png)
** correction - put the NAT in a public subnet

We should be able to curl the API Gateway endpoint and get the json response returned from the lambda. Additionally, all logging output should go to Cloudwatch.

The lambda function is provided for you in the [./lambda](./lambda/) directory.


## Submitting and Collaboration
- fork this repo
- make the commits and changes necessary on a feature branch
- make an upstream pull request back to this repo and email us with your PR link
- the examiner can review the PR and make comments and ask you to improve the PR
- once the PR is rejected or accepted, you can delete the PR, we won't merge it

## Solution

### Testing
1. Install pulumi the preferred way
2. Login to pulumi cloud `pulumi login` or use local backend `pulumi login --local`
3. (Optional) Create and activate virtual env `python3 -m venv venv && source venv/bin/activate`
4. Install packages using pip `pip install -r requirements.txt` 
5. Ensure correct aws profile configuration
6. Run `PULUMI_CONFIG_PASSPHRASE="" pulumi up --stack dev` and apply changes.
7. Run `export $(PULUMI_CONFIG_PASSPHRASE="" pulumi stack --stack dev output --shell) && curl $SIMPLE_LAMBDA_TEST_URL` - the output should be the JSON returned by Lambda function.

### General
I took 1-region and 1-az approach, which results from the `architecture.png` diagram. I assumed that `router` represents general routing functionality, not a particular `router` instance. 
I find API Gateway location confusing, I assume that it was to be placed outside of the VPC, just like CloudWatch is. Putting API Gateway within VPC on diagram could suggest VPC endoints usage, provided the arrow was pointed into API Gateway.
General resources naming convention could be reconsidered in relation to company approach/policies.

### VPC 
VPC is configured the easiest way possible. I decided to split VPC configuration into a separate module in order to spearate infrastructure from the platform and application configuration (API GW and Lambda in serverless module).

In a real-case scenario I would probably apply some extra separation, like proposed in [https://github.com/pulumi-zephyr](aa) example - VPC configuration in infrastrucutre repository, application-related infrastructure in application repository. 

AWS IPAM integration could be used as well.

There's no explicit information on private subnet having route to NAT gateway. I added the required configuration but kept it commented. I added route to IGW in public subnet though, based on the diagram.

### Serverless 
Serveless part consist of a module containing Lambda function and API Gateway. 

#### API Gateway
Driven by a pragmatic approach I decided to use [AWS API Gateway Component](https://github.com/pulumi/pulumi-aws-apigateway). It provides an abstraction layer over resources required to configure AWS API Gateway, making the configuration fast and easy compared to either specyfing manually OpenAPI definition JSON or using lower-level resources like `aws.apigateway.Integration` or `aws.apigateway.Method`.

I don't have a strong opinion on a quality of the API Gateway component. I don't have any real hands-on expirience with it and I'm not a part of communiy, that obviously must have some opinons on it. In a real world scenario I would take a deeper dive before using API Gateway component over a classic way of configuration.

I made a shortcut while confguring API Gateway routing. According to the `architecture.png` diagram, the Lambda function should be exposed under `/info` path. I named the stage `info` and set route to `/`. It's a result of a fact, that `stage` name becomes a part of a path in the final url. In a real world it would be considered a bad practice, because it's does not follow the API GW idea. 

This issue can be might be mitigated i.e. by setting API Gateway Custom Domain with proper path settings or configuring a Cloudfront distribution, considering the stage path in the origin configuration.

In a real-case scenario I'd go with using a custom domain, an actual stage name (prod/dev/etc) as the API GW stage parameter and `/info` as lambda path. 

I'd also consider configuring logging.

#### Lambda
Lambda in located private subnet and writes output logs to Cloudwatch. An empty security group had to be added in order to run Lambda in a VPC. I didn't add any outbound rule because there no explicit information on Lambda having Internet access in the documentation. AWS-managed policy was used to provide Lambda access to CloudWatch and assigning network interfaces within a VPC. In a real-world scenario I would consider adjusting CloudWatch log group configuration i.e setting retention.
