from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_kms as kms,
)
from constructs import Construct


class ComputeStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        raw_s3_bucket: s3.IBucket,
        raw_s3_kms_key: kms.IKey,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Function
        glue_lambda_function = _lambda.Function(
            self,
            "ETLTriggerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("compute_stack"),
            handler="s3_to_glue.handler",
            environment={"GLUE_CRAWLER_NAME": "YourGlueCrawlerName"},
        )

        # Grant Lambda permissions to use the KMS key
        raw_s3_kms_key.grant_encrypt_decrypt(glue_lambda_function)

        # S3 Event Notification
        notification = s3_notifications.LambdaDestination(glue_lambda_function)
        raw_s3_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
