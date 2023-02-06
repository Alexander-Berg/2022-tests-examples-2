import logging
import os
import pathlib
from typing import Dict
from typing import List
import urllib

import aiohttp
import pytest

from taxi_schemas import utils
from taxi_schemas.utils import http_client

logger = logging.getLogger(__name__)

API_URL = os.getenv('CLOWNDUCTOR_URL', 'http://clownductor.taxi.yandex.net')

NAMESPACE_FIELD = 'audit_namespace'
COMMON_NAMESPACE = 'common'


@pytest.mark.skipif(
    not os.environ.get('IS_TEAMCITY'), reason='Test works on build agent only',
)
@pytest.mark.nofilldb()
async def test_check_namespace(new_and_modified_config_path):
    config_schema = utils.load_yaml(new_and_modified_config_path)

    file = pathlib.Path(new_and_modified_config_path)
    config_name, _ = file.name.split('.', maxsplit=1)
    if NAMESPACE_FIELD not in config_schema:
        logger.warning(
            f'Config `%s` does not have a %s field. '
            'See https://nda.ya.ru/t/stWF0LQ-59HrJu for details',
            config_name,
            NAMESPACE_FIELD,
        )
        return
    if config_schema[NAMESPACE_FIELD] == COMMON_NAMESPACE:
        logger.info(
            'Skip test because `common` '
            'value for audit_namespace field is being used',
        )
        return

    existed_namespace = config_schema[NAMESPACE_FIELD]
    registered_namespaces = []
    registered_namespaces = await _get_namespaces(existed_namespace)

    assert existed_namespace in registered_namespaces, (
        f'Namespace {existed_namespace} '
        f'for `{config_name}` config not registered'
    )


async def _get_namespaces(namespace: str) -> List[str]:
    response: Dict
    async with aiohttp.ClientSession() as session:
        client = http_client.BaseClient(session)
        response = await client.request(
            'POST',
            urllib.parse.urljoin(API_URL, '/v1/namespaces/retrieve/'),
            json={'filters': {'names': [namespace]}},
        )
    return [namespace_obj['name'] for namespace_obj in response['namespaces']]
