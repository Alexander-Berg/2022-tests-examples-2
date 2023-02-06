from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from testsuite.utils import ordered_object

from tests_tags.tags import acl_tools
from tests_tags.tags import constants


_NO_TOPIC_TAG = 'no_topic_tag'
_FINANCE_TOPIC_TAG = 'finance_topic_tag'
_TOPIC = 'topic'
_TOPIC_TAG = 'topic_tag0'
_TOPIC_TAG_1 = 'topic_tag1'
_MULTI_TOPIC_TAG = 'multi_topic_tag'
_AUDITED_TAG = 'audited_tag'
_AUDITED_TOPIC = 'audited_topic'
_FINANCE_TOPIC = 'finance_topic'


def _body(tags: Optional[List[str]], topics: Optional[List[str]] = None):
    _dict: Dict[str, List[str]] = {}
    if tags is not None:
        _dict['tags'] = tags
    if topics is not None:
        _dict['topics'] = topics
    return _dict


def _make_topic_permission(
        topic: str,
        tags: Optional[List[str]],
        is_financial: bool,
        acl: str,
        is_audited: Optional[bool] = None,
):
    if is_audited is None:
        is_audited = is_financial
    _dict = {
        'topic': topic,
        'is_financial': is_financial,
        'is_audited': is_audited,
        'acl': acl,
    }
    if tags is not None:
        _dict['tags'] = tags

    return _dict


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topics_initial.sql'])
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': [_AUDITED_TOPIC],
                'tag_names': [_AUDITED_TAG],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'acl_enabled, tags, topics, expected_topics, '
    'prohibited_topics, expected_response',
    [
        pytest.param(
            True,
            [_NO_TOPIC_TAG],
            None,
            [],
            [],
            {'topics': []},
            id='empty response for tags without topics',
        ),
        pytest.param(
            True,
            [_FINANCE_TOPIC_TAG, _TOPIC_TAG],
            None,
            [_FINANCE_TOPIC, _TOPIC],
            [],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=[_FINANCE_TOPIC_TAG],
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_TOPIC_TAG],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='topic finance and not finance allowed',
        ),
        pytest.param(
            True,
            [_FINANCE_TOPIC_TAG, _TOPIC_TAG],
            None,
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC, _FINANCE_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=[_FINANCE_TOPIC_TAG],
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_TOPIC_TAG],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                ],
            },
            id='topic finance and not finance prohibited',
        ),
        pytest.param(
            False,
            [_FINANCE_TOPIC_TAG, _TOPIC_TAG],
            None,
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC, _FINANCE_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=[_FINANCE_TOPIC_TAG],
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_TOPIC_TAG],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='topic finance and not finance prohibited, but acl disabled',
        ),
        pytest.param(
            True,
            [_MULTI_TOPIC_TAG],
            None,
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=[_MULTI_TOPIC_TAG],
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_MULTI_TOPIC_TAG],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                ],
            },
            id='tags in multiple topics one prohibited, one allowed',
        ),
        pytest.param(
            True,
            [_TOPIC_TAG_1, _TOPIC_TAG],
            None,
            [_TOPIC],
            [],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_TOPIC_TAG, _TOPIC_TAG_1],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='topic with multiple tags',
        ),
        pytest.param(
            True,
            None,
            [_TOPIC, _FINANCE_TOPIC],
            [_FINANCE_TOPIC, _TOPIC],
            [],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=None,
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=None,
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='allowed topics without tags',
        ),
        pytest.param(
            True,
            None,
            [_TOPIC, _FINANCE_TOPIC],
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=None,
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=None,
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='prohibited and allowed topics without tags',
        ),
        pytest.param(
            True,
            [_MULTI_TOPIC_TAG],
            [_TOPIC],
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=[_MULTI_TOPIC_TAG],
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_MULTI_TOPIC_TAG],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                ],
            },
            id='tags and topics request same topic',
        ),
        pytest.param(
            True,
            [_TOPIC_TAG_1],
            [_FINANCE_TOPIC],
            [_FINANCE_TOPIC, _TOPIC],
            [_TOPIC, _FINANCE_TOPIC],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_FINANCE_TOPIC,
                        tags=None,
                        is_financial=True,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                    _make_topic_permission(
                        topic=_TOPIC,
                        tags=[_TOPIC_TAG_1],
                        is_financial=False,
                        acl=acl_tools.ACL_PERMISSION_PROHIBITED,
                    ),
                ],
            },
            id='tags and topics request',
        ),
        pytest.param(
            True,
            ['random_tag_name'],
            [_AUDITED_TOPIC],
            [_AUDITED_TOPIC],
            [],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_AUDITED_TOPIC,
                        tags=None,
                        is_financial=False,
                        is_audited=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='audited topic',
        ),
        pytest.param(
            True,
            [_AUDITED_TAG],
            None,
            [_AUDITED_TOPIC],
            [],
            {
                'topics': [
                    _make_topic_permission(
                        topic=_AUDITED_TOPIC,
                        tags=[_AUDITED_TAG],
                        is_financial=False,
                        is_audited=True,
                        acl=acl_tools.ACL_PERMISSION_ALLOWED,
                    ),
                ],
            },
            id='find audited topic by tag name',
        ),
    ],
)
async def test_tags_topics_permissions(
        taxi_tags,
        pgsql,
        tags: Optional[List[str]],
        topics: Optional[List[str]],
        expected_topics: List[str],
        prohibited_topics: List[str],
        expected_response: Dict[str, Any],
        mockserver,
        taxi_config,
        acl_enabled: bool,
):
    await acl_tools.toggle_acl(taxi_tags, taxi_config, acl_enabled)

    acl_tools.make_mock_acl_prohibited(
        mockserver, constants.TEST_LOGIN, expected_topics, prohibited_topics,
    )

    response = await taxi_tags.post(
        'v1/admin/tags/topics_permissions',
        _body(tags=tags, topics=topics),
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == 200

    response_data = response.json()
    ordered_object.assert_eq(response_data, expected_response, ['topics'])


@pytest.mark.nofilldb()
@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.parametrize(
    'tags, topics, error_code, error_text',
    [
        pytest.param(
            None,
            None,
            400,
            'provide any of [tags, topics] arguments',
            id='no tags and no topics',
        ),
        pytest.param(
            None,
            ['unknown_topic'],
            404,
            'topic unknown_topic not found',
            id='unknown_topic',
        ),
    ],
)
async def test_tags_topics_permissions_validate(
        taxi_tags,
        pgsql,
        tags: Optional[List[str]],
        topics: Optional[List[str]],
        error_code: int,
        error_text: str,
        taxi_config,
):
    response = await taxi_tags.post(
        'v1/admin/tags/topics_permissions',
        _body(tags=tags, topics=topics),
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == error_code
    assert response.json() == {'code': str(error_code), 'message': error_text}


@pytest.mark.nofilldb()
@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.parametrize(
    'tags, topics, error_code',
    [
        pytest.param([], None, 400, id='empty tags'),
        pytest.param(None, [], 400, id='empty topics'),
    ],
)
async def test_tags_topics_permissions_validate_codegen(
        taxi_tags,
        pgsql,
        tags: Optional[List[str]],
        topics: Optional[List[str]],
        error_code: int,
        taxi_config,
):
    response = await taxi_tags.post(
        'v1/admin/tags/topics_permissions',
        _body(tags=tags, topics=topics),
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == error_code
    assert response.json()['code'] == '400'
