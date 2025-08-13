import json
import logging
import os

import azure.functions as func
import azure.durable_functions as df

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

SB_CONNECTION_STRING = os.getenv("SB_CONNECTION_STRING", "")

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# An HTTP-triggered function with a Durable Functions client binding
@myApp.route(route="orchestrators/hello_orchestrator")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    # function_name = req.route_params.get("functionName")
    instance_id = await client.start_new("hello_orchestrator")
    response = client.create_check_status_response(req, instance_id)
    return response


# Orchestrator
@myApp.orchestration_trigger(context_name="context")
def hello_orchestrator(context):
    result1 = yield context.call_activity("hello", "Seattle")
    result2 = yield context.call_activity("hello", "Tokyo")
    result3 = yield context.call_activity("hello", "London")
    result4 = yield context.call_activity(
        "publish_event",
        {
            "hello": "world",
        },
    )

    return [result1, result2, result3, result4]


# Activity
@myApp.activity_trigger(input_name="city")
async def hello(city: str):
    return f"Hello {city}"


@myApp.activity_trigger(input_name="payload")
async def publish_event(payload: dict) -> str:
    try:
        message = ServiceBusMessage(
            body=json.dumps(payload),
            content_type="application/json",
        )

        async with ServiceBusClient.from_connection_string(
            conn_str=SB_CONNECTION_STRING,
        ) as sb_client:
            async with sb_client.get_queue_sender(
                queue_name="queue.1",
                socket_timeout=3,
            ) as sender:
                await sender.send_messages(message)

    except Exception as e:
        logging.error(f"Error publishing event: {e}")
        raise e

    return "Done"
