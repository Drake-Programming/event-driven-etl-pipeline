import aws_cdk as core
import aws_cdk.assertions as assertions

from event_driven_etl_pipeline.event_driven_etl_pipeline_stack import EventDrivenEtlPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in event_driven_etl_pipeline/event_driven_etl_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EventDrivenEtlPipelineStack(app, "event-driven-etl-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
