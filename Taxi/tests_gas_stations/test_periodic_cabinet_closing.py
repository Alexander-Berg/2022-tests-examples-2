import datetime

import bson
import pytest


def _check_updated(row):
    def _check_is_now(value):
        delta = datetime.datetime.utcnow() - value
        assert datetime.timedelta() <= delta <= datetime.timedelta(minutes=1)

    updated_ts = row.pop('updated_ts')
    assert isinstance(updated_ts, bson.timestamp.Timestamp)
    assert updated_ts.inc > 0
    _check_is_now(datetime.datetime.utcfromtimestamp(updated_ts.time))

    modified_date = row.pop('modified_date')
    assert isinstance(modified_date, datetime.datetime)
    _check_is_now(modified_date)


@pytest.mark.parametrize(
    (),
    [
        pytest.param(
            id='empty_config', marks=pytest.mark.config(GAS_STATIONS_CRONS={}),
        ),
        pytest.param(
            id='empty_times',
            marks=[
                pytest.mark.config(
                    GAS_STATIONS_CRONS={
                        'DROP_OUTDATED_GAS_STATION_CABINETS': {
                            'kind': 'every_day_times',
                            'times': [],
                        },
                    },
                ),
                pytest.mark.now('2020-10-11T17:59:59+00:00'),
            ],
        ),
        pytest.param(
            id='too_early',
            marks=[
                pytest.mark.config(
                    GAS_STATIONS_CRONS={
                        'DROP_OUTDATED_GAS_STATION_CABINETS': {
                            'kind': 'every_day_times',
                            'times': ['18:00'],
                        },
                    },
                ),
                pytest.mark.now('2020-10-11T17:59:59+00:00'),
            ],
        ),
        pytest.param(
            id='some_time_after',
            marks=[
                pytest.mark.config(
                    GAS_STATIONS_CRONS={
                        'DROP_OUTDATED_GAS_STATION_CABINETS': {
                            'kind': 'every_day_times',
                            'times': ['18:00', '22:00'],
                        },
                    },
                ),
                pytest.mark.now('2020-10-11T18:20+00:00'),
            ],
        ),
        pytest.param(
            id='other_time',
            marks=[
                pytest.mark.config(
                    GAS_STATIONS_CRONS={
                        'DROP_OUTDATED_GAS_STATION_CABINETS': {
                            'kind': 'every_day_times',
                            'times': ['18:00', '22:00'],
                        },
                    },
                ),
                pytest.mark.now('2020-10-11T20:00+00:00'),
            ],
        ),
    ],
)
async def test_cron_not_start(taxi_gas_stations, testpoint):
    @testpoint('cron::DropOutdatedGS-finished')
    def task_completed(data):
        pass

    async with taxi_gas_stations.spawn_task('distlock/drop-outdated-gs'):
        result = await task_completed.wait_call()
    assert result == {'data': {'result': 'not-run'}}


_NOTIFICATION_CLOSED_PAYLOAD = {
    'entity': {'type': 'gas-stations/cabinet-closed-automatically'},
    'text': 'Кабинет закрыт текст',
    'title': 'Кабинет закрыт заголовок',
}
_NOTIFICATION_MONEY_PAYLOAD = {
    'entity': {'type': 'gas-stations/need-withdraw-balance'},
    'text': 'В кабинете деньги текст',
    'title': 'В кабинете деньги заголовок',
}


