import copy
from typing import NamedTuple
from typing import Optional
import uuid

import pytest

SWAGGER_SCHEMA_PING = {
    'swagger': '2.0',
    'info': {'version': '1.0', 'title': 'hello'},
    'paths': {
        '/ping': {
            'get': {
                'operationId': 'Ping',
                'responses': {'200': {'description': 'OK'}},
            },
        },
    },
}


class Params(NamedTuple):
    taxi_middlewares: dict
    tvm_enabled: bool
    expected_ping_tvm: Optional[bool]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                taxi_middlewares={'tvm': True},
                tvm_enabled=True,
                expected_ping_tvm=True,
            ),
            id='tvm_tvm-ping',
        ),
        pytest.param(
            Params(
                taxi_middlewares={'tvm': False},
                tvm_enabled=True,
                expected_ping_tvm=False,
            ),
            id='tvm_no-tvm-ping',
        ),
        pytest.param(
            Params(
                taxi_middlewares={'tvm': False},
                tvm_enabled=False,
                expected_ping_tvm=None,
            ),
            id='no-tvm_none-tvm-ping',
        ),
    ],
)
async def test_tvm_ping(generate_service, params):
    schema_copy = copy.deepcopy(SWAGGER_SCHEMA_PING)
    if params.taxi_middlewares:
        schema_copy['paths']['/ping']['get'][
            'x-taxi-middlewares'
        ] = params.taxi_middlewares
    web_cfg: Optional[dict] = None
    if params.tvm_enabled:
        web_cfg = {'web': {'tvm': {'service_name': 'test_package'}}}
    importer = generate_service(
        package_name='test_package' + '_' + uuid.uuid4().hex,
        swagger_schema=schema_copy,
        unit_plugins_cfg_by_unit_name=web_cfg,
    )
    path_extras = importer.middlewares_context().PATHS_EXTRAS
    if params.expected_ping_tvm is None:
        assert not hasattr(path_extras[('/ping', 'GET')], 'tvm')
        assert not hasattr(path_extras[('/ping/', 'GET')], 'tvm')
    else:
        assert path_extras[('/ping', 'GET')].tvm == params.expected_ping_tvm
        assert path_extras[('/ping/', 'GET')].tvm == params.expected_ping_tvm
