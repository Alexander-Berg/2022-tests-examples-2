# pylint: disable=redefined-outer-name
import pytest

import yanformator_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['yanformator_bot.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def config_schemas_mockserver(mockserver):
    @mockserver.json_handler('configs-admin/v1/configs/list/')
    def _config_schemas(_):
        return {
            'items': [
                {
                    'group': 'DISPATCH_BUFFER',
                    'name': 'DISPATCH_BUFFER_SETTINGS',
                    'description': '',
                    'tags': [],
                    'ticket_required': False,
                    'is_fallback': False,
                    'has_overrides': False,
                    'default': {
                        'remove_orders_consumer': {
                            'enabled': False,
                            'chunk_size': 100,
                            'queue_timeout_ms': 100,
                            'config_poll_period_ms': 1000,
                        },
                    },
                },
            ],
        }


@pytest.fixture(autouse=True)
def abc_mockserver(mockserver):
    @mockserver.json_handler('/abc/api/v4/duty/on_duty/')
    def _config_schemas(_):
        return [{'id': 1, 'person': {'login': 'alex-tsarkov'}}]


@pytest.fixture(autouse=True)
def staff_mockserver(mockserver):
    @mockserver.json_handler('staff/v3/persons')
    def _persons(_):
        return {
            'result': [
                {
                    'login': 'alex-tsarkov',
                    'accounts': [{'type': 'telegram', 'value': 'tsarkov'}],
                },
            ],
        }
