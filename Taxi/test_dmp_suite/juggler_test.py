import pytest
from collections import namedtuple
from itertools import chain
from mock import mock

from dmp_suite.critical import critical_flag
from init_py_env import service as dwh_service

from dmp_suite.juggler import (
    JugglerClient,
    Event,
    ErrorWrongRequest,
    ErrorWrongEvents,
    EventStatus,
)

juggler_host = 'http://localhost/events'
app_host_name = 'test.dwh.taxi'
event_ok = {'app_host_name': app_host_name, 'status': EventStatus.OK,
            'service': 'test_service', 'description': 'desc'}
event_ok_raw = {'instance': '', 'host': app_host_name, 'tags': [dwh_service.name],
                'status': 'OK', 'service': 'test_service',
                'description': 'desc'}
event_crit = {'app_host_name': app_host_name, 'status': EventStatus.CRIT,
              'service': 'test_service', 'description': 'desc',
              'instance': 'inst'}
event_crit_raw = {'host': app_host_name, 'tags': [dwh_service.name], 'status': 'CRIT',
                  'service': 'test_service',
                  'description': 'desc', 'instance': 'inst'}
event_ok_parameterized = {'app_host_name': f'{app_host_name}.subhost', 'status': EventStatus.OK,
                          'service': 'test_service', 'description': 'desc'}
event_ok_parameterized_raw = {'instance': '', 'host': f'{app_host_name}.subhost', 'tags': [dwh_service.name],
                              'status': 'OK', 'service': 'test_service',
                              'description': 'desc'}
event_crit_parameterized = {'app_host_name': f'{app_host_name}.subhost', 'status': EventStatus.CRIT,
                            'service': 'test_service', 'description': 'desc',
                            'instance': 'inst'}
event_crit_parameterized_raw = {'host': f'{app_host_name}.subhost', 'tags': [dwh_service.name], 'status': 'CRIT',
                                'service': 'test_service',
                                'description': 'desc', 'instance': 'inst'}

timeout = 10


def get_api_response(events, resp_type='ok'):
    """emulate response from juggler  api"""
    Resp = namedtuple('resp',
                      ('status_code', 'json', 'text', 'raise_for_status'))
    if resp_type == 'ok':
        data = {"accepted_events": len(events),
                "events": [{"code": 200}] * len(events), "success": True}
    elif resp_type == 'one_err':
        events = [{"code": 200}] * (len(events) - 1) + [
            {'code': 400, 'error': 'Error text'}]
        data = {"accepted_events": len(events) - 1, "events": events,
                "success": True}
    elif 'err':
        data = {"message": "Expecting value: line 1 column 1 (char 0)",
                "success": False}

    return Resp(200, lambda: data, '', raise_for_status=lambda: 0)


def test_event_serializer():
    params = {'host': 'host', 'service': 'srvc', 'status': EventStatus.OK,
              'description': 'desc'}
    e = Event(**params)
    expected = params.copy()
    expected['instance'] = ''
    # В список тегов всегда добавляется DWH сервис:
    expected['tags'] = [dwh_service.name]
    expected['status'] = 'OK'
    assert expected == e.to_dict()


def test_event_in_critical_code():
    # Если событие генерируется в коде, который помечен,
    # как критический, то в списке тегов должен появиться 'critical'

    params = {'host': 'host', 'service': 'srvc', 'status': EventStatus.OK,
              'description': 'desc'}

    with critical_flag():
        e = Event(**params)

    expected = params.copy()
    expected['instance'] = ''
    # Помимо DWH сервиса в тегах должен быть 'critical'
    expected['tags'] = [dwh_service.name, 'critical']
    expected['status'] = 'OK'
    assert expected == e.to_dict()


def test_event_validator():
    with pytest.raises(ValueError):
        Event('h', 's', 'OOK', 'd')


def test_client_send_ok_events():
    client = JugglerClient(juggler_host, app_host_name, timeout=timeout)
    events = [event_ok, event_crit]
    with mock.patch('requests.post',
                    return_value=get_api_response(events)) as post:
        for ev in events:
            client.add_base_event(**{k: v for k, v in ev.items() if k != 'app_host_name'})
        client.send()
    post.assert_called_with(juggler_host, json={'source': 'taxidwh-etl',
                                                'events': [event_ok_raw,
                                                           event_crit_raw]},
                            timeout=timeout)


def test_client_correct_last_chunk():
    client = JugglerClient(juggler_host, app_host_name, timeout=timeout, chunk_size=100)

    events1 = [event_ok, ] * 100
    events2 = [event_ok, ] * 50
    with mock.patch('requests.post',
                    return_value=get_api_response(events2)) as post:
        for ev in chain(events1, events2):
            client.add_base_event(**{k: v for k, v in ev.items() if k != 'app_host_name'})
        client.send()
    post.assert_called_with(juggler_host, json={'source': 'taxidwh-etl',
                                                'events': [event_ok_raw, ] * 50},
                            timeout=timeout)


def test_client_with_err_response():
    client = JugglerClient(juggler_host, app_host_name)
    events = [event_ok, ]
    with mock.patch('requests.post',
                    return_value=get_api_response(events, 'err'), ):
        with pytest.raises(ErrorWrongRequest):
            client.add_base_event(**{k: v for k, v in events[0].items() if k != 'app_host_name'})
            client.send()


def test_client_with_err_in_response():
    client = JugglerClient(juggler_host, app_host_name)
    events = [event_ok, ]
    with mock.patch('requests.post',
                    return_value=get_api_response(events, 'one_err'), ):
        client.add_base_event(**{k: v for k, v in events[0].items() if k != 'app_host_name'})
        with pytest.raises(ErrorWrongEvents):
            client.send()


def test_client_send_ok_parameterized_events():
    client = JugglerClient(juggler_host, app_host_name, timeout=timeout)
    events = [event_ok_parameterized, event_crit_parameterized]
    with mock.patch('requests.post',
                    return_value=get_api_response(events)) as post:
        for ev in events:
            args = {**ev, 'app_host_name': ev['app_host_name'][len(app_host_name) + 1:]}
            client.add_event(**args)
        client.send()
    post.assert_called_with(juggler_host, json={'source': 'taxidwh-etl',
                                                'events': [event_ok_parameterized_raw,
                                                           event_crit_parameterized_raw]},
                            timeout=timeout)
