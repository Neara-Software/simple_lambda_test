from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, NATGateway, InternetGateway, APIGateway
from diagrams.aws.management import Cloudwatch

with Diagram("Neara Software Infra Challenge", show=False):
    with Cluster("AWS Region"):
        with Cluster("VPC"):
            igw = InternetGateway("Internet Gateway")

            with Cluster("Public Subnet"):
                nat_gateway = NATGateway("NAT Gateway")
                nat_gateway >> igw

            with Cluster("Private Subnet"):
                lambda_func = Lambda("Lambda Function")
                lambda_func - nat_gateway
                cloudwatch_logs = Cloudwatch("CloudWatch Logs")
                lambda_func >> cloudwatch_logs

        api_gateway = APIGateway("API Gateway")
        api_gateway >> lambda_func
