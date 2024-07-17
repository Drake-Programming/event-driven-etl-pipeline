from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_glue as glue,
    aws_sqs as sqs,
    aws_lambda_event_sources as eventsources
)
from constructs import Construct


class LambdaStack(Stack):

    def __init__(
        self, scope: Construct, construct_id: str, crawler: glue.CfnCrawler, crawler_queue: sqs.Queue, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.crawler_policy = iam.PolicyStatement(
            actions=["glue:StartCrawler"],
            effect=iam.Effect.ALLOW,
            resources=[crawler.get_att("Arn").to_string()],
        )

        self.lambda_crawler_role = iam.Role(
            self,
            "LambdaCrawlerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Lambda Crawler Role",
            role_name="LambdaCrawlerRole",
            managed_policies=[self.crawler_policy],
        )

        # Lambda Function
        self.glue_lambda_function = _lambda.Function(
            self,
            "LambdaCrawlerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("_lambda"),
            role=self.lambda_crawler_role,
            handler="s3_to_glue.handler",
            environment={"GLUE_CRAWLER_NAME": crawler.name},
        )


