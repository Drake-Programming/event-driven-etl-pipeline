#!/usr/bin/env python3
import os

import aws_cdk as cdk

from storage.storage_stack import StorageStack

app = cdk.App()

storage_stack = StorageStack(
    app,
    "StorageStack",
)

app.synth()
