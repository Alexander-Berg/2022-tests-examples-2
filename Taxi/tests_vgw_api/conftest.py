# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest
from vgw_api_plugins import *  # noqa: F403 F401


@pytest.fixture(name='personal', autouse=True)
def _personal(mockserver, load_json):
    class Context:
        @staticmethod
        @mockserver.json_handler('personal/v1/phones/bulk_store')
        def personal_phone_retrieve(request):
            body = json.loads(request.get_data())
            items = body['items']
            response = []
            for item in items:
                response.append(
                    {'id': f'id-{item["value"]}', 'value': f'{item["value"]}'},
                )
            return {'items': response}

    return Context()
