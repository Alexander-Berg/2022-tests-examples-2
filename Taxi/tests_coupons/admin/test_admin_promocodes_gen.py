import datetime

import pytest


HEADERS = {'gen': {'X-YaTaxi-Draft-Tickets': 'TAXIRATE-4'}}
REQ_PARAMS = {'count': 15, 'email': 'self@ya.ru'}
HANDLERS = {
    'basic': 'gen',
    'externalbudget': 'gen',
    'firstlimit': 'gen_first_limit',
}
HANDLE_MODES = ['check', 'apply']


def prepare_db_data(db, series_id, db_data):
    if not db_data:
        return

    if '_id' in db_data:
        new_series_id = db_data['_id']
        doc = db.promocode_series.find_one({'_id': series_id})
        doc['_id'] = new_series_id
        db.promocode_series.insert_one(doc)
        return

    if 'status' in db_data:
        db.promocode_gen.insert_one(
            {
                'series_id': series_id,
                'status': db_data['status'],
                'promocodes_count': 10,
                'error_message': '',
                'email': 'ya@ya.ru',
                'created': datetime.datetime.now(),
            },
        )

    to_unset = {key: True for key, value in db_data.items() if value is None}
    to_set = {key: db_data[key] for key in set(db_data) - set(to_unset)}
    update = {'$set': to_set} if to_set else {'$unset': to_unset}
    db.promocode_series.update_one({'_id': series_id}, update)


@pytest.mark.parametrize(
    'handler, headers, series, db_data, expected_code',
    [
        # no ticket header
        *[
            pytest.param(
                'gen',
                None,
                series,
                None,
                {'check': 200, 'apply': 400},
                id=f'gen: no ticket header ({series})',
            )
            for series in ('basic', 'externalbudget')
        ],
        # series not found
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                'notexist',
                None,
                404,
                id=f'{handler}: series not found',
            )
            for handler in HANDLERS.values()
        ],
        # wrong handler
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                None,
                400,
                id=f'{handler}: wrong handler for {series} series',
            )
            for series in HANDLERS
            for handler in HANDLERS.values()
            if HANDLERS[series] != handler
        ],
        # bad series cases
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                db_data,
                400,
                id=f'{handler}: {text} ({series})',
            )
            for series, handler in HANDLERS.items()
            for db_data, text in (
                ({'_id': '12'}, 'two-digit series'),
                ({'clear_text': False}, 'false clear_text'),
                ({'clear_text': None}, 'no clear_text'),
                ({'is_unique': False}, 'not unique'),
                ({'for_support': True}, 'for support'),
            )
        ],
        # bad/ok last gen statuses
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                {'status': status},
                200
                if status == 'completed'
                and series != 'basic'
                or status == 'failed'
                else 400,
                id=f'{handler}: {series} with {status} gen',
            )
            for series, handler in HANDLERS.items()
            for status in ('pending', 'processing', 'failed', 'completed')
        ],
        # ok data
        *[
            pytest.param(
                handler,
                HEADERS.get(handler),
                series,
                None,
                200,
                id=f'{handler}: ok {series}',
            )
            for series, handler in HANDLERS.items()
        ],
    ],
)
@pytest.mark.parametrize('mode', HANDLE_MODES)
async def test_gen(
        make_admin_request,
        handler,
        headers,
        series,
        db_data,
        mode,
        expected_code,
        mongodb,
        stq,
):
    if isinstance(expected_code, dict):
        expected_code = expected_code[mode]

    prepare_db_data(mongodb, series, db_data)
    if db_data:
        series = db_data.get('_id', series)
    data = dict(REQ_PARAMS, **{'series_id': series})

    response = await make_admin_request(data, mode, handler, headers)
    assert response.status_code == expected_code

    if expected_code == 200:
        response_json = response.json()
        if mode == 'check':
            assert response_json['data'] == data
        else:
            assert response_json['series'] == series
            assert response_json['action'] == 'gen'

            gen_doc = mongodb.promocode_gen.find_one({'status': 'pending'})
            assert gen_doc['series_id'] == series
            assert gen_doc['email'] == data['email']
            assert gen_doc['promocodes_count'] == data['count']

            assert stq.generate_promocodes.times_called == 1

            stq_request_params = stq.generate_promocodes.next_call()
            assert stq_request_params['queue'] == 'generate_promocodes'
            assert (
                stq_request_params['id']
                == stq_request_params['args'][0]
                == gen_doc['_id']
            )


@pytest.mark.config(COUPONS_PROMOCODE_GENERATE_NEW_WORKERS_ENABLED=False)
async def test_gen_fallback(make_admin_request, mongodb, stq):
    series = 'basic'
    data = dict(REQ_PARAMS, **{'series_id': series})

    response = await make_admin_request(data, 'apply', 'gen', HEADERS['gen'])
    assert response.status_code == 200

    gen_doc = mongodb.promocode_gen.find_one({'status': 'pending'})
    assert gen_doc['series_id'] == series
    assert stq.promocodes_generate.times_called == 1

    stq_request_params = stq.promocodes_generate.next_call()
    assert stq_request_params['queue'] == 'promocodes_generate'
    assert (
        stq_request_params['id']
        == stq_request_params['args'][0]
        == gen_doc['_id']
    )
