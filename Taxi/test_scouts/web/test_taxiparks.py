import freezegun
import pytest

from infranaim.models import configs as conf


@freezegun.freeze_time('2019-9-4T14:07:37')
@pytest.mark.parametrize(
    'login_doc, external_config, expected_response, '
    'expected_status_code, show_personal',
    [
        (
            {'login': 'taxipark-1', 'password': 'scout_pass'},
            {'TAXIPARKS_TICKETS_LIVE_PERIOD': {'__default__': 96}},
            {
                'data': [{
                    'created_dttm': '2019-08-30 12:00:00',
                    'date_ytc_visit': None,
                    'id': '31337',
                    'name': 'Тупиков Александр Юрьевич',
                    'phone': '+79264927795',
                    'personal_phone_id': '1cd53a0af061466ebcafa3527ee8f892',
                    'updated_dttm': '2019-09-04 13:07:37',
                }],
                'pos': 0,
                'is_last_page': True
            },
            200,
            1
        ),
        (
            {'login': 'taxipark-2', 'password': 'scout_pass'},
            {'TAXIPARKS_TICKETS_LIVE_PERIOD': {'__default__': 96}},
            {
                'data': [{
                    'created_dttm': '2019-08-30 12:00:00',
                    'date_ytc_visit': None,
                    'id': '31339',
                    'name': 'Тупиков Александр Юрьевич',
                    'phone': '+79264927795',
                    'personal_phone_id': '1cd53a0af061466ebcafa3527ee8f892',
                    'updated_dttm': '2019-09-04 13:07:37',
                }],
                'pos': 0,
                'is_last_page': True
            },
            200,
            1
        ),
        (
            {'login': 'scout', 'password': 'scout_pass'},
            {'TAXIPARKS_TICKETS_LIVE_PERIOD': {'__default__': 96}},
            None,
            403,
            1
        ),
        (
            {'login': 'taxipark-1', 'password': 'scout_pass'},
            {'TAXIPARKS_TICKETS_LIVE_PERIOD': {'__default__': 96}},
            {
                'data': [{
                    'created_dttm': '2019-08-30 12:00:00',
                    'date_ytc_visit': None,
                    'id': '31337',
                    'name': 'Тупиков Александр Юрьевич',
                    'personal_phone_id': '1cd53a0af061466ebcafa3527ee8f892',
                    'updated_dttm': '2019-09-04 13:07:37',
                }],
                'pos': 0,
                'is_last_page': True
            },
            200,
            0
        ),
        (
            {'login': 'taxipark-1', 'password': 'scout_pass'},
            {
                'TAXIPARKS_TICKETS_LIVE_PERIOD': {
                    '__default__': 96,
                    'smth': 0
                }
            },
            {
                'data': [{
                    'created_dttm': '2019-08-30 12:00:00',
                    'date_ytc_visit': None,
                    'id': '31337',
                    'name': 'Тупиков Александр Юрьевич',
                    'personal_phone_id': '1cd53a0af061466ebcafa3527ee8f892',
                    'updated_dttm': '2019-09-04 13:07:37',
                }],
                'pos': 0,
                'is_last_page': True
            },
            200,
            0
        ),
        (
            {'login': 'taxipark-1', 'password': 'scout_pass'},
            {
                'TAXIPARKS_TICKETS_LIVE_PERIOD': {
                    '__default__': 96,
                    '5a21425a940d437aa8b81ce676960f75': 0
                }
            },
            {
                'data': [],
                'pos': 0,
                'is_last_page': True
            },
            200,
            0
        ),
    ],
)
def test_taxipark_tickets(
        flask_client_factory, get_mongo,
        login_doc, external_config,
        expected_response, expected_status_code,
        show_personal,
):
    mongo = get_mongo
    for config in external_config:
        setattr(conf.external_config, config, external_config[config])
    configs = {
        'PERSONAL_DATA_SHOW': show_personal
    }
    client = flask_client_factory(mongo, configs=configs)

    login_doc.update(
        {
            'csrf_token': client.get('/get_token').json['token']
        }
    )
    client.post('/login', json=login_doc)

    response = client.get('/taxipark/tickets')
    assert response.status_code == expected_status_code
    assert response.json == expected_response
