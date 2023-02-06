import pytest

OUTDATED_ETAG = '"Q8J0yel5i5aER7OY"'
UP_TO_DATE_ETAG = '"2Q5xmbmQijboKM7W"'
FUTURE_ETAG = '"7O9pgenriGeNQxy0"'
INVALID_ETAG = '"0123456789abcdef"'


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'mode_home.sql'])
def test_state_empty_db(taxi_reposition, pgsql, etag):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = taxi_reposition.post(
        '/v2/reposition/state?uuid=uuid&dbid=dbid777', headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        'state': {'status': 'no_state'},
        'usages': {
            'home': {
                'start_screen_usages': {'title': '', 'subtitle': ''},
                'usage_allowed': True,
                'usage_limit_dialog': {'title': '', 'body': ''},
            },
        },
    }


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.parametrize('state', ['empty', 'active', 'disabled', 'bonus'])
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
def test_state(taxi_reposition, pgsql, load, load_json, state, etag):
    queries = [load('drivers.sql')]
    queries.append(load(state + '_state.sql'))
    pgsql['reposition'].apply_queries(queries)

    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = taxi_reposition.post(
        '/v2/reposition/state?uuid=uuid&dbid=dbid777', headers=headers,
    )

    if etag is None or etag == OUTDATED_ETAG or etag == INVALID_ETAG:
        assert response.status_code == 200
        assert response.json() == load_json(state + '_state.json')
        assert response.headers['ETag'] == UP_TO_DATE_ETAG
    else:
        assert response.status_code == 304


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'header_data, error_text',
    [
        ({}, 'header X-Ya-Service-Ticket is absent'),
        ({'X-Ya-Service-Ticket': ''}, 'header X-Ya-Service-Ticket is absent'),
        ({'X-Ya-Service-Ticket': 'INVALID-TOKEN-VALUE'}, 'invalid ticket'),
    ],
)
def test_check_tvm2(header_data, error_text, taxi_reposition):
    response = taxi_reposition.post(
        '/v2/reposition/state', headers=header_data, data={},
    )
    assert response.status_code == 401
    assert response.json() == {'error': {'text': error_text}}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
    TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
)
@pytest.mark.parametrize(
    'service_access',
    [
        ({'reposition': {'/v2/reposition/state': []}}),
        ({'reposition': {'/v2/reposition/state': ['protocol']}}),
    ],
)
def test_check_tvm2_access_deny(taxi_reposition, config, service_access, load):
    config.set_values(dict(TVM_SERVICE_HANDLER_ACCESS=service_access))
    response = taxi_reposition.post(
        '/v2/reposition/state',
        headers={'X-Ya-Service-Ticket': load('tvm2_ticket_19_18')},
        data={},
    )
    assert response.status_code == 401
    assert response.json() == {'error': {'text': 'Unauthorized'}}


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'empty_state.sql'])
@pytest.mark.parametrize(
    'tvm_enabled,tvm_header,service_access_enabled,service_access',
    [
        (False, True, None, None),
        (True, True, False, None),
        (True, True, True, {}),
        (True, True, True, {'reposition': {}}),
        (
            True,
            True,
            True,
            {'reposition': {'/v2/reposition/state': ['driver_protocol']}},
        ),
    ],
)
def test_check_tvm2_access_allow(
        config,
        tvm_enabled,
        tvm_header,
        service_access_enabled,
        service_access,
        taxi_reposition,
        load,
        load_json,
):
    config.set_values(
        dict(
            TVM_ENABLED=tvm_enabled,
            TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
            TVM_SERVICE_HANDLER_ACCESS_ENABLED=service_access_enabled,
            TVM_SERVICE_HANDLER_ACCESS=service_access
            if service_access
            else {},
        ),
    )

    response = taxi_reposition.post(
        '/v2/reposition/state?uuid=uuid&dbid=dbid777',
        headers={
            'Accept-Language': 'en-EN',
            'X-Ya-Service-Ticket': load('tvm2_ticket_19_18'),
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json('empty_state.json')
