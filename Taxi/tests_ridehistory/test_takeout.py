import datetime as dt
import json

import pytest
import pytz


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.parametrize(
    'delete_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
        ),
        False,
    ],
)
async def test_delete_simple(taxi_ridehistory, pgsql, delete_enabled):
    response = await taxi_ridehistory.post(
        '/v1/takeout/delete',
        json={
            'request_id': '1',
            'yandex_uids': [
                {'is_portal': True, 'uid': 'uid1'},
                {'is_portal': False, 'uid': 'uid2'},
            ],
            'phone_ids': ['phone_id1', 'phone_id2'],
            'user_ids': ['user_id1'],
        },
    )

    if not delete_enabled:
        assert response.status == 501
        return

    assert response.status == 200

    db = pgsql['ridehistory']
    exp_delete_to = dt.datetime(2017, 9, 8, 21)

    cursor = db.cursor()
    cursor.execute(
        'SELECT yandex_uid, delete_to '
        'FROM ridehistory.takeout_delete_yandex_uid '
        'ORDER BY yandex_uid',
    )
    for (uid, delete_to), exp_uid in zip(cursor, ['uid1', 'uid2']):
        assert uid == exp_uid
        assert (
            delete_to.astimezone(pytz.UTC).replace(tzinfo=None)
            == exp_delete_to
        )

    cursor = db.cursor()
    cursor.execute(
        'SELECT phone_id, delete_to '
        'FROM ridehistory.takeout_delete_phone_id '
        'ORDER BY phone_id',
    )
    for (phone_id, delete_to), exp_phone_id in zip(
            cursor, ['phone_id1', 'phone_id2'],
    ):
        assert phone_id == exp_phone_id
        assert (
            delete_to.astimezone(pytz.UTC).replace(tzinfo=None)
            == exp_delete_to
        )


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'delete_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
        ),
        False,
    ],
)
@pytest.mark.parametrize(
    'data_state, exp_yt_request',
    [
        ('ready_to_delete', 'expected_yt_request_lucky_status'),
        pytest.param(
            'empty',
            'expected_yt_request_lucky_tombstone_status',
            marks=pytest.mark.pgsql(
                'ridehistory', files=['takeout_delete.sql'],
            ),
        ),
    ],
)
async def test_status_simple(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_territories,
        data_state,
        exp_yt_request,
        delete_enabled,
):
    mock_yt_queries(exp_yt_request)
    mock_order_core_query(
        ['77777777777777777777777777777777'], 'order_core_resp_simple', False,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_territories(True)

    response = await taxi_ridehistory.post(
        '/v1/takeout/status',
        json={
            'request_id': '1',
            'yandex_uids': [{'is_portal': True, 'uid': '12345'}],
            'phone_ids': ['777777777777777777777777'],
            'user_ids': ['user_id1'],
        },
    )

    if not delete_enabled:
        assert response.status == 501
        return

    assert response.status == 200
    assert response.json() == {'data_state': data_state}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'exp_yt_request, exp_resp_orders_num',
    [
        pytest.param(
            'expected_yt_request_lucky',
            2,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_lucky_query_enabled.json',
                ),
                pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
            ],
        ),
        pytest.param(
            'expected_yt_request_lucky',
            2,
            marks=[
                pytest.mark.pgsql('ridehistory', files=['takeout_delete.sql']),
                pytest.mark.experiments3(
                    filename='exp3_lucky_query_enabled.json',
                ),
            ],
        ),
        pytest.param(
            'expected_yt_request_lucky_tombstone',
            0,
            marks=[
                pytest.mark.pgsql('ridehistory', files=['takeout_delete.sql']),
                pytest.mark.experiments3(
                    filename='exp3_lucky_query_enabled.json',
                ),
                pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
            ],
        ),
        pytest.param(
            'expected_yt_request_heavy_tombstone',
            0,
            marks=[
                pytest.mark.pgsql('ridehistory', files=['takeout_delete.sql']),
                pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
            ],
        ),
    ],
)
async def test_list_simple(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        exp_yt_request,
        exp_resp_orders_num,
):
    mock_yt_queries(exp_yt_request)
    mock_order_core_query(
        ['77777777777777777777777777777777'], 'order_core_resp_simple', False,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', False)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json={},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert len(response.json()['orders']) == exp_resp_orders_num


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'order_id, exp_yt_request, exp_resp_code',
    [
        pytest.param(
            '77777777777777777777777777777777',
            None,
            200,
            marks=pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
        ),
        pytest.param(
            '13386de2bb47265d852774a128db6255',
            'expected_yt_request_item',
            200,
            marks=pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
        ),
        pytest.param(
            '77777777777777777777777777777777',
            None,
            200,
            marks=pytest.mark.pgsql(
                'ridehistory', files=['takeout_delete.sql'],
            ),
        ),
        pytest.param(
            '13386de2bb47265d852774a128db6255',
            'expected_yt_request_item',
            200,
            marks=pytest.mark.pgsql(
                'ridehistory', files=['takeout_delete.sql'],
            ),
        ),
        pytest.param(
            '77777777777777777777777777777777',
            'expected_yt_request_item_tombstone_pg',
            404,
            marks=[
                pytest.mark.pgsql('ridehistory', files=['takeout_delete.sql']),
                pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
            ],
        ),
        pytest.param(
            '13386de2bb47265d852774a128db6255',
            'expected_yt_request_item',
            404,
            marks=[
                pytest.mark.pgsql('ridehistory', files=['takeout_delete.sql']),
                pytest.mark.config(RIDEHISTORY_TAKEOUT_DELETE_ENABLED=True),
            ],
        ),
    ],
)
async def test_item_simple(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        order_id,
        exp_yt_request,
        exp_resp_code,
):
    mock_yt_queries(exp_yt_request)
    mock_order_core_query([order_id], 'order_core_resp_simple', True)
    mock_transactions_query([order_id], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    response = await taxi_ridehistory.post(
        'v2/item',
        json={'check_permissions': True, 'order_id': order_id},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == exp_resp_code


async def test_job_create_simple(taxi_ridehistory, stq):
    response = await taxi_ridehistory.put(
        '/v1/takeout/job', json={'request_id': '1', 'yandex_uid': '2'},
    )

    assert response.status == 200
    assert stq['ridehistory_takeout_job'].times_called == 1

    call = stq['ridehistory_takeout_job'].next_call()
    kwargs = call['kwargs']
    del kwargs['log_extra']

    assert kwargs == {'request_id': '1', 'yandex_uid': '2'}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.config(
    TAKEOUT_ORDER_HISTORY_CHUNK_SIZE=1,
    RIDEHISTORY_TAKEOUT_JOB_SLEEP=-1,
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
)
@pytest.mark.pgsql('ridehistory', files=['takeout_job_simple.sql'])
async def test_job_simple(
        taxi_ridehistory,
        mockserver,
        load_json,
        stq_runner,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
):
    @mockserver.json_handler('/taxi-takeout/v1/jobs/done')
    def jobs_done_mock(request):
        assert request.json['job_id'] == '777'
        expected_json = load_json('expected_takeout_job_result_simple.json')[
            0
        ]['result_json']
        assert json.loads(request.json['result']) == expected_json
        assert request.json['service_name'] == 'ridehistory'
        return {}

    @mockserver.json_handler('/zalogin/v2/internal/uid-info')
    def zalogin_mock(request):
        assert request.query['yandex_uid'] == '1'

        return {
            'yandex_uid': '1',
            'type': 'portal',
            'bound_phonishes': [
                {
                    'uid': '2',
                    'phone_id': '777',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
                {
                    'uid': '3',
                    'phone_id': '666',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
            ],
        }

    mock_yt_queries('expected_yt_request_takeout_job')
    mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_simple',
        True,
    )
    mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    await stq_runner.ridehistory_takeout_job.call(
        task_id='sample_task',
        args=[],
        kwargs={'request_id': '777', 'yandex_uid': '1'},
        expect_fail=False,
    )

    assert zalogin_mock.times_called == 1
    assert jobs_done_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.config(
    TAKEOUT_ORDER_HISTORY_CHUNK_SIZE=1,
    RIDEHISTORY_TAKEOUT_JOB_SLEEP=-1,
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
)
async def test_job_no_data(mockserver, stq_runner, mock_yt_queries):
    @mockserver.json_handler('/zalogin/v2/internal/uid-info')
    def zalogin_mock(request):
        assert request.query['yandex_uid'] == '1'

        return {'yandex_uid': '1', 'type': 'portal'}

    @mockserver.json_handler('/taxi-takeout/v1/jobs/done')
    def jobs_done_mock(request):
        assert 'result' not in request.json
        return {}

    mock_yt_queries('expected_yt_request_takeout_job_no_data')

    await stq_runner.ridehistory_takeout_job.call(
        task_id='sample_task',
        args=[],
        kwargs={'request_id': '1', 'yandex_uid': '1'},
        expect_fail=False,
    )

    assert zalogin_mock.times_called == 1
    assert jobs_done_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.config(
    TAKEOUT_ORDER_HISTORY_CHUNK_SIZE=1,
    RIDEHISTORY_TAKEOUT_JOB_SLEEP=-1,
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
)
@pytest.mark.pgsql('ridehistory', files=['takeout_job_simple.sql'])
async def test_job_404(
        taxi_ridehistory,
        mockserver,
        stq_runner,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
):
    @mockserver.json_handler('/taxi-takeout/v1/jobs/done')
    def jobs_done_mock(request):
        return mockserver.make_response(
            status=404, json={'status': 'error', 'error': 'job not found'},
        )

    @mockserver.json_handler('/zalogin/v2/internal/uid-info')
    def zalogin_mock(request):
        assert request.query['yandex_uid'] == '1'

        return {
            'yandex_uid': '1',
            'type': 'portal',
            'bound_phonishes': [
                {
                    'uid': '2',
                    'phone_id': '777',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
                {
                    'uid': '3',
                    'phone_id': '666',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
            ],
        }

    mock_yt_queries('expected_yt_request_takeout_job')
    mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_simple',
        True,
    )
    mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    await stq_runner.ridehistory_takeout_job.call(
        task_id='sample_task',
        args=[],
        kwargs={'request_id': '777', 'yandex_uid': '1'},
        expect_fail=False,
    )

    assert zalogin_mock.times_called == 1
    assert jobs_done_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.config(
    TAKEOUT_ORDER_HISTORY_CHUNK_SIZE=1,
    RIDEHISTORY_TAKEOUT_JOB_SLEEP=-1,
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
)
@pytest.mark.pgsql('ridehistory', files=['takeout_job_simple.sql'])
async def test_job_500(
        taxi_ridehistory,
        mockserver,
        stq_runner,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
):
    @mockserver.json_handler('/taxi-takeout/v1/jobs/done')
    def jobs_done_mock(request):
        return mockserver.make_response(
            status=500, json={'status': 'error', 'error': 'internal error'},
        )

    @mockserver.json_handler('/zalogin/v2/internal/uid-info')
    def zalogin_mock(request):
        assert request.query['yandex_uid'] == '1'

        return {
            'yandex_uid': '1',
            'type': 'portal',
            'bound_phonishes': [
                {
                    'uid': '2',
                    'phone_id': '777',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
                {
                    'uid': '3',
                    'phone_id': '666',
                    'created': '2017-09-05T00:00:00+0300',
                    'last_confirmed': '2017-09-06T00:00:00+0300',
                },
            ],
        }

    mock_yt_queries('expected_yt_request_takeout_job')
    mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_simple',
        True,
    )
    mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', True)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    await stq_runner.ridehistory_takeout_job.call(
        task_id='sample_task',
        args=[],
        kwargs={'request_id': '777', 'yandex_uid': '1'},
        expect_fail=True,
    )

    assert zalogin_mock.times_called == 1
    assert jobs_done_mock.times_called == 1
