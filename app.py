#!/usr/bin/env python3
import os

import aws_cdk as cdk

from security_stack.security_stack import SecurityStack
from storage_stack.storage_stack import StorageStack
from compute_stack.compute_stack import ComputeStack
from glue_stack.glue_stack import GlueStack


app = cdk.App()

security_stack = SecurityStack(app, "SecurityStack")

#  init storage stack
storage_stack = StorageStack(
    app, "StorageStack", raw_s3_kms_key=security_stack.raw_bucket_kms_key
)

#  init compute stack
compute_stack = ComputeStack(
    app,
    "ComputeStack",
    raw_s3_bucket=storage_stack.raw_bucket,
    raw_s3_kms_key=security_stack.raw_bucket_kms_key,
)

#  init glue stack
glue_stack = GlueStack(
    app,
    "GlueStack",
    raw_s3_bucket=storage_stack.raw_bucket,
    raw_s3_kms_key=security_stack.raw_bucket_kms_key,
)

app.synth()
