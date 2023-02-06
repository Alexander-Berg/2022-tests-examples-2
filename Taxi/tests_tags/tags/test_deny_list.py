from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_select as select
from tests_tags.tags import tags_tools as tools

_PROVIDER = tools.Provider.from_id(1000, True)


def _make_deny_list_config(
        provider_policies: Optional[Dict[str, str]] = None,
        provider: Optional[str] = None,
        policy: Optional[str] = None,
        unit_name='tags',
):
    if provider_policies is None:
        provider_policies = {}
    if provider and policy:
        provider_policies[provider] = policy
    return {unit_name: {'upload': provider_policies}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_PROVIDER]),
        tools.insert_service_providers(
            [(_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
    ],
)
@pytest.mark.parametrize(
    'query, data',
    [
        pytest.param(
            'v1/upload?provider_id={id}&confirmation_token=no_token'.format(
                id=_PROVIDER.name,
            ),
            {
                'tags': [tools.Tag.get_data('tag_name', 'driver_identifier')],
                'merge_policy': 'append',
                'entity_type': 'dbid_uuid',
            },
            id='v1/upload',
        ),
        pytest.param(
            'v2/upload',
            {
                'provider_id': _PROVIDER.name,
                'append': [
                    {
                        'entity_type': 'dbid_uuid',
                        'tags': [
                            tools.Tag.get_tag_data(
                                'tag_name', 'driver_identifier',
                            ),
                        ],
                    },
                ],
            },
            id='v2/upload',
        ),
        pytest.param(
            'v1/assign',
            {
                'provider': _PROVIDER.name,
                'entities': [
                    {
                        'type': 'dbid_uuid',
                        'name': 'driver_identifier',
                        'tags': {'tag_name': {}},
                    },
                ],
            },
            id='v1/assign',
        ),
    ],
)
@pytest.mark.parametrize(
    'policy, expected_code', [('shadow_ban', 200), ('forbidden', 403)],
)
async def test_deny_list(
        taxi_tags: Any,
        taxi_config: Any,
        pgsql: Any,
        query: str,
        data: Dict[str, Any],
        policy: str,
        expected_code: int,
):
    taxi_config.set_values(
        dict(
            TAGS_DENY_LIST=_make_deny_list_config(
                provider=_PROVIDER.name, policy=policy,
            ),
        ),
    )
    await taxi_tags.invalidate_caches()

    response = await taxi_tags.post(
        query, data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == expected_code

    assert [] == select.select_table_named(
        'state.tags_customs', 'id', pgsql['tags'],
    )
    assert [] == select.select_table_named(
        'state.tags', 'revision', pgsql['tags'],
    )
    assert [] == select.select_table_named(
        'service.request_results', 'confirmation_token', pgsql['tags'],
    )
