import datetime

import bson
import pytest

from tests_ivr_dispatcher import utils


TEST_ORDER_ID = '1543_order_id'
TEST_TAXI_PHONE = '2128700'


def _fetch_order_stats(mongodb, order_id):
    return mongodb.ivr_disp_order_stats.find_one({'_id': order_id})


def _fetch_order_events(mongodb, order_id):
    return mongodb.ivr_disp_order_events.find_one({'_id': order_id})


def _extract_event(order_events, index):
    return next(
        (
            event
            for event in order_events['events']
            if event['event_index'] == index
        ),
    )


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_normal_workflow(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
):
    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert mock_octonode.octonode.times_called == 1


@pytest.mark.pgsql('ivr_api', files=['inbound_number.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.IVR_SETTINGS_NO_DISP,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        TEST_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
            'tags': ['outbound_calls_forbidden'],
        },
    },
)
@pytest.mark.parametrize(
    ['order_id', 'inbound_number', 'result'],
    [
        [
            utils.DEFAULT_ORDER_ID,
            utils.DEFAULT_TAXI_PHONE,
            utils.DEFAULT_TAXI_PHONE,
        ],
        [TEST_ORDER_ID, TEST_TAXI_PHONE, '2128710'],
    ],
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_outbound_forbidden(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        order_id,
        inbound_number,
        result,
):
    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': order_id,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert mock_octonode.octonode.times_called == 1
    request = mock_octonode.octonode.next_call()['request'].json
    params = request['script']['steps']['start']['parameters']
    assert params['calling_number'] == result


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_user_cancel(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
):
    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_CANCEL_BY_USER,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not stq.ivr_status_call.times_called
    assert not stq.ivr_sms_sending.times_called
    assert not mock_octonode.octonode.times_called


@pytest.mark.parametrize(
    ['still_pending', 'created_triggered_first_time'],
    [[True, True], [True, False], [False, True], [False, False]],
)
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [300],
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_on_search_workflow(
        stq_runner,
        mockserver,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        created_triggered_first_time,
        load_json,
        still_pending,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        if still_pending:
            response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    kwargs = {
        'order_id': utils.DEFAULT_ORDER_ID,
        'event_key': None,
        'event_reason': utils.CREATE_REASON,
        'event_index': 0,
        'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
    }

    # Simulate, that we already processed create, sleep and wake_up
    if not created_triggered_first_time:
        mongodb.ivr_disp_order_events.update_one(
            {'_id': utils.DEFAULT_ORDER_ID},
            {
                '$push': {
                    'events': {
                        'event_id': (
                            '9b0ef3c5398b3e07b59f03110563479d_create_0'
                        ),
                        'event_key': kwargs['event_reason'],
                        'event_index': kwargs['event_index'],
                        'event_created': kwargs['event_created'],
                    },
                },
            },
            upsert=True,
        )

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID, kwargs=kwargs,
    )

    if not still_pending and not created_triggered_first_time:
        assert not stq.ivr_status_call.times_called
        assert not mock_octonode.octonode.times_called
        return

    if still_pending or created_triggered_first_time:
        # at first time, we always reschedule task
        # and when we wake up, we take a decision
        # to reschedule one more time or not
        assert stq.ivr_status_call.times_called == 1
    else:
        assert not stq.ivr_status_call.times_called

    assert mock_octonode.octonode.times_called == int(
        not created_triggered_first_time,
    )

    assert not stq.ivr_sms_sending.times_called


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [300],
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_on_search_preordered(
        stq_runner,
        mockserver,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        response['fields']['order']['preorder_request_id'] = 'tadada'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    kwargs = {
        'order_id': utils.DEFAULT_ORDER_ID,
        'event_key': None,
        'event_reason': utils.CREATE_REASON,
        'event_index': 0,
        'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
    }
    # Simulate, that we already processed create, sleep and wake_up
    mongodb.ivr_disp_order_events.update_one(
        {'_id': utils.DEFAULT_ORDER_ID},
        {
            '$push': {
                'events': {
                    'event_id': '9b0ef3c5398b3e07b59f03110563479d_create_0',
                    'event_key': kwargs['event_reason'],
                    'event_index': kwargs['event_index'],
                    'event_created': kwargs['event_created'],
                },
            },
        },
        upsert=True,
    )
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID, kwargs=kwargs,
    )

    assert not stq.ivr_status_call.times_called
    assert not mock_octonode.octonode.times_called
    assert not stq.ivr_sms_sending.times_called


@pytest.mark.parametrize('task_was_triggered_before', [True, False])
@pytest.mark.config(
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=0,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': False,
        'wake_up_intervals': [300],
    },
)
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:05:00')
async def test_on_search_disabled(
        stq_runner,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        task_was_triggered_before,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    kwargs = {
        'order_id': utils.DEFAULT_ORDER_ID,
        'event_key': None,
        'event_reason': utils.CREATE_REASON,
        'event_index': 0,
        'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
    }
    if task_was_triggered_before:
        # simulate that was triggerd and processed earliear
        # to test behaviour of tasks, when we disable config
        mongodb.ivr_disp_order_events.update_one(
            {'_id': utils.DEFAULT_ORDER_ID},
            {
                '$push': {
                    'events': {
                        'event_id': (
                            '9b0ef3c5398b3e07b59f03110563479d_create_0'
                        ),
                        'event_key': kwargs['event_reason'],
                        'event_index': kwargs['event_index'],
                        'event_created': kwargs['event_created'],
                    },
                },
            },
            upsert=True,
        )

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID, kwargs=kwargs,
    )
    assert not stq.ivr_status_call.times_called
    assert not mock_octonode.octonode.times_called
    assert not stq.ivr_sms_sending.times_called


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.config(IVR_STATUS_CALL_MAX_EVENT_CUTOFF=1800)
async def test_ivr_status_call_event_expired(
        stq_runner,
        taxi_ivr_dispatcher,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2018, 12, 31, 23, 29, 0, 0),
        },
    )


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.parametrize(
    'db_filled',
    (
        pytest.param(False, id='db is empty'),
        pytest.param(
            True,
            id='db is filled',
            marks=pytest.mark.filldb(ivr_disp_order_stats='already_filled'),
        ),
    ),
)
async def test_ivr_status_call_fetch_stats_from_db(
        stq_runner,
        mock_order_core,
        mock_user_api,
        db_filled,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    external_api_called = int(not db_filled)  # if db filled then 0
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert (
        mock_order_core.order_core.times_called == external_api_called + 1
    )  # one is for order_state fetching
    assert (
        mock_user_api.retrieve_personal_id.times_called == external_api_called
    )


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_adding_new_event_to_empty_db(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mongodb,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    order_stats = _fetch_order_stats(mongodb, utils.DEFAULT_ORDER_ID)
    assert order_stats
    assert order_stats['_id'] == utils.DEFAULT_ORDER_ID

    order_events = _fetch_order_events(mongodb, utils.DEFAULT_ORDER_ID)
    assert order_events
    assert order_events.get('events')
    event = order_events['events'][0]
    assert event['event_index'] == 0
    assert event['event_key'] == utils.HANDLE_DRIVING
    assert event['event_created'] == datetime.datetime(2019, 1, 1, 0, 0, 0, 0)


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.filldb(ivr_disp_order_events='already_filled')
async def test_adding_new_event_to_filled_db(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mongodb,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_WAITING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    order_events = _fetch_order_events(mongodb, utils.DEFAULT_ORDER_ID)
    assert order_events
    assert len(order_events['events']) == 2

    event = _extract_event(order_events, 1)
    assert event['event_index'] == 1
    assert event['event_key'] == utils.HANDLE_WAITING


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.filldb(ivr_disp_order_events='already_filled')
async def test_event_is_not_newest(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mongodb,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_WAITING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2016, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called


@pytest.mark.pgsql('ivr_api', files=['notification_already_sent.sql'])
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.filldb(ivr_disp_order_stats='already_filled')
@pytest.mark.filldb(ivr_disp_order_events='already_filled')
async def test_already_processed(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_save_session_worker_pair(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mongodb,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        pgsql,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )

    # Fetch session_id
    order_events = mongodb.ivr_disp_order_events.find_one(
        {'_id': utils.DEFAULT_ORDER_ID},
    )
    events = order_events['events']
    assert len(events) == 1
    event_id = events[0]['event_id']
    db = pgsql['ivr_api']
    cursor = db.cursor()
    cursor.execute(
        f'SELECT id FROM ivr_api.notifications WHERE event_id = %s;',
        (event_id,),
    )
    notification_id = cursor.fetchone()[0]

    doc = mongodb.ivr_disp_sessions.find_one({'_id': notification_id})
    assert doc
    assert doc['worker_id'] == 'order_informer_worker_2_0'


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.filldb(ivr_disp_order_stats='bad_already_filled')
async def test_adding_new_event_to_bad_filled_db(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mongodb,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_WAITING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    order_stats = _fetch_order_stats(mongodb, utils.DEFAULT_ORDER_ID)
    assert order_stats and order_stats['order_constants']

    assert 'application' in order_stats['order_constants']
    assert 'country' in order_stats['order_constants']
    assert 'dont_call' in order_stats['order_constants']
    assert 'nearest_zone' in order_stats['order_constants']
    assert 'personal_phone_id' in order_stats['order_constants']
    assert 'user_locale' in order_stats['order_constants']
    assert 'user_phone_id' in order_stats['order_constants']


@pytest.mark.pgsql('ivr_api', files=['inbound_number.sql'])
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_inbound_number(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
):
    @mockserver.json_handler('/octonode', prefix=True)
    async def octonode(request):
        data = request.json
        assert (
            data['script']['steps']['start']['parameters']['calling_number']
            == '+74959999999'
        )  # we use number, cause it is in pg and in DEFAULT_IVR_SETTINGS
        if data.get('session_id'):
            return {'session_id': data['session_id']}
        return {'session_id': 'mocked_session_id'}

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert octonode.times_called == 1


@pytest.mark.parametrize(
    [
        'taxi_status',
        'phone_id',
        'is_newbie',
        'application',
        'was_routesharing',
    ],
    [
        ['driving', utils.DEFAULT_PHONE_ID, False, 'call_center', True],
        [
            'driving',
            utils.DEFAULT_PHONE_ID,
            True,
            'call_center',
            False,
        ],  # no exp for newbies
        [
            'driving',
            utils.DEFAULT_PHONE_ID,
            False,
            '7220_call_center',
            False,
        ],  # no exp for this app
        [
            'waiting',
            utils.DEFAULT_PHONE_ID,
            False,
            'call_center',
            False,
        ],  # exp in driving for this pd_id
        [
            'waiting',
            '581fe54e0779cf3c0cb61b71',
            False,
            'call_center',
            True,
        ],  # exp in waiting for this pd_id
    ],
    ids=(
        'exp in driving',
        'no sms for newbie',
        'no sms for application',
        'no sms in waiting for selected pd_id',
        'sms in waiting for selected pd_id',
    ),
)
@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='experiments3_routesharing.json')
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    ROUTE_SHARING_URL_TEMPLATES={
        '/whitelabel/vezet': '',
        '/yango/turboapp': 'https://yango.yandex.com/route/{key}?lang={lang}',
        'rutaxi': 'https://rutaxi.ru/route/{key}{key}?lang={lang}',
        'turboapp': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
        'vezet': 'https://tariff.vezet.ru/route/{key}?lang={lang}',
        'yandex': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
        'yango': 'https://yango.yandex.com/route/{key}?lang={lang}',
        'yataxi': 'https://go.yandex/route/{key}?lang={lang}',
        'yauber': 'https://support-uber.com/route/{key}?lang={lang}',
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_routesharing_exp(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        taxi_status,
        phone_id,
        is_newbie,
        application,
        mock_clck,
        was_routesharing,
        stq,
        mock_personal,
):
    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _retrieve_personal_id(request):
        data = request.json
        return {
            'id': data['id'],
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
        }

    if not is_newbie:
        now = datetime.datetime(2018, 12, 1, 00, 00, 00)
        query = {'_id': bson.ObjectId(phone_id)}
        update = {
            '$set': {
                'created': now,
                'updated': now,
                f'applications.{utils.DEFAULT_APPLICATION}': now,
            },
        }
        mongodb.callcenter_newbies.update_one(query, update, upsert=True)

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['taxi_status'] = taxi_status
        response['fields']['order']['application'] = application
        response['fields']['order']['user_phone_id'] = phone_id
        return response

    if taxi_status == 'driving':
        event_key = utils.HANDLE_DRIVING
    else:  # waiting
        event_key = utils.HANDLE_WAITING

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': event_key,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )

    if was_routesharing or is_newbie:
        assert stq.ivr_sms_sending.times_called == 1
        args = stq.ivr_sms_sending.next_call()
        args = args['kwargs']
        if is_newbie:
            assert 'Условия использования' in args['text']
        else:
            # sms with route sharing
            assert args['text'] == 'Ссылка на водителя - clck_url'
    else:
        assert not stq.ivr_sms_sending.times_called
