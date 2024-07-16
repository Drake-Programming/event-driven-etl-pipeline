#!/usr/bin/env python3
import os

import aws_cdk as cdk

from glue.glue_stack import GlueStack
from kms.kms_stack import KmsStack
from _lambda.lambda_stack import LambdaStack
from storage.storage_stack import StorageStack


app = cdk.App()
kms_stack = KmsStack(
    app,
    "KmsStack",
)

storage_stack = StorageStack(
    app, "StorageStack", raw_s3_kms_key=kms_stack.raw_bucket_kms_key
)

glue_stack = GlueStack(
    app,
    "GlueStack",
    raw_s3_kms_key=kms_stack.raw_bucket_kms_key,
    raw_s3_bucket=storage_stack.raw_bucket,
)

lambda_stack = LambdaStack(
    app, "LambdaStack", crawler=glue_stack.raw_glue_crawler
)

lambda_stack.add_dependency(glue_stack)
glue_stack.add_dependency(storage_stack)
storage_stack.add_dependency(kms_stack)

app.synth()
