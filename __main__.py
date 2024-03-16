"""An AWS Python Pulumi program"""

import pulumi
import vpc
import serverless

pulumi.export("SIMPLE_LAMBDA_TEST_URL", serverless.rest_api.url)