@pytest.mark.now('2020-10-11T20:00:00+00:00')
@pytest.mark.config(
    GAS_STATIONS_CRONS={
        'DROP_OUTDATED_GAS_STATION_CABINETS': {
            'kind': 'every_day_times',
            'times': ['20:00'],
        },
    },
    GAS_STATIONS_TANKER_YT_REPLICA_PATH='//path/to/zapravki/mongo/dump',
)
@pytest.mark.filldb(dbparks='client_id_fix')
@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.translations(
    gas_stations={
        'cabinet_closed_automatically_text': {'ru': 'Кабинет закрыт текст'},
        'cabinet_closed_automatically_title': {
            'ru': 'Кабинет закрыт заголовок',
        },
        'cabinet_need_withdraw_balance_text': {
            'ru': 'В кабинете деньги текст',
        },
        'cabinet_need_withdraw_balance_title': {
            'ru': 'В кабинете деньги заголовок',
        },
    },
)
async def test_run(
        taxi_gas_stations, testpoint, mockserver, load_json, yt_apply, mongodb,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def v1_parks_list(request):
        req_js = request.json
        park_ids = set(req_js['query']['park']['ids'])
        filtered = [
            x for x in load_json('parks_response.json') if x['id'] in park_ids
        ]
        assert len(park_ids) == len(filtered)
        return {'parks': filtered}

    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    async def billing_client_id_retrieve(request):
        clid = request.query['park_id']
        mapping = {
            'clid_preserve': 1111,
            'clid_drop': 1222,
            'clid_has_balance': 1333,
            'clid_has_neg_balance': 1444,
        }
        assert clid in mapping, 'Unknown clid requested'
        return {'billing_client_id': str(mapping[clid])}

    @mockserver.json_handler('app-tanker/api/corporation/balance/taxi')
    async def tanker_balance(request):
        park_id = request.query['dbId']
        balances = {
            'park_id_drop': 0.0,
            'park_id_has_balance': 2.0,
            'park_id_has_neg_balance': -100.1,
        }
        assert park_id in balances
        return {'balance': balances[park_id]}

    @mockserver.json_handler('/fleet-notifications/v1/notifications/create')
    async def park_notifications(request):
        req_js = request.json

        expected_payloads = {
            'park_id_drop': _NOTIFICATION_CLOSED_PAYLOAD,
            'park_id_has_balance': _NOTIFICATION_MONEY_PAYLOAD,
            'park_id_has_neg_balance': _NOTIFICATION_MONEY_PAYLOAD,
        }

        park_id = req_js['destinations'][0]['park_id']
        request_id = req_js['request_id']
        assert park_id in expected_payloads
        assert req_js == {
            'destinations': [{'park_id': park_id}],
            'payload': expected_payloads[park_id],
            'request_id': request_id,
        }
        return {}

    @testpoint('cron::DropOutdatedGS-finished')
    def task_completed(data):
        pass

    async with taxi_gas_stations.spawn_task('distlock/drop-outdated-gs'):
        result = await task_completed.wait_call()
    assert result == {'data': {'result': 'complete'}}
    db_state = sorted(mongodb.dbparks.find({}), key=lambda x: x['_id'])
    for row in db_state:
        if row['_id'] != 'park_id_drop':
            continue
        _check_updated(row)
    assert db_state == [
        {'_id': 'park_id_drop', 'login': 'park_id_drop'},
        {
            '_id': 'park_id_has_balance',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_has_balance',
        },
        {
            '_id': 'park_id_has_neg_balance',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_has_neg_balance',
        },
        {'_id': 'park_id_not_accepted', 'login': 'park_id_not_accepted'},
        {
            '_id': 'park_id_preserve',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_preserve',
        },
    ]
    assert v1_parks_list.has_calls
    assert billing_client_id_retrieve.has_calls
    assert tanker_balance.has_calls
    assert park_notifications.has_calls


@pytest.mark.now('2020-10-11T22:00:00+00:00')
@pytest.mark.config(
    GAS_STATIONS_CRONS={
        'DROP_OUTDATED_GAS_STATION_CABINETS': {
            'kind': 'every_day_times',
            'times': ['22:00'],
        },
    },
    GAS_STATIONS_TANKER_YT_REPLICA_PATH='//path/to/zapravki/mongo/dump',
)
@pytest.mark.filldb(dbparks='duplicate_cabinets')
@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'],
    static_table_data=['yt_data_duplicates.yaml'],
)
@pytest.mark.translations(
    gas_stations={
        'cabinet_closed_automatically_text': {'ru': 'Кабинет закрыт текст'},
        'cabinet_closed_automatically_title': {
            'ru': 'Кабинет закрыт заголовок',
        },
        'cabinet_need_withdraw_balance_text': {
            'ru': 'В кабинете деньги текст',
        },
        'cabinet_need_withdraw_balance_title': {
            'ru': 'В кабинете деньги заголовок',
        },
    },
)
async def test_run_duplicates(
        taxi_gas_stations, testpoint, mockserver, load_json, yt_apply, mongodb,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def v1_parks_list(request):
        req_js = request.json
        park_ids = set(req_js['query']['park']['ids'])
        filtered = [
            x
            for x in load_json('parks_response_duplicates.json')
            if x['id'] in park_ids
        ]
        assert len(park_ids) == len(filtered)
        return {'parks': filtered}

    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    async def billing_client_id_retrieve(request):
        clid = request.query['park_id']
        mapping = {
            'clid_drop_only_one_KEEP': 1111,
            'clid_drop_only_one': 1222,
            'clid_dont_drop1': 1333,
            'clid_dont_drop2': 1444,
            'clid_simple_drop1': 1555,
            'clid_simple_drop2': 1666,
        }
        assert clid in mapping, 'Unknown clid requested'
        return {'billing_client_id': str(mapping[clid])}

    @mockserver.json_handler('app-tanker/api/corporation/balance/taxi')
    async def tanker_balance(request):
        park_id = request.query['dbId']
        balances = {
            'park_id_drop_only_one_DROP': 500,
            'park_id_drop_only_one_KEEP': 500,
            'park_id_dont_drop1': -500,
            'park_id_dont_drop2': -500,
            'park_id_simple_drop1': 0.0,
            'park_id_simple_drop2': 0.0,
        }
        assert park_id in balances
        return {'balance': balances[park_id]}

    @mockserver.json_handler('/fleet-notifications/v1/notifications/create')
    async def park_notifications(request):
        req_js = request.json

        expected_payloads = {
            'park_id_drop_only_one_DROP': _NOTIFICATION_CLOSED_PAYLOAD,
            'park_id_dont_drop1': _NOTIFICATION_MONEY_PAYLOAD,
            'park_id_dont_drop2': _NOTIFICATION_MONEY_PAYLOAD,
            'park_id_simple_drop1': _NOTIFICATION_CLOSED_PAYLOAD,
            'park_id_simple_drop2': _NOTIFICATION_CLOSED_PAYLOAD,
        }

        park_id = req_js['destinations'][0]['park_id']
        request_id = req_js['request_id']
        assert park_id in expected_payloads
        assert req_js == {
            'destinations': [{'park_id': park_id}],
            'payload': expected_payloads[park_id],
            'request_id': request_id,
        }
        return {}

    @testpoint('cron::DropOutdatedGS-finished')
    def task_completed(data):
        pass

    async with taxi_gas_stations.spawn_task('distlock/drop-outdated-gs'):
        result = await task_completed.wait_call()
    assert result == {'data': {'result': 'complete'}}
    db_state = sorted(mongodb.dbparks.find({}), key=lambda x: x['_id'])
    for row in db_state:
        if row['_id'] in {
                'park_id_drop_only_one_DROP',
                'park_id_simple_drop1',
                'park_id_simple_drop2',
        }:
            _check_updated(row)
    assert db_state == [
        {
            '_id': 'park_id_dont_drop1',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_dont_drop1',
        },
        {
            '_id': 'park_id_dont_drop2',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_dont_drop2',
        },
        {
            '_id': 'park_id_drop_only_one_DROP',
            'login': 'park_id_drop_only_one_DROP',
        },
        {
            '_id': 'park_id_drop_only_one_KEEP',
            'gas_stations': {
                'informed_consent_accepted_date': '2020-07-29T08:19:18.984Z',
                'offer_accepted_date': '2020-07-29T08:19:18.984Z',
            },
            'login': 'park_id_drop_only_one_KEEP',
        },
        {'_id': 'park_id_simple_drop1', 'login': 'park_id_simple_drop1'},
        {'_id': 'park_id_simple_drop2', 'login': 'park_id_simple_drop2'},
    ]
    assert v1_parks_list.has_calls
    assert billing_client_id_retrieve.has_calls
    assert tanker_balance.has_calls
    assert park_notifications.has_calls
