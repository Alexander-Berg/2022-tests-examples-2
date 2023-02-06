import csv

import freezegun
import pytest


@freezegun.freeze_time('2019-09-01T12:00:00Z')
@pytest.mark.parametrize(
    'show_personal', [1, 0]
)
def test_download_csv(
        flask_client_factory, find_documents_in_tickets,
        get_mongo, show_personal,
):
    mongo = get_mongo
    configs = {
        'PERSONAL_DATA_SHOW': show_personal
    }
    client = flask_client_factory(mongo, configs=configs)

    data = {
        'login': 'agent',
        'password': 'agent_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)

    request = {
        'csrf_token': client.get('/get_token').json['token'],
        'filters': {
            'created_from': '2019-08-01',
            'created_to': '2019-09-01'
        },
        'sort': {},
        'columns': {
            'name': 'name',
            'phone': 'phone',
            'city': 'city',
            'driver_license': 'driver_license',
            'workflow': 'workflow',
            'own_auto': 'own_auto',
            'park': 'park',
            'status_tag': 'status_tag',
            'reject_reason': 'reject_reason',
            'created_dttm': 'created_dttm',
            'date_active': 'date_active',
            'date_last_ride': 'date_last_ride'
        }
    }
    res = client.post('/download', json=request)
    assert res.status_code == 200

    text = [
        line.strip()
        for line in res.data.decode('utf8').split('\n')
    ]
    fieldnames = text.pop(0).split(';')
    reader = csv.DictReader(text, fieldnames, delimiter=';')
    for i, line in enumerate(reader):
        assert 'personal_phone_id' not in line
        assert 'personal_license_id' not in line
        if show_personal:
            assert 'phone' in line
            assert 'driver_license' in line
        else:
            assert 'phone' not in line
            assert 'driver_license' not in line
    assert i
