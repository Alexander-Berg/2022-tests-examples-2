# pylint: disable=protected-access

import pytest
from stall.client.eda_core import client, EdaCoreError

from libstall.model import coerces
from scripts.couriers_profile_updates import CouriersProfileUpdatesDaemon


@pytest.mark.parametrize('gender', ['male', 'female', None])
@pytest.mark.parametrize('birthday', ['2020-01-01', None])
async def test_common(
    tap, ext_api, dataset, uuid, gender, birthday,
):
    with tap.plan(6, 'штатная работа скрипта'):
        eda_id = uuid()

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'cursor': '1',
                'profiles': [{
                    'id': eda_id,
                    'gender': gender,
                    'birthday': birthday,
                }]
            }

        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.eq(cursor, '1', 'new cursor')

        with await courier.reload():
            tap.eq(courier.gender, gender, 'gender ok')
            tap.eq(courier.birthday, coerces.date(birthday), 'birthday ok')


@pytest.mark.parametrize('is_storekeeper', [True, False, None])
async def test_is_storekeeper(
        tap, ext_api, dataset, uuid, is_storekeeper
):
    with tap.plan(4, 'штатная работа скрипта'):
        eda_id = uuid()

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'cursor': '1',
                'profiles': [{
                    'id': eda_id,
                    'is_storekeeper': is_storekeeper,
                }]
            }

        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.ok(courier.is_storekeeper is None, 'initial none')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.eq(cursor, '1', 'new cursor')

        with await courier.reload():
            tap.is_ok(courier.is_storekeeper, is_storekeeper,
                      'is_storekeeper ok')


@pytest.mark.parametrize('is_rover', [True, False, None])
async def test_is_rover(
        tap, ext_api, dataset, uuid, is_rover
):
    with tap.plan(4, 'штатная работа скрипта'):
        eda_id = uuid()

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'cursor': '1',
                'profiles': [{
                    'id': eda_id,
                    'is_rover': is_rover,
                }]
            }

        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.ok(courier.is_rover is None, 'initial none')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.eq(cursor, '1', 'new cursor')

        with await courier.reload():
            tap.is_ok(courier.is_rover, is_rover, 'is_rover ok')


async def test_many(tap, ext_api, dataset, uuid):
    eda_id1 = uuid()
    eda_id2 = uuid()

    # pylint: disable=unused-argument
    async def handle(request):
        return {
            'cursor': '4',
            'profiles': [{
                'id': eda_id1,
                'gender': 'male',
                'birthday': '2020-01-01',
            }, {
                'id': eda_id2,
                'gender': 'female',
                'birthday': '2017-04-01',
            }, {
                'id': uuid(),
                'gender': 'female',
                'birthday': '2011-02-01',
            }]
        }

    with tap.plan(11, 'штатная работа скрипта для множества курьеров'):
        courier1 = await dataset.courier(
            vars={'external_ids': {'eats': eda_id1}}
        )
        courier2 = await dataset.courier(
            vars={'external_ids': {'eats': eda_id2}}
        )
        for eda_id, courier in [(eda_id1, courier1), (eda_id2, courier2)]:
            tap.eq(courier.eda_id, eda_id, 'eda_id ok')
            tap.is_ok(courier.gender, None, 'gender empty')
            tap.is_ok(courier.birthday, None, 'birthday empty')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.eq(cursor, '4', 'new cursor')

        with await courier1.reload() as courier:
            tap.eq(courier.gender, 'male', 'gender ok')
            tap.eq(courier.birthday, coerces.date('2020-01-01'), 'birthday ok')

        with await courier2.reload() as courier:
            tap.eq(courier.gender, 'female', 'gender ok')
            tap.eq(courier.birthday, coerces.date('2017-04-01'), 'birthday ok')


async def test_empty_profiles(tap, ext_api, dataset, uuid):
    eda_id = uuid()

    # pylint: disable=unused-argument
    async def handle(request):
        return {
            'cursor': '1',
            'profiles': []
        }

    with tap.plan(6, 'клиент не отдал профили'):
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.is_ok(cursor, None, 'cursor None')

        with await courier.reload() as courier:
            tap.is_ok(courier.gender, None, 'gender ok')
            tap.is_ok(courier.birthday, None, 'birthday ok')


async def test_unknown_profile(tap, ext_api, dataset, uuid):
    eda_id = uuid()

    # pylint: disable=unused-argument
    async def handle(request):
        return {
            'cursor': '1',
            'profiles': [{
                'id': uuid(),
                'gender': 'female',
                'birthday': '2020-02-02',
            }]
        }

    with tap.plan(6, 'клиент не отдал нужный профиль'):
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        async with await ext_api('eda_core', handle):
            cursor = await CouriersProfileUpdatesDaemon()._process()
            tap.eq(cursor, '1', 'cursor ok')

        with await courier.reload() as courier:
            tap.is_ok(courier.gender, None, 'gender ok')
            tap.is_ok(courier.birthday, None, 'birthday ok')


async def test_eda_core_error(tap, monkeypatch, dataset, uuid):
    eda_id = uuid()

    # pylint: disable=unused-argument
    async def raiser(self, *args, **kwargs):
        raise EdaCoreError

    monkeypatch.setattr(client, client.profiles_updates.__name__, raiser)

    with tap.plan(6, 'клиент получил известную ошибку'):
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        cursor = await CouriersProfileUpdatesDaemon()._process()
        tap.is_ok(cursor, None, 'cursor None')

        with await courier.reload() as courier:
            tap.is_ok(courier.gender, None, 'gender ok')
            tap.is_ok(courier.birthday, None, 'birthday ok')


async def test_exception_error(tap, monkeypatch, dataset, uuid):
    eda_id = uuid()

    class CustomException(Exception):
        pass

    # pylint: disable=unused-argument
    async def raiser(self, *args, **kwargs):
        raise CustomException

    monkeypatch.setattr(client, client.profiles_updates.__name__, raiser)

    with tap.plan(6, 'клиент получил неизвестную ошибку'):
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        with tap.raises(CustomException):
            await CouriersProfileUpdatesDaemon()._process()

        with await courier.reload() as courier:
            tap.is_ok(courier.gender, None, 'gender ok')
            tap.is_ok(courier.birthday, None, 'birthday ok')


async def test_business_error(tap, ext_api, monkeypatch, dataset, uuid):
    eda_id = uuid()

    # pylint: disable=unused-argument
    async def handle(request):
        return {
            'cursor': '1',
            'profiles': [{
                'id': eda_id,
                'gender': 'female',
                'birthday': '2020-02-02',
            }]
        }

    daemon = CouriersProfileUpdatesDaemon()

    class CustomException(Exception):
        pass

    # pylint: disable=unused-argument
    async def raiser(self, *args, **kwargs):
        raise CustomException

    monkeypatch.setattr(daemon, daemon._business.__name__, raiser)

    with tap.plan(6, 'клиент отработал, но упал _business'):
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}}
        )
        tap.eq(courier.eda_id, eda_id, 'eda_id ok')
        tap.is_ok(courier.gender, None, 'gender empty')
        tap.is_ok(courier.birthday, None, 'birthday empty')

        async with await ext_api('eda_core', handle):
            with tap.raises(CustomException):
                await daemon._process()

        with await courier.reload() as courier:
            tap.is_ok(courier.gender, None, 'gender ok')
            tap.is_ok(courier.birthday, None, 'birthday ok')
