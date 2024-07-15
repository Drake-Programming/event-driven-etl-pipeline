from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_glue as glue,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
)
from constructs import Construct


class IntegrationStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        raw_bucket: s3.IBucket,
        raw_kms_key: kms.IKey,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SNS Topic
        topic = sns.Topic(self, "ETLTopic")
        topic.add_subscription(
            subscriptions.EmailSubscription("adaptivecreature1864@gmail.com")
        )
