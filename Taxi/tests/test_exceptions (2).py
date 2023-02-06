import freezegun
import pytest

from taxi.robowarehouse.lib.misc import exceptions


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_error():
    with pytest.raises(exceptions.Error) as e:
        raise exceptions.Error()

    expected = {
        'code': 'ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'An error has occurred',
    }

    assert e.value.status_code == 500
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_error_custom_params():
    with pytest.raises(exceptions.Error) as e:
        raise exceptions.Error(code='ERR', message='msg', entity_id='123')

    expected = {
        'code': 'ERR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'entity_id': '123'},
        'message': 'msg',
    }

    assert e.value.status_code == 500
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_not_found_error():
    with pytest.raises(exceptions.NotFoundError) as e:
        raise exceptions.NotFoundError()

    expected = {
        'code': 'NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Entity not found',
    }

    assert e.value.status_code == 404
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_validation_error():
    with pytest.raises(exceptions.ValidationError) as e:
        raise exceptions.ValidationError()

    expected = {
        'code': 'VALIDATION_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Bad request',
    }

    assert e.value.status_code == 400
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_authentication_error():
    with pytest.raises(exceptions.AuthenticationError) as e:
        raise exceptions.AuthenticationError()

    expected = {
        'code': 'AUTHENTICATION_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Authentication error',
    }

    assert e.value.status_code == 401
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_authorization_error():
    with pytest.raises(exceptions.AuthorizationError) as e:
        raise exceptions.AuthorizationError()

    expected = {
        'code': 'AUTHORIZATION_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Authorization error',
    }

    assert e.value.status_code == 403
    assert e.value.to_dict() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_conflict_error():
    with pytest.raises(exceptions.ConflictError) as e:
        raise exceptions.ConflictError()

    expected = {
        'code': 'CONFLICT_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Conflict',
    }

    assert e.value.status_code == 409
    assert e.value.to_dict() == expected
