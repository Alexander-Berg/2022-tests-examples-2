# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime

import pytest

from generated.models import api7

import fleet_plugins_tests.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from fleet_plugins_tests.generated.web.fleet_common import entities
from fleet_plugins_tests.generated.web.fleet_common import enums
from fleet_plugins_tests.generated.web.fleet_common.utils import exceptions

pytest_plugins = ['fleet_plugins_tests.generated.service.pytest_plugins']


@pytest.fixture
def mock_auth(patch, add_grants, fleet_user):
    add_grants()

    @patch('fleet_plugins_tests.generated.web.fleet_common.services.auth.run')
    async def _auth(*args, **kwargs):
        return fleet_user

    return fleet_user


@pytest.fixture
def add_grants(patch):
    def mock_grants(*grants: enums.Grant):
        @patch(
            'fleet_plugins_tests.generated.web.fleet_common.services.grants.check_grant',  # noqa E501
        )
        async def _check_grant(context, fleet_user, grant, log_extra):
            if grant not in grants:
                raise exceptions.NoGrants()

    return mock_grants


@pytest.fixture
def fleet_user() -> entities.FleetUser:
    return entities.FleetUser(
        park=entities.Park.make_from_api7(
            api7_park=api7.ParkInfo(
                id='7ad36bc7560449998acbe2c57a75c293',
                name='Лещ',
                clid='111111',
                city='Москва',
                currency_id='RUB',
                locale='ru',
                timezone=3,
                created_date=datetime.datetime(2018, 5, 18, 0, 0),
                self_employed=False,
                ui_mode='default',
                country_id='rus',
            ),
        ),
        passport_user=entities.PassportUser(uid='42', login='vasya'),
        api7_parks=[
            api7.ParkInfo(
                id='7ad36bc7560449998acbe2c57a75c293',
                name='Лещ',
                timezone=3,
                clid='111111',
                city='Москва',
                city_eng='Moscow',
                country_id='rus',
                country_name='Россия',
                currency_id='RUB',
                locale='ru',
            ),
            api7.ParkInfo(
                id='8adbd417a90f48f09597981cd13ac043',
                name='Korp test Erevan',
                timezone=4,
                clid='222222',
                city='Ереван',
                city_eng='Erevan',
                country_id='arm',
                country_name='Армения',
                currency_id='RUB',
                locale='ru',
            ),
        ],
        api7_user=api7.User(
            id='dc7e031f6dd94512989d8c17dc6f2163',
            park_id='7ad36bc7560449998acbe2c57a75c293',
            display_name='vasya',
            passport_uid='',
            email='vasya@yandex.ru',
            phone='',
            group_id='9330ae2ecbc646bab446b936b3048d11',
            group_name='Администратор',
            is_enabled=True,
            is_confirmed=True,
            is_superuser=True,
            is_usage_consent_accepted=True,
            usage_consent_acceptance_date='',
            yandex_uid='',
        ),
        user_ticket='user_ticket',
        real_ip='127.0.0.1',
        ticket_provider='yandex',
        support_mode=False,
        is_uber_domain=False,
        chatterbox_ticket_id=None,
    )


@pytest.fixture
def support_fleet_user() -> entities.FleetUser:
    return entities.FleetUser(
        park=entities.Park.make_from_api7(
            api7_park=api7.ParkInfo(
                id='7ad36bc7560449998acbe2c57a75c293',
                name='Лещ',
                clid='111111',
                city='Москва',
                currency_id='RUB',
                locale='ru',
                timezone=3,
                created_date=datetime.datetime(2018, 5, 18, 0, 0),
                self_employed=False,
                ui_mode='default',
                country_id='rus',
            ),
        ),
        passport_user=entities.PassportUser(uid='42', login='vasya'),
        api7_parks=[
            api7.ParkInfo(
                id='7ad36bc7560449998acbe2c57a75c293',
                name='Лещ',
                timezone=3,
                clid='111111',
                city='Москва',
                city_eng='Moscow',
                country_id='rus',
                country_name='Россия',
                currency_id='RUB',
                locale='ru',
            ),
        ],
        api7_user=None,
        user_ticket='user_ticket',
        real_ip='127.0.0.1',
        ticket_provider='yandex',
        support_mode=True,
        is_uber_domain=False,
        chatterbox_ticket_id=None,
    )
