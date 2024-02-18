import json
import os
import requests
from datetime import datetime

def process_init():
    print(f"{datetime.now()} - Processing Init\n")
    print(f"{datetime.now()} - Init Processing Completed\n")

def process_shutdown():
    print(f"{datetime.now()} - Processing Shutdown\n")
    print(f"{datetime.now()} - Shutdown Processing Completed\n")

def process_handler(cloud_event):
    try:
        cloud_event_data = json.loads(cloud_event)
    except json.JSONDecodeError:
        raise Exception("\nPayload must be JSON encoded")

    try:
        slack_secret = json.loads(os.environ.get('SLACK_SECRET', ''))
    except json.JSONDecodeError:
        raise Exception("\nK8s secrets $env:SLACK_SECRET does not look to be defined")

    if os.environ.get('FUNCTION_DEBUG') == "true":
        print(f"{datetime.now()} - DEBUG: K8s Secrets:\n{os.environ.get('SLACK_SECRET')}\n")
        print(f"{datetime.now()} - DEBUG: CloudEventData\n {cloud_event_data}\n")

    payload = {
        "text": f"{cloud_event_data['involvedObject']['kind']} {cloud_event_data['involvedObject']['name']} in {cloud_event_data['metadata']['namespace']}: {cloud_event_data['reason']}\nEvent Type: {cloud_event_data['type']}\nUnique ID: {cloud_event_data['id']}\nDateTime in UTC: {cloud_event_data['time']}\nSource: {cloud_event_data['source']}",
        "attachments": [
            {
                "text": f"{slack_secret['SLACK_MESSAGE_PRETEXT']}",
                "footer": "Powered by Knative",
                "footer_icon": "https://github.com/knative/docs/blob/main/docs/images/logo/cmyk/knative-logo-cmyk.png"
            }
        ]
    }

    if os.environ.get('FUNCTION_DEBUG') == "true":
        print(f"{datetime.now()} - DEBUG: {json.dumps(payload)}")

    print(f"{datetime.now()} - Sending Webhook payload to Webex ...")
    try:
        response = requests.post(os.environ.get('WEBEX_WEBHOOK_URL'), json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"{datetime.now()} - Failed to send Webex Message: {e}")

    print(f"{datetime.now()} - Successfully sent Webhook ...\n")

if __name__ == "__main__":
    # Sample cloud event JSON
    cloud_event_json = """
    {
        "message": "Some message",
        "reason": "Some reason",
        "involvedObject": {
            "kind": "Pod",
            "name": "example-pod"
        },
        "metadata": {
            "namespace": "default"
        },
        "type": "Normal",
        "id": "12345",
        "time": "2024-02-18T12:00:00Z",
        "source": "some-source"
    }
    """

    # Call process_handler with the sample cloud event JSON
    process_handler(cloud_event_json)
