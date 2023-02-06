import copy
import typing

import pytest

ENDPOINT = '/fleet/driver-money/v1/driver/balance/correction/url'

PARKS_RESPONSE = {
    'driver_profiles': [
        {
            'accounts': [
                {'balance': '2444216.6162', 'currency': 'RUB', 'id': 'driver'},
            ],
            'driver_profile': {
                'id': 'driver',
                'created_date': '2020-12-12T22:22:00.1231Z',
            },
        },
    ],
    'offset': 0,
    'parks': [
        {
            'id': '7ad36bc7560449998acbe2c57a75c293',
            'country_id': 'rus',
            'city': 'Москва',
            'tz': 3,
            'driver_partner_source': 'yandex',
            'provider_config': {'yandex': {'clid': 'clid_0'}},
        },
    ],
    'total': 1,
    'limit': 1,
}

CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'balance_correction_notification_files_download',
    'consumers': ['driver_money/v1_driver_balance_main_filtered'],
    'clauses': [
        {
            'value': {
                'title_key': 'DriverMoney_Correction_Notification_To_Download',
                'support_title_key': (
                    'DriverMoney_Correction_Notification_Download_Support'
                ),
                'support_deeplink_url': 'taximeter://screen/support',
                'files': [
                    {
                        'title_key': (
                            'DriverMoney_Correction_Notification_PDF_Download'
                        ),
                        'url': 'dir/{park_id}_{uuid}.pdf',
                        'ttl_in_minutes': 20,
                    },
                    {
                        'title_key': (
                            'DriverMoney_Correction_Notification_XLSX_Download'
                        ),
                        'url': 'dir/{park_id}_{uuid}.xlsx',
                        'ttl_in_minutes': 20,
                    },
                ],
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'driver',
                    'arg_name': 'driver_id',
                    'arg_type': 'string',
                },
            },
        },
    ],
}

CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED: typing.Dict[
    str, typing.Any,
] = copy.deepcopy(CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED)
CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED['clauses'][0]['predicate'][
    'init'
]['value'] = 'driver_other'


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize(
    'have_url',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                **CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                **CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED,
            ),
        ),
    ],
)
async def test_fleet_driver_balance_correction_url(
        taxi_driver_money, mockserver, have_url,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(_):
        return PARKS_RESPONSE

    response = await taxi_driver_money.get(
        ENDPOINT,
        headers={
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '100',
        },
        params={'driver_profile_id': 'driver'},
    )
    assert response.status_code == 200
    data = response.json()
    if have_url:
        assert 'url' in data
        assert data['url'].startswith(
            'https://driver-money.'
            + mockserver.url('/mds-s3')
            + '/dir/7ad36bc7560449998acbe2c57a75c293_driver.pdf',
        )
    else:
        assert 'url' not in data
