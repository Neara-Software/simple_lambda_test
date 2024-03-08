import json
import os


def info_handler(event, context):
    json_region = os.environ["AWS_REGION"]
    print(event)
    print(context)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"Region ": json_region}),
    }
