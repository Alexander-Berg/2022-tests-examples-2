from aiohttp import web
import pytest

from test_eats_tips_withdrawal import conftest


FULLNAME_MAP = {
    'Петр Петрович Пупкин': 'FULLNAME_ID_11',
    'test fio': 'SHORT_FULLNAME_ID',
}
RUB_CURRENCY_FORMAT = {
    'code': 'RUB',
    'sign': '₽',
    'template': '$VALUE$&nbsp$SIGN$$CURRENCY$',
    'text': 'руб.',
}
PARTNER_IDS_BY_ALIAS = {
    1: '00000000-0000-0000-0000-000000000001',
    2: '00000000-0000-0000-0000-000000000002',
    4: '00000000-0000-0000-0000-000000000004',
    11: '00000000-0000-0000-0000-000000000011',
    27: '00000000-0000-0000-0000-000000000000',
}

WITHDRAWAL_REQUESTS = {
    3: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '21'},
        'comment': 'some comment',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '3',
        'is_blacklist': True,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000001',
        'status': 'manual rejected',
        'user_mysql_id': '1',
        'withdrawal_type': 'SBPb2p',
        'yandex_antifraud_block': False,
    },
    4: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '21'},
        'comment': '',
        'create_date': '2021-06-19T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '4',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000001',
        'status': 'successfully sent to B2P',
        'user_mysql_id': '1',
        'withdrawal_type': 'SBPb2p',
        'yandex_antifraud_block': False,
    },
    9: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '210'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '9',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000004',
        'status': 'sent to manual check',
        'user_mysql_id': '4',
        'withdrawal_type': 'SBPb2p',
        'yandex_antifraud_block': False,
    },
    10: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '210'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '10',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000004',
        'status': 'sent to manual check',
        'user_mysql_id': '4',
        'withdrawal_type': 'SBPb2p',
        'yandex_antifraud_block': False,
    },
    14: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '100'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'Петр Петрович Пупкин',
        'id': '14',
        'is_big_pay': False,
        'is_blacklist': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000011',
        'status': 'error',
        'user_mysql_id': '11',
        'withdrawal_type': 'best2pay',
        'yandex_antifraud_block': False,
    },
    15: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '100'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'Петр Петрович Пупкин',
        'id': '15',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000011',
        'status': 'successfully sent to B2P',
        'user_mysql_id': '11',
        'withdrawal_type': 'best2pay',
        'yandex_antifraud_block': False,
    },
    19: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '100'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'Петр Петрович Пупкин',
        'id': '19',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000011',
        'status': 'sent to manual check',
        'user_mysql_id': '11',
        'withdrawal_type': 'best2pay',
        'yandex_antifraud_block': False,
    },
    20: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '21'},
        'comment': '',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '20',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000001',
        'status': 'success',
        'user_mysql_id': '1',
        'withdrawal_type': 'best2pay',
        'yandex_antifraud_block': False,
    },
    21: {
        'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '21'},
        'comment': 'some comment 2',
        'create_date': '2021-06-22T22:10:25+03:00',
        'exceeded_threshold': False,
        'exceeded_threshold_fresh': False,
        'fullname': 'test fio',
        'id': '21',
        'is_blacklist': False,
        'is_big_pay': False,
        'is_one_card': False,
        'legacy': False,
        'partner_id': '00000000-0000-0000-0000-000000000001',
        'status': 'rejected by B2P',
        'user_mysql_id': '1',
        'withdrawal_type': 'SBPb2p',
        'yandex_antifraud_block': False,
    },
}


@pytest.mark.parametrize(
    'jwt, get_processed, date_from, date_to, multi_filter, expected_result, '
    'expected_status',
    [
        pytest.param(
            conftest.JWT_USER_1,
            False,
            None,
            None,
            None,
            {
                'code': 'not_allowed',
                'message': 'Method not allowed for this user group',
            },
            403,
            id='restricted for not admin',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            False,
            None,
            None,
            None,
            {
                'requests': [
                    WITHDRAWAL_REQUESTS[9],
                    WITHDRAWAL_REQUESTS[10],
                    WITHDRAWAL_REQUESTS[19],
                ],
            },
            200,
            id='no filter',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            True,
            '2021-06-19T22:00:25%2B03:00',
            '2021-06-19T22:40:00%2B03:00',
            None,
            {'requests': [WITHDRAWAL_REQUESTS[4]]},
            200,
            id='date filter',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            False,
            None,
            None,
            '00000000-0000-0000-0000-000000000004',
            {'requests': [WITHDRAWAL_REQUESTS[9], WITHDRAWAL_REQUESTS[10]]},
            200,
            id='partner filter',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            False,
            None,
            None,
            '11',
            {'requests': [WITHDRAWAL_REQUESTS[19]]},
            200,
            id='mysql id filter',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            False,
            None,
            None,
            'test fio',
            {'requests': [WITHDRAWAL_REQUESTS[9], WITHDRAWAL_REQUESTS[10]]},
            200,
            id='name filter',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            True,
            None,
            None,
            'test fio',
            {
                'requests': [
                    WITHDRAWAL_REQUESTS[3],
                    WITHDRAWAL_REQUESTS[9],
                    WITHDRAWAL_REQUESTS[10],
                    WITHDRAWAL_REQUESTS[20],
                    WITHDRAWAL_REQUESTS[21],
                ],
            },
            200,
            id='name filter + processed',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            True,
            None,
            None,
            None,
            {
                'requests': [
                    WITHDRAWAL_REQUESTS[3],
                    WITHDRAWAL_REQUESTS[9],
                    WITHDRAWAL_REQUESTS[10],
                    WITHDRAWAL_REQUESTS[14],
                    WITHDRAWAL_REQUESTS[15],
                    WITHDRAWAL_REQUESTS[19],
                    WITHDRAWAL_REQUESTS[20],
                    WITHDRAWAL_REQUESTS[21],
                ],
            },
            200,
            id='get processed',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-withdrawal', 'dst': 'personal'}],
)
@pytest.mark.now('2021-06-22T22:40:25.077345+03:00')
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_withdrawal_list(
        mock_eats_tips_partners,
        web_app_client,
        web_context,
        mockserver,
        jwt,
        get_processed,
        date_from,
        date_to,
        multi_filter,
        expected_result,
        expected_status,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    @mockserver.json_handler('/personal/v1/identifications/store')
    def _mock_identifications_store(request):
        return {
            'value': request.json['value'],
            'id': FULLNAME_MAP[request.json['value']],
        }

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_identifications_retrieve(request):
        fullname = ''
        for fullname, fullname_id in FULLNAME_MAP.items():
            if fullname_id == request.json['id']:
                break
        return {'value': fullname, 'id': request.json['id']}

    @mockserver.json_handler('/personal/v1/identifications/bulk_retrieve')
    def _mock_identifications_bulk_retrieve(request):
        fullname_map = {
            fullname_id: fullname
            for fullname, fullname_id in FULLNAME_MAP.items()
        }
        return {
            'items': [
                {'id': item['id'], 'value': fullname_map.get(item['id'], '')}
                for item in request.json['items']
            ],
        }

    params = {}
    if date_from is not None:
        params['start_date'] = date_from
    if date_to is not None:
        params['finish_date'] = date_to
    if get_processed is not None:
        params['finished_requests'] = str(get_processed)
    if multi_filter is not None:
        params['multi_filter'] = multi_filter
    response = await web_app_client.get(
        '/v1/withdrawal/accountant/requests-list',
        params=params,
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
