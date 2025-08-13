# Azure Durable Functions Timeout Example

This repository reproduces an issues I am seeing with an activity that uses Azure Service Bus aio client to send messages.

## Problem

Under load the activity will sometimes freeze and result in a function timeout and worker restart.

```
[2025-08-13T12:16:44.057Z] Task was destroyed but it is pending!
[2025-08-13T12:16:44.057Z] task: <ContextEnabledTask pending name='Task-1285' coro=<Dispatcher._dispatch_grpc_request() done, defined at /opt/homebrew/Cellar/azure-functions-core-tools@4/4.1.1/workers/python/3.12/OSX/Arm64/azure_functions_worker/dispatcher.py:287> wait_for=<Future pending cb=[ContextEnabledTask.task_wakeup()]>>

...

[2025-08-13T12:17:44.046Z] Timeout value of 00:01:00 exceeded by function 'Functions.publish_event' (Id: '98d8ea26-9f19-420e-b1d0-3ef47760b640'). Initiating cancellation.
[2025-08-13T12:17:44.099Z] Executed 'Functions.publish_event' (Failed, Id=98d8ea26-9f19-420e-b1d0-3ef47760b640, Duration=60066ms)
[2025-08-13T12:17:44.099Z] Microsoft.Azure.WebJobs.Host: Timeout value of 00:01:00 was exceeded by function: Functions.publish_event.
[2025-08-13T12:17:46.110Z] A function timeout has occurred. Restarting worker process executing invocationId '98d8ea26-9f19-420e-b1d0-3ef47760b640'.
[2025-08-13T12:17:46.557Z] Worker process started and initialized.
[2025-08-13T12:17:56.592Z] Restart of language worker process(es) completed.
```

## Reproduction Steps

1. Clone the repository.
2. Ensure you have Docker installed and running along with azure function core tools.
3. Create the python environment how you wish and install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the following command to start the services:

   ```bash
   docker compose up -d
   func start
   ```

5. Keep sending many requests to `localhost:7071/api/orchestrators/hello_orchestrator`, and eventually the above error message will appear.
