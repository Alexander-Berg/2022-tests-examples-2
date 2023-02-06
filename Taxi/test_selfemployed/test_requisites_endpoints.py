# pylint: disable=redefined-outer-name,unused-variable
import pytest

from testsuite.utils import http

from selfemployed.db import dbmain
from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, inn, bik, account_number,
            created_at, modified_at)
        VALUES
            ('aaa15', '1d', '1p', 'm_inn', 'm_bik', 'm_acc',
            now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS=(
        conftest.TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS
    ),
)
async def test_get_requisites(se_client, se_web_context):
    park_id = '1p'
    driver_id = '1d'

    response = await se_client.get(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()

    driver_data = await dbmain.get_from_driver(
        se_web_context.pg, park_id, driver_id,
    )
    assert content == {
        'inn': driver_data['inn'],
        'banks': [
            {
                'info': '',
                'title': 'Сбербанк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702937&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Альфа-банк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702737&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Тинькофф',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702897&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'ВТБ',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000695638&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
        ],
        'bik_mask': '[000000000]',
        'bik_hint': '000000000',
        'bik': driver_data['bik'],
        'account': driver_data['account_number'],
        'account_mask': '[00000] [00000] [00000] [00000]',
        'account_hint': '00000 00000 00000 00000',
        'required': False,
        'btn_next_text': 'Далее',
        'description': 'Нам нужны ваши реквизиты, чтобы...',
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, inn, bik, account_number,
            salesforce_account_id, salesforce_requisites_case_id,
            created_at, modified_at)
        VALUES
            ('aaa15', '1d', '1p', 'm_inn', null, null,
             'sf_acc_id', 'sf_case_id',
              now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS=(
        conftest.TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS
    ),
)
async def test_get_requisites_sf_case(
        se_client, se_web_context, mock_salesforce,
):
    park_id = '1p'
    driver_id = '1d'

    @mock_salesforce('/services/data/v46.0/sobjects/Case/sf_case_id')
    async def _mock_get_case(request: http.Request):
        assert request.query == {'fields': 'IBAN__c,SWIFT__c,Subject,Status'}
        return {
            'IBAN__c': '00000000000000000000',
            'SWIFT__c': '000000000',
            'Subject': 'Self-Employed Change Payment Details',
            'Status': 'In Progress',
        }

    response = await se_client.get(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()

    driver_data = await dbmain.get_from_driver(
        se_web_context.pg, park_id, driver_id,
    )
    assert content == {
        'inn': driver_data['inn'],
        'banks': [
            {
                'info': '',
                'title': 'Сбербанк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702937&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Альфа-банк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702737&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Тинькофф',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702897&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'ВТБ',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000695638&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
        ],
        'bik_mask': '[000000000]',
        'bik_hint': '000000000',
        'bik': '000000000',
        'account': '00000000000000000000',
        'account_mask': '[00000] [00000] [00000] [00000]',
        'account_hint': '00000 00000 00000 00000',
        'required': False,
        'btn_next_text': 'Далее',
        'description': 'Нам нужны ваши реквизиты, чтобы...',
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_driver_id, from_park_id, park_id, driver_id, inn, bik,
             account_number, created_at, modified_at)
        VALUES
            ('aaa15', '1d', '1p', 'new1p', 'new1d', 'm_inn', 'm_bik',
            'm_acc', now()::timestamp, now()::timestamp)
        """,
    ],
)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS=(
        conftest.TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS
    ),
)
async def test_get_requisites_se(se_client, se_web_context):
    park_id = 'new1p'
    driver_id = 'new1d'

    response = await se_client.get(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()

    driver_data = await dbmain.get_from_selfemployed(
        se_web_context.pg, park_id, driver_id,
    )
    assert content == {
        'inn': driver_data['inn'],
        'banks': [
            {
                'info': '',
                'title': 'Сбербанк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702937&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Альфа-банк',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702737&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'Тинькофф',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000702897&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
            {
                'info': '',
                'title': 'ВТБ',
                'url': (
                    'https://taxi.yandex.ru/driver-partner/info/'
                    '?articleId=360000695638&lang=ru'
                    '&sectionId=360000189789'
                ),
            },
        ],
        'bik_mask': '[000000000]',
        'bik_hint': '000000000',
        'bik': driver_data['bik'],
        'account': driver_data['account_number'],
        'account_mask': '[00000] [00000] [00000] [00000]',
        'account_hint': '00000 00000 00000 00000',
        'required': True,
        'btn_next_text': 'Отправить',
        'description': 'Нам нужны ваши реквизиты, чтобы обновить',
    }


async def test_post_requisites_401(se_client):
    data = {'step': dbmain.Step.REQUISITES}

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
    )
    assert response.status == 401


async def test_post_requisites_body_400(se_client):
    params = {'park': '1', 'driver': '1'}
    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json={},
    )
    assert response.status == 400


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_requisites_body_409(se_client):
    params = {'park': '4_2p', 'driver': '4_2d'}
    data = {
        'bik': '123456789',
        'personal_account': '40817111122223333222',
        'step': dbmain.Step.REQUISITES,
    }
    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 409


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, inn, bik, account_number,
            created_at, modified_at)
        VALUES
            ('aaa15', '41p', '41d', 'm_inn1', NULL, NULL,
             NOW(), NOW()),
            ('aaa16', '42p', '42d', 'm_inn2', NULL, NULL,
             NOW(), NOW())
        """,
    ],
)
@pytest.mark.parametrize(
    'park_id,driver_id,bik,account,se_id',
    [
        ('41p', '41d', '123456789', '40817111122223333224', 'aaa15'),
        ('42p', '42d', '123456789', '40817111122223333224', 'aaa16'),
    ],
)
async def test_post_requisites_filled_200(
        park_id,
        driver_id,
        bik,
        account,
        se_id,
        se_client,
        se_web_context,
        patch,
        mock_partner_contracts,
        mock_client_notify,
):
    clid = 'OLD_PARK_CLID'

    @patch('taxi.clients.parks.ParksClient._request')
    async def _request_parks(*args, **kwargs):
        return {
            'driver_profiles': [],
            'parks': [{'provider_config': {'yandex': {'clid': clid}}}],
        }

    @mock_partner_contracts('/v1/register_partner/rus/')
    async def _request_contracts(request):
        assert request.json == {
            'flow': 'selfemployed',
            'rewrite': True,
            'new': True,
            'stage_name': 'newreq',
            'inquiry_id': se_id,
            'params': {
                'selfemployed_id': se_id,
                'clid': clid,
                'company_rs': account,
                'company_bik': bik,
            },
        }
        return {'inquiry_id': 'inquiry_id', 'status': 'status'}

    @mock_client_notify('/v2/push')
    async def _send_message(request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{park_id}-{driver_id}',
            'collapse_key': f'requisites_saved_{park_id}',
            'notification': {'text': 'Реквизиты сохранены'},
        }
        return {'notification_id': 'notification_id'}

    data = {
        'step': dbmain.Step.REQUISITES,
        'bik': bik,
        'personal_account': account,
    }
    params = {'park': park_id, 'driver': driver_id}

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content == {'next_step': 'finish', 'step_count': 7, 'step_index': 7}

    # assert db
    postgres = se_web_context.pg
    row = await dbmain.get_from_driver(postgres, park_id, driver_id)
    if data['bik']:
        assert row['bik'] == data['bik']
    else:
        assert not row['bik']

    if data['personal_account']:
        assert row['account_number'] == data['personal_account']
    else:
        assert not row['account_number']

    if bik and account:
        assert row['step'] == dbmain.Step.REQUISITES


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, park_id, driver_id, inn, from_park_id, from_driver_id,
             salesforce_account_id, created_at, modified_at)
        VALUES
            ('seid', 'parkid', 'driverid', 'inn', 'fromparkid', 'fromdriverid',
             'sfacc', NOW(), NOW())
        """,
    ],
)
async def test_post_requisites_salesforce_200(
        se_client, se_web_context, mock_salesforce, mock_client_notify,
):
    bik = '123456789'
    iban = '40817111122223333224'

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _request_contracts(request):
        assert request.json == {
            'RecordTypeId': 'RecordTypeCase',
            'AccountId': 'sfacc',
            'Status': 'In Progress',
            'Origin': 'API',
            'IBAN__c': iban,
            'SWIFT__c': bik,
            'Subject': 'Self-Employed Change Payment Details',
        }
        return {'id': 'CaseId'}

    @mock_client_notify('/v2/push')
    async def _send_message(request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': 'fromparkid-fromdriverid',
            'collapse_key': 'requisites_saved_fromparkid',
            'notification': {'text': 'Реквизиты сохранены'},
        }
        return {'notification_id': 'notification_id'}

    data = {
        'step': dbmain.Step.REQUISITES,
        'bik': bik,
        'personal_account': iban,
    }
    params = {'park': 'parkid', 'driver': 'driverid'}

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert driver data
    driver_data = await dbmain.get_from_selfemployed(
        se_web_context.pg, 'parkid', 'driverid',
    )
    assert driver_data['salesforce_requisites_case_id'] == 'CaseId'

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content == {'next_step': 'exit', 'step_count': 7}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, park_id, driver_id, inn,
             bik, account_number,
             created_at, modified_at)
        VALUES
            ('se_d_1', 'old1p', 'old1d', 'new1p', 'new1d', 'm_inn1',
             '00000', '0001010',
             NOW(), NOW())
        """,
    ],
)
async def test_post_requisites_filled_se(
        se_client,
        se_web_context,
        patch,
        mock_partner_contracts,
        mock_client_notify,
):
    clid = 'OLD_PARK_CLID'
    park_id = 'new1p'
    driver_id = 'new1d'
    bik = '123456789'
    account = '40817111122223333224'
    se_id = 'se_d_1'

    @patch('taxi.clients.parks.ParksClient._request')
    async def _request_parks(*args, **kwargs):
        assert kwargs['data']['query']['park']['id'] == 'new1p'
        return {
            'driver_profiles': [],
            'parks': [{'provider_config': {'yandex': {'clid': clid}}}],
        }

    @mock_partner_contracts('/v1/register_partner/rus/')
    async def _request_contracts(request):
        assert request.json == {
            'flow': 'selfemployed',
            'rewrite': True,
            'new': True,
            'stage_name': 'newreq',
            'inquiry_id': se_id,
            'params': {
                'selfemployed_id': se_id,
                'clid': clid,
                'company_rs': account,
                'company_bik': bik,
            },
        }
        return {'inquiry_id': 'inquiry_id', 'status': 'status'}

    @mock_client_notify('/v2/push')
    async def _send_message(request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': 'old1p-old1d',
            'collapse_key': 'requisites_saved_old1p',
            'notification': {'text': 'Реквизиты сохранены'},
        }
        return {'notification_id': 'notification_id'}

    data = {
        'step': dbmain.Step.REQUISITES,
        'bik': bik,
        'personal_account': account,
    }
    params = {'park': park_id, 'driver': driver_id}

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )

    # assert response
    assert response.status == 200
    content = await response.json()
    assert content['next_step'] == 'exit'

    # assert db
    postgres = se_web_context.pg
    row = await dbmain.get_from_selfemployed(postgres, park_id, driver_id)
    if data['bik']:
        assert row['bik'] == data['bik']
    else:
        assert not row['bik']

    if data['personal_account']:
        assert row['account_number'] == data['personal_account']
    else:
        assert not row['account_number']

    if bik and account:
        assert row['step'] == dbmain.Step.REQUISITES


async def test_post_requisites_step_400(se_client):
    data = {'step': dbmain.Step.INTRO}
    params = {'park': '1', 'driver': '1'}

    response = await se_client.post(
        '/self-employment/fns-se/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=data,
    )
    assert response.status == 400
