# pylint: disable=W0612
import pytest

from tests_tags.tags import acl_tools
from tests_tags.tags import constants
from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools as tools


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
async def test_get_all(taxi_tags):
    response = await taxi_tags.get('v1/topics')
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'name': 'topic0',
                'description': 'topic0_description',
                'is_financial': False,
            },
            {
                'name': 'topic1',
                'description': 'topic1_description',
                'is_financial': False,
            },
            {
                'name': 'topic2',
                'description': 'topic2_description',
                'is_financial': True,
            },
        ],
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags')
@pytest.mark.parametrize('is_financial', [True, False, None])
async def test_insert_topic(taxi_tags, pgsql, is_financial):
    url = 'v1/topics?topic=topic&description=topic_description'
    if is_financial is not None:
        url += '&is_financial={is_financial}'.format(
            is_financial='true' if is_financial else 'false',
        )

    response = await taxi_tags.post(url)
    assert response.status_code == 200

    topics = []
    assert response.json() == {'status': 'ok'}
    topics.append(
        {
            'id': 1,
            'name': 'topic',
            'description': 'topic_description',
            'is_financial': bool(is_financial),
        },
    )

    rows = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    assert rows == topics


@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
@pytest.mark.parametrize(
    'topic, is_financial, expected_code',
    [
        ('topic0', True, 403),
        ('topic0', False, 200),
        ('topic0', None, 200),
        ('topic2', False, 403),
        ('topic2', True, 200),
        pytest.param('a' * 256, False, 400, id='too_long_name'),
        ('', False, 400),
        ('абвгде', False, 400),
        ('-!?', False, 400),
    ],
)
async def test_double_insert_topic(
        taxi_tags, pgsql, topic, is_financial, expected_code,
):
    topics = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])

    url = 'v1/topics?topic=' + topic + '&description=description_overridden'
    if is_financial is not None:
        url += '&is_financial={is_financial}'.format(
            is_financial='true' if is_financial else 'false',
        )

    response = await taxi_tags.post(url)
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'status': 'ok'}
        index = next(i for i, row in enumerate(topics) if row['name'] == topic)
        topics[index]['description'] = 'description_overridden'
        topics[index]['is_financial'] = bool(is_financial)

    rows = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    assert rows == topics


