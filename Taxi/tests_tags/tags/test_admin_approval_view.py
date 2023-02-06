import datetime
from typing import Any
from typing import Dict

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)


def _verify_answer(got: Dict[str, Any], should_be: Dict[str, Any]):
    def sorter(k):
        return k['name']

    got_tags = sorted(got['tags'], key=sorter)
    should_be_tags = sorted(should_be['tags'], key=sorter)
    assert len(got_tags) == len(should_be_tags)
    for (g_item, s_item) in zip(got_tags, should_be_tags):
        assert g_item['name'] == s_item['name']
        assert sorted(g_item['providers'], key=sorter) == sorted(
            s_item['providers'], key=sorter,
        )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(0, 'tag0'),
                tags_tools.TagName(1, 'tag1'),
                tags_tools.TagName(2, 'financial_tag'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider(0, 'yql_wo_tag', '', True),
                tags_tools.Provider(1, 'base_service', '', True),
                tags_tools.Provider(2, 'yql_w_tag', '', True),
                tags_tools.Provider(3, 'audited_service', '', True),
                tags_tools.Provider(4, 'manual_provider', '', True),
                tags_tools.Provider(5, 'disabled_provider', '', False),
            ],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='wo_tag',
                    provider_id=0,
                    tags=[],
                    author='author',
                    changed=_NOW,
                    created=_NOW,
                ),
                yql_tools.Query(
                    name='w_tag',
                    provider_id=2,
                    tags=['tag1'],
                    author='author',
                    created=_NOW,
                    changed=_NOW,
                ),
            ],
        ),
        tags_tools.insert_service_providers(
            [
                (1, ['base_service'], 'base'),
                (3, ['audited_service'], 'audited'),
            ],
        ),
        tags_tools.insert_entities(
            [tags_tools.Entity(0, 'udid0'), tags_tools.Entity(1, 'udid1')],
        ),
        tags_tools.insert_topics([tags_tools.Topic(0, 'financial', True)]),
        tags_tools.insert_relations([tags_tools.Relation(2, 0)]),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(0, 0, 0),
                tags_tools.Tag(0, 0, 1),
                tags_tools.Tag(0, 1, 0),
                tags_tools.Tag(1, 2, 0),
                tags_tools.Tag(1, 3, 0),
                tags_tools.Tag(1, 4, 0),
                tags_tools.Tag(
                    1, 4, 1, _NOW, _MINUTE_AGO,
                ),  # outdated tags_tools.Tag
                tags_tools.Tag(1, 5, 0),  # disabled tags_tools.Provider
                tags_tools.Tag(2, 4, 0),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'check_strictness, expected_manual_provider_tags_count',
    [('account_active', 1), ('account_all', 2)],
)
async def test_add_tags(
        taxi_tags,
        check_strictness: str,
        expected_manual_provider_tags_count: int,
        taxi_config,
):
    taxi_config.set_values(
        dict(TAGS_PROVIDERS_CHECK_STRICTNESS=check_strictness),
    )
    await taxi_tags.invalidate_caches()

    response = await taxi_tags.post(
        'v2/admin/topics/items/approval_view',
        {
            'topic': 'financial',
            'tags': ['tag0', 'tag1', 'financial_tag', 'tag2'],
        },
    )
    assert response.status_code == 200

    should_be = {
        'tags': [
            {
                'name': 'tag0',
                'providers': [
                    {
                        'name': 'yql_wo_tag',
                        'tags_count': 2,
                        'level': 'prohibited',
                        'type': 'yql',
                        'yql_name': 'wo_tag',
                    },
                    {
                        'name': 'base_service',
                        'tags_count': 1,
                        'type': 'service',
                        'level': 'prohibited',
                    },
                ],
            },
            {
                'name': 'tag1',
                'providers': [
                    {
                        'name': 'yql_w_tag',
                        'tags_count': 1,
                        'level': 'approval_required',
                        'type': 'yql',
                        'yql_name': 'w_tag',
                    },
                    {
                        'name': 'audited_service',
                        'tags_count': 1,
                        'level': 'allowed',
                        'type': 'service',
                    },
                    {
                        'name': 'manual_provider',
                        'tags_count': expected_manual_provider_tags_count,
                        'level': 'approval_required',
                        'type': 'manual',
                    },
                    {
                        'name': 'disabled_provider',
                        'tags_count': 1,
                        'level': 'approval_required',
                        'type': 'manual',
                    },
                ],
            },
            {
                'name': 'financial_tag',
                'providers': [
                    {
                        'level': 'allowed',
                        'name': 'manual_provider',
                        'tags_count': 1,
                        'type': 'manual',
                    },
                ],
            },
            {'name': 'tag2', 'providers': []},
        ],
    }

    _verify_answer(response.json(), should_be)
