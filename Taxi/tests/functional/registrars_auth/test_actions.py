import datetime
import pytest
import freezegun

from taxi.robowarehouse.lib.concepts import registrars_auth
from taxi.robowarehouse.lib.concepts import registrars
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc import datetime_utils


@pytest.mark.asyncio
async def test_get_all():
    refresh_token1 = await registrars_auth.factories.create()
    refresh_token2 = await registrars_auth.factories.create()

    result = await registrars_auth.get_all()

    result = [el.to_dict() for el in result]
    expected = [el.to_dict() for el in (refresh_token1, refresh_token2)]

    result.sort(key=lambda el: el['refresh_token'])
    expected.sort(key=lambda el: el['refresh_token'])

    assert len(result) == 2
    assert_items_equal(result, expected)


@pytest.mark.asyncio
async def test_get_session_by_refresh_token():
    refresh_token1 = await registrars_auth.factories.create()
    await registrars_auth.factories.create()

    result = await registrars_auth.get_session_by_refresh_token(refresh_token1.refresh_token)

    assert result.to_dict() == refresh_token1.to_dict()


@pytest.mark.asyncio
async def test_get_session_by_refresh_token_not_found():
    await registrars_auth.factories.create()
    refresh_token = generate_id()

    with pytest.raises(registrars_auth.exceptions.RegistrarRefreshTokenNotFoundError):
        await registrars_auth.get_session_by_refresh_token(refresh_token)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_active_sessions_by_registrar_id():
    now = datetime_utils.get_now()
    delta_10m = datetime.timedelta(minutes=10)

    registrar = await registrars.factories.create()
    refresh_token1 = await registrars_auth.factories.create(
        expires_at=now + delta_10m,
        registrar_id=registrar.registrar_id,
    )
    refresh_token2 = await registrars_auth.factories.create(
        expires_at=now + delta_10m,
        registrar_id=registrar.registrar_id,
    )
    await registrars_auth.factories.create(registrar_id=registrar.registrar_id)
    await registrars_auth.factories.create()

    result = await registrars_auth.get_active_sessions_by_registrar_id(registrar.registrar_id)

    result = [el.to_dict() for el in result]
    expected = [el.to_dict() for el in (refresh_token1, refresh_token2)]

    result.sort(key=lambda el: el['refresh_token'])
    expected.sort(key=lambda el: el['refresh_token'])

    assert len(result) == 2
    assert_items_equal(result, expected)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_registrar_session():
    registrar = await registrars.factories.create()
    refresh_token1 = await registrars_auth.factories.create()
    refresh_token2 = registrars_auth.factories.build(registrar_id=registrar.registrar_id)

    result = await registrars_auth.create_registrar_session(
        registrars_auth.CreateRegistrarAuthRequests.from_orm(refresh_token2)
    )
    registrars_sessions = await registrars_auth.get_all()
    registrars_sessions = [el.to_dict() for el in registrars_sessions]
    expected = [el.to_dict() for el in (refresh_token1, refresh_token2)]

    registrars_sessions.sort(key=lambda el: el['refresh_token'])
    expected.sort(key=lambda el: el['refresh_token'])

    assert result.to_dict() == refresh_token2.to_dict()
    assert_items_equal(registrars_sessions, expected)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_revoke_refresh_token():
    now = datetime_utils.get_now()
    delta_10m = datetime.timedelta(minutes=10)

    refresh_token1 = await registrars_auth.factories.create(expires_at=now + delta_10m)
    refresh_token2 = await registrars_auth.factories.create(expires_at=now + delta_10m)

    result = await registrars_auth.revoke_refresh_token(refresh_token1.refresh_token)
    registrars_sessions = await registrars_auth.get_all()

    registrars_sessions = [el.to_dict() for el in registrars_sessions]
    expected_token = {**refresh_token1.to_dict(), 'expires_at': now}
    expected = [expected_token, refresh_token2.to_dict()]

    registrars_sessions.sort(key=lambda el: el['refresh_token'])
    expected.sort(key=lambda el: el['refresh_token'])

    assert result.to_dict() == expected_token
    assert len(registrars_sessions) == 2
    assert_items_equal(registrars_sessions, expected)
