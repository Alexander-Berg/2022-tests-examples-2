import pytest

from tests_coupons import util
from tests_coupons.admin import common

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

AUTHOR = {'X-YaTaxi-Draft-Author': 'super-author', 'X-Yandex-Uid': '007'}
HEADERS = {'add': dict(common.HEADERS, **AUTHOR), 'add_first_limit': AUTHOR}
NEW_SERIES = common.GOOD_CHANGES['firstlimit']
HANDLERS = {
    'basic': 'add',
    'externalbudget': 'add',
    'firstlimit': 'add_first_limit',
}


@pytest.mark.now('2016-12-01T12:00:00.0')
@pytest.mark.parametrize(
    'handler, headers, series, expected_code',
    [
        # no ticket header
        *[
            pytest.param(
                'add',
                AUTHOR,
                f'new{series}',
                {'check': 200, 'apply': 400},
                id=f'add: no ticket header ({series})',
            )
            for series in ('basic', 'externalbudget')
        ],
        # series already exists
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                400,
                id=f'{handler}: series {series} already exists',
            )
            for series, handler in HANDLERS.items()
        ],
        # wrong handler
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                400,
                id=f'{handler}: wrong handler for {series} series',
            )
            for series in HANDLERS
            for handler in HANDLERS.values()
            if HANDLERS[series] != handler
        ],
        # ok data
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                f'new{series}',
                200,
                id=f'{handler}: ok {series}',
            )
            for series, handler in HANDLERS.items()
        ],
        # other cases are covered by test_edit checks
    ],
)
@pytest.mark.parametrize('mode', common.HANDLE_MODES)
async def test_add(
        make_admin_request,
        handler,
        headers,
        series,
        mode,
        expected_code,
        tariffs,
        mongodb,
):
    if isinstance(expected_code, dict):
        expected_code = expected_code[mode]

    data = dict(NEW_SERIES, **{'series_id': series})
    if 'firstlimit' in series:
        data['first_limit'] = 1
    if 'externalbudget' in series:
        data['external_budget'] = True

    response = await make_admin_request(data, mode, handler, headers)
    assert response.status_code == expected_code

    if expected_code == 200:
        response_json = util.sort_json(response.json(), common.PATH_TO_SORT)
        sorted_req_data = util.sort_json(data, common.FIELDS_TO_SORT)
        if mode == 'check':
            assert response_json['data'] == sorted_req_data
            assert tariffs.times_called == 0
        else:
            assert response_json['series'] == series
            assert response_json['action'] == 'add'
            assert tariffs.times_called == 1

            args_find_series = ({'_id': series}, {'updated_at': 0})
            doc = mongodb.promocode_series.find_one(*args_find_series)
            sorted_doc = util.sort_json(doc, common.FIELDS_TO_SORT)

            for key in common.prepare_update_data(sorted_req_data):
                assert sorted_doc[key] == sorted_req_data[key]

            for key, value in common.CALCULATED[series[len('new') :]].items():
                assert sorted_doc[key] == value

            assert doc.get('ticket') == headers.get('X-YaTaxi-Draft-Tickets')
            assert doc.get('external_budget', False) == data.get(
                'external_budget', False,
            )
            assert doc.get('first_limit') == data.get('first_limit')
            assert doc['creator'] == {'login': 'super-author', 'uid': '007'}
            assert doc['created'].strftime(common.DATE_FORMAT) == '2016-12-01'

            assert sorted_doc == common.prepare_update_data(
                response_json['update']['$set'], fmt=TIMESTAMP_FORMAT,
            )
