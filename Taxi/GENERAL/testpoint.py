from typing import Any
from typing import Dict

from taxi import settings
from taxi.pytest_plugins.blacksuite import patches
from taxi.util import client_session


TESTPOINT_URL = patches.MOCKSERVER_MARK + '/testpoint'


async def add(name: str, data: Any):
    if not settings.IS_BLACKSUITE_ENV:
        return

    json_data = {'name': name, 'data': data}
    return await _send_data(json_data)


async def _send_data(json_data: Dict[str, Any]):
    async with client_session.get_client_session() as session:
        response = await session.post(url=TESTPOINT_URL, json=json_data)
        response.raise_for_status()

        response_json = await response.json()

        return response_json['data']
