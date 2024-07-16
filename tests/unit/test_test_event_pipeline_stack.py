import aws_cdk as core
import aws_cdk.assertions as assertions

from test_event_pipeline.test_event_pipeline_stack import TestEventPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in test_event_pipeline/test_event_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TestEventPipelineStack(app, "test-event-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
