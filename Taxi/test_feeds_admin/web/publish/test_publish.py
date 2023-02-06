from aiohttp import web
import pytest

from test_feeds_admin import const


CURRENT_SCHEDULE = {
    'id': const.UUID_1,
    'service': 'eats-promotions-story',
    'experiment': 'my_experiment',
    'schedule': {
        'recurrence': 'once',
        'ttl_auto': True,
        'first_publish_at': '2019-08-26T00:00:00+0300',
        'last_publish_at': '2020-08-26T00:00:00+0300',
    },
}


LONG_TIME_PASSED_SCHEDULE = {
    'id': const.UUID_1,
    'service': 'eats-promotions-story',
    'experiment': 'my_experiment',
    'schedule': {
        'recurrence': 'once',
        'ttl_auto': True,
        'first_publish_at': '2000-01-01T00:00:00+0300',
        'last_publish_at': '2000-10-01T00:00:00+0300',
    },
}


FUTURE_SCHEDULE = {
    'id': const.UUID_1,
    'service': 'eats-promotions-story',
    'experiment': 'my_experiment',
    'schedule': {
        'recurrence': 'once',
        'ttl_auto': True,
        'first_publish_at': '2050-01-01T00:00:00+0300',
        'last_publish_at': '2050-10-01T00:00:00+0300',
    },
}

YQL_SCHEDULE = {
    'id': const.UUID_2,
    'service': 'eats-promotions-story',
    'schedule': {
        'recurrence': 'once',
        'ttl_auto': True,
        'first_publish_at': '2019-08-26T00:00:00+0300',
        'last_publish_at': '2020-08-26T00:00:00+0300',
    },
    'recipients': {
        'recipient_type': 'yql',
        'yql_link': (
            'https://yql.yandex-team.ru/Operations/'
            'XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo='
        ),
    },
}


TOO_MANY_RECIPIENTS_SCHEDULE = {
    'id': const.UUID_3,
    'service': 'eats-promotions-story',
    'experiment': 'my_experiment',
    'schedule': {
        'recurrence': 'once',
        'ttl_auto': True,
        'first_publish_at': '2019-08-26T00:00:00+0300',
        'last_publish_at': '2020-08-26T00:00:00+0300',
    },
}


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_publish.sql'])
@pytest.mark.parametrize(
    ['params', 'status'],
    [(CURRENT_SCHEDULE, 200), (LONG_TIME_PASSED_SCHEDULE, 400)],
)
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
)
@pytest.mark.now('2019-08-27T10:00:00')
async def test_publish(
        web_app_client, testpoint, patch, mock_feeds, params, status,
):  # pylint: disable=W0612
    @mock_feeds('/v1/batch/create')
    async def handler_add(request):  # pylint: disable=W0612
        item = request.json['items'][0]
        assert item['package_id'] == params['id']
        assert item['request_id'].split('_')[0] == params['id']
        return web.json_response(
            data={
                'items': [
                    {
                        'service': item['service'],
                        'feed_ids': {item['service']: 'feeds_feed_id'},
                        'filtered': [],
                    },
                ],
            },
        )

    @patch('feeds_admin.views.run_history.schedule_run')
    async def schedule(*args, **kwargs):
        assert False

    @testpoint('actions::create')
    def actions_create(data):
        pass

    publish_response = await web_app_client.post(
        '/v1/eats-promotions/publish', json=params,
    )
    assert publish_response.status == status


# FUTURE_SCHEDULE and TOO_MANY_RECIPIENTS_SCHEDULE require recipients_groups,
# so they are disabled until creation of general /v1/publish handler
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_publish.sql'])
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
)
@pytest.mark.parametrize(
    ['params'],
    # [(FUTURE_SCHEDULE,), (YQL_SCHEDULE,), (TOO_MANY_RECIPIENTS_SCHEDULE,)],
    [(YQL_SCHEDULE,)],
)
@pytest.mark.now('2019-08-27T10:00:00')
async def test_publish_through_stq(
        web_app_client, patch, mock_feeds, params,
):  # pylint: disable=W0612
    @mock_feeds('/v1/batch/create')
    async def handler_add(request):  # pylint: disable=W0612
        assert False

    publish_response = await web_app_client.post(
        '/v1/eats-promotions/publish', json=params,
    )
    assert publish_response.status == 200


@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        'feeds-sample': {
            'max_channels_for_immediate_publish': 3,
            'feed_id_source': 'feeds-admin',
        },
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_publish.sql'])
@pytest.mark.now('2019-08-27T10:00:00')
async def test_publish_with_same_feed_id(
        web_app_client, mockserver, stq_runner, patch,
):
    params = {'id': const.UUID_4, 'service': 'feeds-sample'}

    @mockserver.handler('feeds/v1/batch/create')
    async def create(request):
        item = request.json['items'][0]
        assert item.get('feed_id') == params['id']
        assert item.get('channels') is None
        return web.json_response(
            data={
                'items': [
                    {
                        'service': item['service'],
                        'feed_ids': {},
                        'filtered': [],
                    },
                ],
            },
        )

    @mockserver.handler('feeds/v1/update')
    async def update(request):
        item = request.json
        assert item['feed_id'] == params['id']
        return web.json_response(
            data={
                'items': [
                    {
                        'service': item['service'],
                        'feed_ids': {},
                        'filtered': [],
                    },
                ],
            },
        )

    await stq_runner.feeds_admin_send.call(
        args=(const.UUID_4,), kwargs={'run_id': 50},
    )
    assert create.times_called == 1
    assert update.times_called == 1
