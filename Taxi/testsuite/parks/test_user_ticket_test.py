import pytest

from . import error

# tvmknife unittest user -d 11 -e test
ya_ticket = (
    '3:user:CA0Q__________9_Gg4KAggLEAsg0oXYzAQoAQ:DojcKSrUg7PrAw8'
    'nHx5KdjK4C4h-6HyDlY-1AeI1xRQvWD3Vb7ZGPQDglxI9z3ZyeqxVZMk-HITg'
    'axs08KduGkkr-EjvD7HscICl7Nug78o4_wnPezs61OfOT7V_8mpLZMgYyk-md'
    'uYEfJd1yAyYq1mmzxkQMEhINJqOLtrlwVE'
)

# tvmknife unittest user -d 11 -e test_yateam
ya_team_ticket = (
    '3:user:CA4Q__________9_Gg4KAggLEAsg0oXYzAQoAw:FlueTmNfeh'
    'T-JYnBi1DS7EDl4m5WPBoD2wGPGIIaoADoitZTUwsan8hTs-M-m7wQXH'
    'lzBiL3keG_OuER5bMqVPRkbB5YJFJSWAI8njjYIRS3TQsUjvE3p2a1Mn'
    '9rolq0LS-8YaPHScA45cVidUTd8q67htFOvyplYTCtsu5Wajk'
)


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=False)
@pytest.mark.parametrize(
    'ticket, code, expected_response',
    [
        (
            {'provider': 'ya', 'ticket': ''},
            401,
            error.make_error_response('can not extract user id'),
        ),
        (
            {'provider': 'ya-team', 'ticket': ''},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya', 'ticket': ya_ticket}, 200, 'b'),
        (
            {'provider': 'ya-team', 'ticket': ya_ticket},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya-team', 'ticket': ya_team_ticket}, 200, 'b'),
        (
            {'provider': 'ya', 'ticket': ya_team_ticket},
            401,
            error.make_error_response('can not extract user id'),
        ),
        (
            {'provider': 'ya', 'ticket': '_!fake!_ya-255'},
            401,
            error.make_error_response('can not extract user id'),
        ),
        (
            {'provider': 'ya-team', 'ticket': '_!fake!_ya-team-255'},
            401,
            error.make_error_response('can not extract user id'),
        ),
    ],
)
def test_tickets1(taxi_parks, ticket, code, expected_response):
    response = taxi_parks.post('/user-ticket-test', json=ticket)

    assert response.status_code == code
    assert response.json() == expected_response


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
@pytest.mark.parametrize(
    'ticket, code, expected_response',
    [
        (
            {'provider': 'ya', 'ticket': ''},
            401,
            error.make_error_response('can not extract user id'),
        ),
        (
            {'provider': 'ya-team', 'ticket': ''},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya', 'ticket': ya_ticket}, 200, 'b'),
        (
            {'provider': 'ya-team', 'ticket': ya_ticket},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya-team', 'ticket': ya_team_ticket}, 200, 'b'),
        (
            {'provider': 'ya', 'ticket': ya_team_ticket},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya', 'ticket': '_!fake!_ya-255'}, 200, 'ff'),
        (
            {'provider': 'ya', 'ticket': '_!fake!_ya_team-255'},
            401,
            error.make_error_response('can not extract user id'),
        ),
        (
            {'provider': 'ya-team', 'ticket': '_!fake!_ya-255'},
            401,
            error.make_error_response('can not extract user id'),
        ),
        ({'provider': 'ya-team', 'ticket': '_!fake!_ya-team-255'}, 200, 'ff'),
        (
            {'provider': 'ya', 'ticket': '_!fake!_ya-0'},
            401,
            error.make_error_response('there is no default user in ticket'),
        ),
        (
            {'provider': 'ya-team', 'ticket': '_!fake!_ya-team-0'},
            401,
            error.make_error_response('there is no default user in ticket'),
        ),
    ],
)
def test_tickets2(taxi_parks, ticket, code, expected_response):
    response = taxi_parks.post('/user-ticket-test', json=ticket)

    assert response.status_code == code
    assert response.json() == expected_response
