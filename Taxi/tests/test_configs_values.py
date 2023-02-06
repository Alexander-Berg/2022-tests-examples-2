import asyncio
import logging
import os
from typing import Any
from typing import Dict
import warnings

import aiohttp
import jsonschema
import pytest

from taxi_schemas import utils
from taxi_schemas.utils import http_client
from taxi_schemas.validators import config_validator

logger = logging.getLogger(__name__)


@pytest.mark.skipif(
    not os.environ.get('IS_TEAMCITY'), reason='Test works on build agent only',
)
@pytest.mark.parametrize(
    'env_name, env_url',
    [
        ('TESTING', 'http://config-schemas.taxi.tst.yandex.net'),
        ('PRODUCTION', 'http://config-schemas.taxi.yandex.net'),
    ],
)
@pytest.mark.nofilldb()
async def test_check_value(
        new_and_modified_config_path, common_definitions, env_name, env_url,
):
    await _check_config_value(
        new_and_modified_config_path, common_definitions, env_name, env_url,
    )


async def _check_config_value(path, common_definitions, env_name, env_url):
    config_schema = utils.load_yaml(path)

    _, file = os.path.split(path)
    config_name, _ = file.split('.', maxsplit=1)

    try:
        async with aiohttp.ClientSession() as session:
            client = http_client.BaseClient(session)
            values_by_service = await _get_values_by_service(
                client, env_url, config_name,
            )
    except utils.http_client.NotFoundError:
        return
    except utils.http_client.UnauthorizedError:
        warnings.warn(
            'TVM enabled for get config value handle', ResourceWarning,
        )
        return

    validators = config_validator.get_validators(
        config_schema, common_definitions,
    )
    for service, value in values_by_service.items():
        for validator in validators:
            try:
                validator(value)
            except (
                config_validator.ValidatorError,
                jsonschema.exceptions.ValidationError,
                jsonschema.exceptions.SchemaError,
            ) as exception:
                message_part = str(value)
                if service != 'general':
                    message_part = f'{message_part} for service {service}'
                pytest.fail(
                    f'Validation failed on {message_part} '
                    f'with error: {exception}',
                )


@pytest.fixture(scope='session', name='common_definitions')
def _common_definitions():
    return config_validator.get_common_definitions()


async def _get_values_by_service(
        client: http_client.BaseClient, base_url: str, name: str,
) -> Dict[str, Any]:
    config = await client.request('GET', f'{base_url}/v1/configs/{name}/')
    results = {'general': config['value']}
    if not config.get('services'):
        return results

    requests = []
    for service in config['services']:
        requests.append(
            client.request(
                'GET',
                f'{base_url}/v1/configs/{name}/',
                params={'service_name': service},
            ),
        )
    for result in await asyncio.gather(*requests, return_exceptions=True):
        if isinstance(result, Exception):
            logger.error('Error for get another values', exc_info=result)
            continue
        results[result['service_name']] = result['value']
    return results
