import copy
import json

import pytest


URL = 'userplaces/events'
USER_ID = '12345678901234567890123456789012'
USER_UID = '123456'
USER_TICKET = 'ticket'

DEFAULT_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Yandex-UID': USER_UID,
    'X-Ya-User-Ticket': USER_TICKET,
}

DEFAULT_REQUEST = {
    'min_timestamp': '2020-01-06T23:00:00+0000',
    'max_timestamp': '2020-02-06T20:30:00+0000',
    'max_number': 2,
    'lang': 'ru',
    'position': [37.5, 55.5],
}

AFISHA_QUERY = (
    '{ userProfile { orders( sessionDates: {date: "2020-01-07", period: 31 } '
    'futureOnly: true sort: sessionDate paging: { limit: 2, offset: 0 } ) '
    '{ items { date event {title type {code}} place { title '
    'id address coordinates { latitude longitude } } } } } }'
)


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_userplacesevents_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 500, response.text
    assert response.headers['Retry-After'] == '120'
    assert response.json() == {'code': '500', 'message': 'Service disabled'}


@pytest.mark.config(USERPLACES_USE_AFISHA=False)
async def test_userplacesevents_afisha_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}


async def test_userplacesevents_afisha_simple(
        taxi_userplaces, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/afisha-draqla/graphql')
    def _mock_afisha_draqla(request):
        assert request.headers['X-Ya-User-Ticket'] == USER_TICKET
        expected_req = {'query': AFISHA_QUERY, 'lon': 37.5, 'lat': 55.5}
        assert json.loads(request.get_data()) == expected_req
        return load_json('afisha_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    yamaps.set_checks({'spn': '0.005000,0.005000'})

    response = await taxi_userplaces.post(
        URL, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


async def test_userplacesevents_afisha_skip_geosearch(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/afisha-draqla/graphql')
    def _mock_afisha_draqla(request):
        assert request.headers['X-Ya-User-Ticket'] == USER_TICKET
        assert json.loads(request.get_data())['query'] == AFISHA_QUERY
        return load_json('afisha_response.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['skip_geosearch'] = True

    response = await taxi_userplaces.post(
        URL, json=request, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_skip_geosearch.json',
    )


async def test_userplacesevents_afisha_error(taxi_userplaces, mockserver):
    @mockserver.json_handler('/afisha-draqla/graphql')
    def _mock_afisha_draqla(request):
        return mockserver.make_response('{}', 500)

    response = await taxi_userplaces.post(
        URL, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}


async def test_userplacesevents_afisha_timeout(taxi_userplaces, mockserver):
    @mockserver.json_handler('/afisha-draqla/graphql')
    def _mock_afisha_draqla(request):
        raise mockserver.TimeoutError()

    response = await taxi_userplaces.post(
        URL, json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}