@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
async def test_delete_non_exist(
        taxi_tags, pgsql, taxi_config, mockserver, acl_enabled,
):
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    response = await taxi_tags.delete(
        'v1/topics?topic=non_exist_topic', headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

    rows = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    assert rows == [
        {
            'id': 2000,
            'name': 'topic0',
            'description': 'topic0_description',
            'is_financial': False,
        },
        {
            'id': 2001,
            'name': 'topic1',
            'description': 'topic1_description',
            'is_financial': False,
        },
        {
            'id': 2002,
            'name': 'topic2',
            'description': 'topic2_description',
            'is_financial': True,
        },
    ]


@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
@pytest.mark.parametrize(
    'topic,expected_code', [('topic0', 400), ('topic2', 200)],
)
async def test_delete_topic(
        taxi_tags,
        pgsql,
        taxi_config,
        mockserver,
        topic,
        expected_code,
        acl_enabled,
):
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    topics = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    relations = tags_select.select_table_named(
        'meta.relations', 'topic_id', pgsql['tags'],
    )

    response = await taxi_tags.delete(
        'v1/topics?topic=' + topic, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        topic_id = next(item['id'] for item in topics if item['name'] == topic)
        topics = [item for item in topics if item['name'] != topic]
        relations = [
            item for item in relations if item['topic_id'] != topic_id
        ]

    rows = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    assert rows == topics
    rows = tags_select.select_table_named(
        'meta.relations', 'topic_id', pgsql['tags'],
    )
    assert rows == relations


@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
async def test_delete_topic_acl_prohibit(taxi_tags, mockserver, pgsql):
    _topic = 'topic0'
    topics = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    relations = tags_select.select_table_named(
        'meta.relations', 'topic_id', pgsql['tags'],
    )

    mock_acl = acl_tools.make_mock_acl_prohibited(
        mockserver, constants.TEST_LOGIN, [_topic], [_topic],
    )

    response = await taxi_tags.delete(
        'v1/topics?topic=' + _topic, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 403
    assert mock_acl.times_called == 1

    expected_message = f'acl prohibited topics: {_topic}'
    assert response.json()['message'] == expected_message

    rows = tags_select.select_table_named('meta.topics', 'id', pgsql['tags'])
    assert rows == topics
    rows = tags_select.select_table_named(
        'meta.relations', 'topic_id', pgsql['tags'],
    )
    assert rows == relations


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
@pytest.mark.parametrize(
    'parameters, status_code, message',
    [
        ('?tag_name=non_exist', 404, 'tag \'non_exist\' was not found'),
        ('?topic=non_exist', 404, 'topic \'non_exist\' was not found'),
        (
            '?tag_contains=acb&tag_name=tag_some',
            400,
            'one of tag_contains & tag_name parameter can be defined only',
        ),
    ],
)
async def test_get_items_failed(taxi_tags, parameters, status_code, message):
    response = await taxi_tags.get('v1/topics/items' + parameters)
    assert response.status_code == status_code
    assert response.json() == {'code': f'{status_code}', 'message': message}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    files=[
        'tags_topic_initial.sql',
        'tags_tags_extra.sql',
        'tags_relation_extra_rus.sql',
    ],
)
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': ['topic1'],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'tag_contains, tag_name',
    [
        (None, None),
        ('a', None),
        (' ', None),
        ('rus_т', None),
        (None, 'tag1'),
        (None, 'rus_тег'),
    ],
)
@pytest.mark.parametrize('topic', [None, 'topic0', 'rus_топик'])
@pytest.mark.parametrize('is_financial', [None, False, True])
@pytest.mark.parametrize('offset, limit', [(None, None), (0, 100), (1, 2)])
async def test_get_items(
        taxi_tags, tag_contains, tag_name, topic, is_financial, offset, limit,
):
    items = [
        {
            'topic': topic,
            'tag': tag,
            'is_financial': is_financial,
            'is_audited': is_audited,
        }
        for topic, tag, is_financial, is_audited in [
            ('topic0', 'tag0', False, False),
            ('topic0', 'tag1', False, False),
            ('topic1', 'tag2', False, True),
            ('topic1', 'bla-bla', False, True),
            ('topic2', 'bla-bla', True, True),
            ('topic2', 'make me laugh', True, True),
            ('topic2', 'test1', True, True),
            ('topic2', 'seach_text', True, True),
            ('topic2', 'space space', True, True),
            ('rus_топик', 'rus_тег', False, False),
        ]
    ]

    url = 'v1/topics/items'
    parameters = []
    if tag_contains is not None:
        parameters.append('tag_contains=' + tag_contains)
    if tag_name is not None:
        parameters.append('tag_name=' + tag_name)
    if topic is not None:
        parameters.append('topic=' + topic)
    if is_financial is not None:
        parameters.append('is_financial=' + str(is_financial).lower())
    if offset is not None:
        parameters.append('offset=' + str(offset))
    if limit is not None:
        parameters.append('limit=' + str(limit))
    if parameters:
        url += '?' + '&'.join(parameters)

    result = []
    for item in items:
        if tag_contains is not None and item['tag'].find(tag_contains) == -1:
            continue
        if tag_name is not None and item['tag'] != tag_name:
            continue
        if topic is not None and item['topic'] != topic:
            continue
        if is_financial is not None and item['is_financial'] != is_financial:
            continue
        result.append(item)
    offset = offset or 0
    limit = limit or 10

    response = await taxi_tags.get(url)
    assert response.status_code == 200
    assert response.json() == {
        'items': result[offset : offset + limit],
        'offset': offset,
        'limit': limit,
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_topics(
            [
                tools.Topic(2000, 'topic', False),
                tools.Topic(2001, 'existing', False),
            ],
        ),
        'insert into meta.endpoints (topic_id, tvm_service_name, url) '
        'values (2001, \'tags\', \'some_url\');',
    ],
)
@pytest.mark.parametrize(
    'expected_code, endpoint_response, endpoint_code, topic_name, '
    'endpoint_url',
    [
        (
            200,
            '{"details": {}, "permission": "allowed"}',
            200,
            'topic',
            '/v1/webhooks/topic',
        ),
        # endpoint exists
        (
            409,
            '{"details": {}, "permission": "allowed"}',
            200,
            'existing',
            '/v1/webhooks/topic',
        ),
        # absent topic
        (
            404,
            '{"details": {}, "permission": "allowed"}',
            200,
            'absent',
            '/v1/webhooks/topic',
        ),
        # endpoint 40x
        (400, 'Bad Request', 400, 'topic', '/v1/webhooks/topic'),
        (400, 'Unauthorized', 401, 'topic', '/v1/webhooks/topic'),
        (400, 'Forbidden', 403, 'topic', '/v1/webhooks/topic'),
        (400, 'Not Found', 404, 'topic', '/v1/webhooks/topic'),
        # endpoint 500
        (400, 'Internal Server Error', 500, 'topic', '/v1/webhooks/topic'),
        # timeout
        (
            400,
            '{"details": {}, "permission": "allowed"}',
            200,
            'topic',
            '/v1/webhooks/timeout',
        ),
        # unreachable
        (
            400,
            '{"details": {}, "permission": "allowed"}',
            200,
            'topic',
            '/v1/webhooks/wrong_host',
        ),
    ],
)
async def test_endpoint(
        taxi_tags,
        mockserver,
        expected_code,
        endpoint_response,
        endpoint_code,
        topic_name,
        endpoint_url,
):
    @mockserver.json_handler('/v1/webhooks/topic')
    def endpoint_topic(_):
        return mockserver.make_response(endpoint_response, endpoint_code)

    @mockserver.json_handler('/v1/webhooks/timeout')
    def endpoint_timeout(_):
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/v1/webhooks/wrong_host')
    def endpoint_unreachable(_):
        raise mockserver.NetworkError()

    url = f'v1/topics/{topic_name}/endpoint'
    endpoint_url = mockserver.url(endpoint_url)
    data = {'tvm_service_name': 'tags', 'url': endpoint_url}
    response = await taxi_tags.put(url, data)
    assert response.status_code == expected_code
