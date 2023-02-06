# import pytest
from taxi_tests import utils


EXP_ERROR_MSG = 'Expected experiment has not been launched in time'


def test_without_session(protocol):
    data = protocol.launch({})
    assert not data['authorized']
    assert 'id' in data
    assert data.get('uuid')
    assert 'phone' not in data


def test_empty_session(protocol, session_maker):
    session = session_maker()
    data = protocol.launch({}, session=session)
    assert not data['authorized']
    assert 'id' in data
    assert data.get('uuid')
    assert 'phone' not in data


def test_no_phone(protocol, session_maker):
    session = session_maker()
    session.init()
    data = protocol.launch({}, session=session)
    assert not data['authorized']
    assert 'id' in data
    assert 'phone' not in data


def test_random_phone(protocol, session_maker):
    session = session_maker()
    session.init(phone='random')
    data = protocol.launch({}, session=session)
    assert data['authorized']
    assert 'id' in data
    assert 'phone' in data
    user_id = data['id']
    phone = data['phone']
    assert phone.startswith('+7')
    assert phone[2] != 9
    del data['server_time']
    del data['typed_experiments']

    data2 = protocol.launch({'id': user_id}, session=session)
    del data2['server_time']
    del data2['typed_experiments']
    assert data == data2


def test_my_phone(protocol, session_maker):
    phone = '+79778638009'
    session = session_maker()
    session.init(phone=phone)
    data = protocol.launch({}, session=session)
    assert data['authorized']
    assert 'id' in data
    assert data.get('phone') == phone


def test_session_id(protocol, session_maker):
    session = session_maker(method='session_id', user_agent=None)
    session.init(phone='random')
    data = protocol.launch({}, session=session)
    assert not data['authorized']
    assert 'id' in data

    auth_data = {
        'id': data['id'],
        'name': 'alberist',
        'phone': session.phone,
    }
    auth_response = protocol.post('/3.0/auth', auth_data, session=session)
    assert auth_response.status_code == 200
    assert auth_response.json() == {'authorized': True}

    data = protocol.launch({}, session=session)
    assert data['authorized']
    assert data.get('phone') == session.phone


def test_passport_500(protocol, session_maker):
    session = session_maker()
    session.init(response_code=500)
    response = protocol.post('/3.0/launch', {}, session=session)
    assert response.status_code == 500


def test_invalid_session(protocol, session_maker):
    session = session_maker()
    session.init(status='INVALID', phone='random')
    data = protocol.launch({}, session=session)
    assert not data['authorized']
    assert 'id' in data


def test_is_staff(protocol, session_maker):
    session = session_maker()
    session.init(is_staff=True, phone='random')
    data = protocol.launch({}, session=session)
    assert data['authorized']
    assert data.get('yandex_staff')


def test_auth_after(protocol, session_maker):
    session = session_maker()
    data = protocol.launch({}, session=session)
    assert not data['authorized']
    assert 'id' in data
    user_id = data['id']

    session.init(phone='random')
    data = protocol.launch({'id': user_id}, session=session)
    assert data['authorized']
    assert data.get('phone') == session.phone
    assert data.get('id') == user_id


def test_exp(protocol, exp, session_maker):
    name = exp.add_experiment(
        clauses=[
            {'title': 'default', 'predicate': {'type': 'true'}, 'value': 1},
        ],
    )
    expected_item = {'name': name, 'value': 1}

    session = session_maker()
    session.init(phone='+79031520355')
    for _ in utils.wait_for(1000, EXP_ERROR_MSG):
        data = protocol.launch(
            {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}, session=session,
        )

        for item in data.get('typed_experiments')['items']:
            if item == expected_item:
                return
