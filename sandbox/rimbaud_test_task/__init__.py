import logging
from sandbox import sdk2
import requests
import json


class RimbaudHelloWorldTestTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        tokens = sdk2.parameters.YavSecret("YAV secret identifier (with optional version)", default="sec-0abc@ver-0def")

    def on_execute(self):

        logging.info("Hello, rimbaud! Hello, dear world!")

        tokens = self.Parameters.tokens.data()
        NIRVANA_TOKEN = tokens["rimbaud_nirvana_token"]

        headers = {
            'Authorization': 'OAuth ' + NIRVANA_TOKEN,
            "Content-Type": "application/json;charset=utf-8",
        }

        r = requests.post(
            'https://nirvana.yandex-team.ru/api/public/v1/cloneWorkflowInstance',
            data=json.dumps(
                {
                    'jsonrpc': "2.0",
                    'id': 'id',
                    'method': 'cloneWorkflowInstance',
                    "params": {
                        'workflowId': 'bbedd057-326f-4598-a584-fc01359fdc7c',
                        'workflowInstanceId': '8577ff7b-0644-47e8-9f59-2152e2d97de1',
                    },
                }
            ),
            verify=False,
            headers=headers,
        )

        graph = r.json()['result']
        logging.info(graph)

        r = requests.post(
            'https://nirvana.yandex-team.ru/api/public/v1/setGlobalParameters',
            data=json.dumps(
                {
                    'jsonrpc': "2.0",
                    'id': 'id',
                    'method': 'setGlobalParameters',
                    "params": {
                        "workflowInstanceId": graph,
                        "params": [
                            {
                                "parameter": "svn-url-for-arcadia",
                                "value": "arcadia:/arc/tags/images/mrindexer/stable-119/r3/arcadia@9715860",
                            }
                        ],
                    },
                }
            ),
            verify=False,
            headers=headers,
        )
