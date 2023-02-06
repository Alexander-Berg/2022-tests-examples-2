import os

import freezegun
import pytest

PERSONAL_FIELDS = {
    'personal_phone_id': 'phone',
    'personal_license_id': 'driver_license'
}


@pytest.mark.parametrize(
    'send_ids, send_values',
    [
        ('0', '1'),
        ('1', '1'),
        ('1', '0')
    ]
)
@freezegun.freeze_time("2019-11-20T23:05:00Z")
def test_send_events_to_replication(
        run_send_events_to_replication,
        get_mongo,
        load_json,
        patch,
        send_values,
        send_ids,
):
    os.environ['REPLICATION_SEND_PERSONAL_IDS'] = send_ids
    os.environ['REPLICATION_SEND_PERSONAL_VALUES'] = send_values

    @patch('infranaim.clients.replication._request')
    def _request(method, location, tvm_client=None, **params):
        items = params['json']['items']
        for item in items:
            data = item['data']
            if data.get('data'):
                data = data['data']

            if not send_ids:
                for field in PERSONAL_FIELDS:
                    assert field not in data
            if not send_values:
                for field in PERSONAL_FIELDS.values():
                    assert field not in data
        return params['json']

    mongo = get_mongo
    run_send_events_to_replication(
        mongo,
        '--event_type=send_create_driver_events'
    )
    assert not list(mongo.statistics_events.find())

    run_send_events_to_replication(
        mongo,
        '--event_type=send_oktell_submit_events'
    )
    assert not list(mongo.oktell_statistics.find())
