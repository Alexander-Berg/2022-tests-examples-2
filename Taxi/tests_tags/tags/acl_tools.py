import json
from typing import List

ACL_PERMISSION_ALLOWED = 'allowed'
ACL_PERMISSION_PROHIBITED = 'prohibited'


async def toggle_acl(taxi_tags, config, acl_enabled: bool):
    config.set_values(dict(TAGS_ACL_TOPICS_ENABLED=acl_enabled))
    await taxi_tags.invalidate_caches()


def make_mock_acl_allowed(mockserver):
    @mockserver.json_handler('/tags-topics/v1/permissions/check')
    async def mock_permission_check(request):
        data = json.loads(request.get_data())
        assert data['login']
        assert data['topics']
        return mockserver.make_response(
            json.dumps({'permission': 'allowed'}), status=200,
        )

    return mock_permission_check


async def toggle_acl_and_mock_allowed(
        taxi_tags, config, mockserver, acl_enabled: bool,
):
    await toggle_acl(taxi_tags, config, acl_enabled)
    if acl_enabled:
        make_mock_acl_allowed(mockserver)


def make_mock_acl_prohibited(
        mockserver,
        expected_login: str,
        expected_topics: List[str],
        prohibited_topics: List[str] = None,
):
    @mockserver.json_handler('/tags-topics/v1/permissions/check')
    def mock_permission_check(request):
        _prohibited_topics = prohibited_topics or []
        data = json.loads(request.get_data())
        assert data['login'] == expected_login
        assert data['topics'] == expected_topics
        return mockserver.make_response(
            json.dumps(
                {
                    'permission': 'prohibited',
                    'details': {'prohibited_topics': _prohibited_topics},
                },
            ),
            status=200,
        )

    return mock_permission_check
