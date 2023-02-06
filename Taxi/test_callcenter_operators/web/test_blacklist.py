import pytest

from test_callcenter_operators import test_utils


DISP_CC_LIST_RESPONSE = {
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSMSG': '',
    'STATUSDESC': None,
    'STATUS': 'TRUE',
    'PARAM': {},
    'DATA': {
        '0': {
            'ID': '13386437',
            'QUEUE': 'disp_cc',
            'SRCNUMB': '1234567890',
            'ACTIONID': '400',
            'ACTIONDATA': '',
            'STREAMSRC': '',
            'EXPIREDATE': '1588168130',
        },
        '1': {
            'ID': '1660644',
            'QUEUE': 'disp_cc',
            'SRCNUMB': '37443214852',
            'ACTIONID': '100',
            'ACTIONDATA': '80086',
            'STREAMSRC': '',
            'EXPIREDATE': '0',
        },
    },
}

HELP_CC_LIST_RESPONSE = {
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSMSG': '',
    'STATUSDESC': None,
    'STATUS': 'TRUE',
    'PARAM': {},
    'DATA': {
        '0': {
            'ID': '13386437',
            'QUEUE': 'help_cc',
            'SRCNUMB': '1234567890',
            'ACTIONID': '100',
            'ACTIONDATA': '425',
            'STREAMSRC': '',
            'EXPIREDATE': '1588168130',
        },
        '1': {
            'ID': '1659623',
            'QUEUE': 'help_cc',
            'SRCNUMB': '1234567891',
            'ACTIONID': '400',
            'ACTIONDATA': '',
            'STREAMSRC': '',
            'EXPIREDATE': '1588168130',
        },
    },
}


@pytest.mark.now('2000-04-29 13:48:50')
@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_show(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        if 'disp_cc' in request.path_qs.lower():
            return DISP_CC_LIST_RESPONSE
        if 'help_cc' in request.path_qs.lower():
            return HELP_CC_LIST_RESPONSE
        raise NotImplementedError

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list', json={},
    )
    assert resp.status == 200
    res_json = await resp.json()
    assert res_json == {
        'blacklist': [
            {
                'expiration_date': '2020-04-29T16:48:50+0300',
                'queue': 'disp_cc',
                'tel_number': '1234567890',
            },
            {
                'expiration_date': '2020-04-29T16:48:50+0300',
                'queue': 'help_cc',
                'tel_number': '1234567891',
            },
        ],
    }


@pytest.mark.now('2020-04-29 13:50:00')
@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_show_past_expiration(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        if 'disp_cc' in request.path_qs.lower():
            return DISP_CC_LIST_RESPONSE
        if 'help_cc' in request.path_qs.lower():
            return HELP_CC_LIST_RESPONSE
        raise NotImplementedError

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list', json={},
    )
    assert resp.status == 200
    res_json = await resp.json()
    assert res_json == {'blacklist': []}


@pytest.mark.now('2000-04-29 13:50:00')
@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_show_queues(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        if 'disp_cc' in request.path_qs.lower():
            return DISP_CC_LIST_RESPONSE
        if 'help_cc' in request.path_qs.lower():
            return HELP_CC_LIST_RESPONSE
        raise NotImplementedError

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list',
        json={'queues': ['disp_cc']},
    )
    assert resp.status == 200
    res_json = await resp.json()
    assert res_json == {
        'blacklist': [
            {
                'expiration_date': '2020-04-29T16:48:50+0300',
                'queue': 'disp_cc',
                'tel_number': '1234567890',
            },
        ],
    }


@pytest.mark.now('2000-04-29 13:50:00')
@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_show_number(mockserver, taxi_callcenter_operators_web):
    number = '1234567891'
    disp_number_response = {
        'TYPE': 'REPLY',
        'STATUSCODE': 200,
        'STATUSMSG': '',
        'STATUSDESC': None,
        'STATUS': 'TRUE',
        'PARAM': {},
        'DATA': {
            '0': {
                'ID': '1659623',
                'QUEUE': 'disp_cc',
                'SRCNUMB': number,
                'ACTIONID': '400',
                'ACTIONDATA': '',
                'STREAMSRC': '',
                'EXPIREDATE': '1588168130',
            },
        },
    }
    help_number_response = {
        'TYPE': 'REPLY',
        'STATUSCODE': 200,
        'STATUSMSG': '',
        'STATUSDESC': None,
        'STATUS': 'TRUE',
        'PARAM': {},
        'DATA': {},
    }

    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        if (
                f'list/{number}' in request.path_qs.lower()
                and 'disp_cc' in request.path_qs.lower()
        ):
            return disp_number_response
        if (
                f'list/{number}' in request.path_qs.lower()
                and 'help_cc' in request.path_qs.lower()
        ):
            return help_number_response
        raise NotImplementedError

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list',
        json={'tel_number': '1234567891'},
    )
    assert resp.status == 200
    res_json = await resp.json()
    assert res_json == {
        'blacklist': [
            {
                'expiration_date': '2020-04-29T16:48:50+0300',
                'queue': 'disp_cc',
                'tel_number': number,
            },
        ],
    }


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_block(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _handle_urls(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/add_bulk',
        json={
            'to_block': [
                {
                    'tel_number': '79999999999',
                    'expires_in': 30,
                    'queues': ['disp_cc', 'help_cc'],
                },
            ],
        },
    )
    assert resp.status == 200
    assert await resp.json() == {'unhandled_numbers': []}


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_block_bad_pattern(mockserver, taxi_callcenter_operators_web):

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/add_bulk',
        json={
            'to_block': [
                {
                    'tel_number': 'abc16832',
                    'expires_in': 30,
                    'queues': ['disp_cc', 'help_cc'],
                },
            ],
        },
    )
    assert resp.status == 400


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_bad_block(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _handle_urls(request):
        return test_utils.make_bad_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/add_bulk',
        json={
            'to_block': [
                {
                    'tel_number': '79999999999',
                    'expires_in': 30,
                    'queues': ['disp_cc', 'help_cc'],
                },
            ],
        },
    )
    assert resp.status == 200
    assert await resp.json() == {
        'unhandled_numbers': [
            {'tel_number': '79999999999', 'queues': ['disp_cc', 'help_cc']},
        ],
    }


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_unblock(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _handle_urls(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/delete_bulk',
        json={
            'to_unblock': [
                {
                    'tel_number': '79999999999',
                    'queues': ['disp_cc', 'help_cc'],
                },
            ],
        },
    )
    assert resp.status == 200
    assert await resp.json() == {'unhandled_numbers': []}


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_unblock_bad_pattern(mockserver, taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/delete_bulk',
        json={
            'to_unblock': [
                {'tel_number': 'abc1728156', 'queues': ['disp_cc', 'help_cc']},
            ],
        },
    )
    assert resp.status == 400


@pytest.mark.config(
    CALLCENTER_OPERATORS_BLACKLIST_ALLOWED_QUEUES=['disp_cc', 'help_cc'],
)
async def test_bad_unblock(mockserver, taxi_callcenter_operators_web):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _handle_urls(request):
        return test_utils.make_bad_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/black_list/delete_bulk',
        json={
            'to_unblock': [
                {
                    'tel_number': '79999999999',
                    'queues': ['disp_cc', 'help_cc'],
                },
            ],
        },
    )
    assert resp.status == 200
    assert await resp.json() == {
        'unhandled_numbers': [
            {'tel_number': '79999999999', 'queues': ['disp_cc', 'help_cc']},
        ],
    }
