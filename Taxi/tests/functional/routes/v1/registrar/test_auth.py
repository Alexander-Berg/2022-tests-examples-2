import datetime

import pytest
import freezegun

from taxi.robowarehouse.lib.concepts import registrars
from taxi.robowarehouse.lib.concepts import registrars_auth
from taxi.robowarehouse.lib.test_utils.helpers import convert_to_frontend_response
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc.helpers import generate_url_token
from taxi.robowarehouse.lib.misc.helpers import sign_payload
from taxi.robowarehouse.lib.misc.helpers import base64url_encode
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.config import settings


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_signup(client):
    now = datetime_utils.get_now()
    registrar = await registrars.factories.create(phone='1234')
    telegram_id = 'test123'
    response = await client.post(
        '/registrar/v1/auth/signup/',
        json={'phone': '1234'},
        headers={'X-TelegramUserId': telegram_id}
    )

    new_registrar = await registrars.get_by_registrar_id(registrar.registrar_id)

    expected_response = registrars.RegistrarTelegramResponse(
        telegram_id=new_registrar.external_registrar_id
    ).dict()

    expected_registrar = {
        **registrar.to_dict(),
        'updated_at': now,
        'external_system': registrars.types.RegistrarExternalSystem.TELEGRAM,
        'external_registrar_id': telegram_id,
    }

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(expected_response)
    assert new_registrar.to_dict() == expected_registrar


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_signup_wrong_phone(client):
    await registrars.factories.create(phone='1234')
    telegram_id = 'test123'
    response = await client.post(
        '/registrar/v1/auth/signup/',
        json={'phone': '1235'},
        headers={'X-TelegramUserId': telegram_id}
    )

    expected = {
        'code': 'REGISTRAR_AUTHORIZATION_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'phone': '1235'},
        'message': 'Authorization error. Access forbidden.'
    }

    assert response.status_code == 403
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_signup_without_tg_id(client):
    await registrars.factories.create(phone='1234')
    response = await client.post(
        '/registrar/v1/auth/signup/',
        json={'phone': '1234'},
    )

    expected = {
        'code': 'REGISTRAR_WRONG_TELEGRAM_ID',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Wrong telegram id',
    }

    assert response.status_code == 401
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_temporary_token(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc',
    )

    response = await client.post(
        '/registrar/v1/auth/temporary-token/',
        headers={'X-TelegramUserId': registrar.external_registrar_id},
    )

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.temporary_token_max_age).total_seconds()
    )
    payload = {
        'telegram_id': registrar.external_registrar_id,
        'exp': expires,
    }
    expected = {
        'token': base64url_encode(sign_payload(payload, settings.registrar.secret),)
    }

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_temporary_token_wrong_id_error(client):
    telegram_id = generate_id()

    response = await client.post(
        '/registrar/v1/auth/temporary-token/',
        headers={'X-TelegramUserId': telegram_id},
    )

    expected = {
        'code': 'REGISTRAR_WRONG_TELEGRAM_ID',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'telegram_id': telegram_id},
        'message': 'Wrong telegram id',
    }

    assert response.status_code == 401
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_token_obtain_pair(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc',
    )

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.temporary_token_max_age).total_seconds()
    )
    data = {
        'telegram_id': registrar.external_registrar_id,
        'exp': expires,
    }

    temporary_token = base64url_encode(sign_payload(data, settings.registrar.secret))
    response = await client.post(
        '/registrar/v1/auth/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + temporary_token},
    )

    registrar_sessions = await registrars_auth.get_all()

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.access_token_max_age).total_seconds()
    )
    payload = {
        'registrar_id': registrar.registrar_id,
        'exp': expires,
    }

    expected = {
        "token": base64url_encode(sign_payload(payload, settings.registrar.secret)),
        "refresh_token": base64url_encode(registrar_sessions[0].refresh_token),
    }
    expected = convert_to_frontend_response(expected)

    refresh_expires = datetime_utils.get_now() + datetime.timedelta(seconds=settings.registrar.refresh_token_max_age)
    assert response.status_code == 200
    assert response.json() == expected
    assert len(registrar_sessions) == 1
    assert registrar_sessions[0].registrar_id == registrar.registrar_id
    assert registrar_sessions[0].expires_at == refresh_expires


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_token_obtain_pair_expired_error(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc',
    )

    expires = (datetime_utils.get_now_timestamp() - datetime.timedelta(minutes=1).total_seconds())
    data = {
        'telegram_id': registrar.external_registrar_id,
        'exp': expires,
    }

    temporary_token = base64url_encode(sign_payload(data, settings.registrar.secret))
    response = await client.post(
        '/registrar/v1/auth/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + temporary_token},
    )

    expected = {
        'code': 'REGISTRAR_TOKEN_EXPIRED',
        'details': {'occurred_at': '2020-01-02T03:04:05+00:00'},
        'message': 'Registrar token has been expired',
    }
    assert response.status_code == 401
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_token_obtain_pair_signature_error(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc',
    )

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.temporary_token_max_age).total_seconds()
    )
    data = {
        'telegram_id': registrar.external_registrar_id,
        'exp': expires,
    }

    temporary_token = base64url_encode(sign_payload(data, 'wrong_secret'))
    response = await client.post(
        '/registrar/v1/auth/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + temporary_token},
    )

    expected = {
        'code': 'INVALID_REGISTRAR_TOKEN',
        'details': {'occurred_at': '2020-01-02T03:04:05+00:00', 'content': 'Invalid signature'},
        'message': 'Invalid token signature',
    }
    assert response.status_code == 400
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_token_obtain_pair_already_auth(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc'
    )

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.temporary_token_max_age).total_seconds()
    )
    data = {
        'telegram_id': registrar.external_registrar_id,
        'exp': expires,
    }

    temporary_token = base64url_encode(sign_payload(data, settings.registrar.secret))
    await client.post(
        '/registrar/v1/auth/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + temporary_token},
    )
    response = await client.post(
        '/registrar/v1/auth/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + temporary_token},
    )

    registrar_sessions = sorted(await registrars_auth.get_all(), key=lambda el: el.expires_at)
    refresh_expires = datetime_utils.get_now() + datetime.timedelta(seconds=settings.registrar.refresh_token_max_age)

    assert len(registrar_sessions) == 2
    assert registrar_sessions[0].registrar_id == registrar.registrar_id
    assert registrar_sessions[0].expires_at == datetime_utils.get_now()
    assert registrar_sessions[1].registrar_id == registrar.registrar_id
    assert registrar_sessions[1].expires_at == refresh_expires

    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(seconds=settings.registrar.access_token_max_age).total_seconds()
    )
    payload = {
        'registrar_id': registrar.registrar_id,
        'exp': expires,
    }

    expected = {
        "token": base64url_encode(sign_payload(payload, settings.registrar.secret)),
        "refresh_token": base64url_encode(registrar_sessions[1].refresh_token),
    }
    expected = convert_to_frontend_response(expected)

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_refresh_token(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc'
    )
    expires = (
        datetime_utils.get_now() +
        datetime.timedelta(seconds=settings.registrar.refresh_token_max_age)
    )
    registar_session = await registrars_auth.factories.create(
        registrar_id=registrar.registrar_id,
        fingerprint='1234',
        expires_at=expires,
        created_at=datetime_utils.get_now(),
    )
    refresh_token = base64url_encode(registar_session.refresh_token)
    response = await client.post(
        '/registrar/v1/auth/refresh-token/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + refresh_token},
    )

    registar_session = await registrars_auth.get_active_sessions_by_registrar_id(registrar.registrar_id)
    expires = (
        datetime_utils.get_now_timestamp() +
        datetime.timedelta(
            seconds=settings.registrar.access_token_max_age).total_seconds()
    )
    payload = {
        'registrar_id': registrar.registrar_id,
        'exp': expires,
    }

    expected = {
        "token": base64url_encode(sign_payload(payload, settings.registrar.secret)),
        "refresh_token": base64url_encode(registar_session[0].refresh_token),
    }

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(expected)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_refresh_token_expired_error(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc'
    )
    expires = datetime_utils.get_now() - datetime.timedelta(minutes=1)
    registar_session = await registrars_auth.factories.create(
        registrar_id=registrar.registrar_id,
        fingerprint='1234',
        expires_at=expires,
        created_at=datetime_utils.get_now(),
    )
    refresh_token = base64url_encode(registar_session.refresh_token)
    response = await client.post(
        '/registrar/v1/auth/refresh-token/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + refresh_token},
    )

    expected = {
        'code': 'REGISTRAR_SESSION_EXPIRED',
        'details': {'occurred_at': '2020-01-02T03:04:05+00:00'},
        'message': 'Registrar session has been expired',
    }

    assert response.status_code == 401
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_refresh_token_multiple_session_error(client):
    registrar = await registrars.factories.create(
        external_system=registrars.types.RegistrarExternalSystem.TELEGRAM,
        external_registrar_id='1234abc'
    )
    expires = (
        datetime_utils.get_now() +
        datetime.timedelta(seconds=settings.registrar.refresh_token_max_age)
    )
    registar_session = await registrars_auth.factories.create(
        registrar_id=registrar.registrar_id,
        fingerprint='1234',
        expires_at=expires,
        created_at=datetime_utils.get_now(),
    )
    refresh_token = base64url_encode(registar_session.refresh_token)
    response = await client.post(
        '/registrar/v1/auth/refresh-token/',
        headers={'X-Fingerprint': '1235', 'Authorization': 'Bearer ' + refresh_token},
    )

    expected = {
        'code': 'REGISTRAR_MULTIPLE_SESSION_ERROR',
        'details': {'occurred_at': '2020-01-02T03:04:05+00:00'},
        'message': "Registrar mustn't has few session",
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
@pytest.mark.asyncio
async def test_refresh_token_not_found_error(client):
    refresh_token = base64url_encode(generate_url_token())
    response = await client.post(
        '/registrar/v1/auth/refresh-token/',
        headers={'X-Fingerprint': '1234', 'Authorization': 'Bearer ' + refresh_token},
    )

    expected = {
        'code': 'REGISTRAR_REFRESH_TOKEN_NOT_FOUND',
        'details': {'occurred_at': '2020-01-02T03:04:05+00:00', 'refresh_token': refresh_token},
        'message': 'Registrar refresh token not found',
    }

    assert response.status_code == 401
    assert response.json() == expected
