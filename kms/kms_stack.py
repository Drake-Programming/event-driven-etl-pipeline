from aws_cdk import Stack, Duration, aws_kms as kms
from constructs import Construct


class KmsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #  Make KMS key for raw S3 bucket
        self.raw_bucket_kms_key = kms.Key(
            self,
            "RawBucketKey",
            enable_key_rotation=True,
            rotation_period=Duration.days(90),
        )
        self.raw_bucket_kms_key.add_alias("alias/test-s3-raw-encryption")