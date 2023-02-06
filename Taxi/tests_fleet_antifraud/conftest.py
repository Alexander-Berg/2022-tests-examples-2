import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fleet_antifraud_plugins import *  # noqa: F403 F401

from tests_fleet_antifraud import mock_api_impl
from tests_fleet_antifraud import utils


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_retrieve(request):
        def make_not_found(park_driver_profile_id):
            return {
                'revision': '0_1234567_0',
                'park_driver_id': park_driver_profile_id,
                'park_driver_profile_id': park_driver_profile_id,
            }

        profiles = {
            profile['park_driver_profile_id']: profile
            for profile in load_json('driver_profiles.json')
        }
        ids = request.json['id_in_set']
        return {
            'profiles': [profiles.get(id, make_not_found(id)) for id in ids],
        }


@pytest.fixture
def pg_dump(pgsql):
    def execute():
        with pgsql['fleet_antifraud'].cursor() as cursor:
            return utils.pg_dump_all(cursor)

    return execute


@pytest.fixture
def mock_api(load_json, mockserver):
    return mock_api_impl.setup(load_json, mockserver)


@pytest.fixture
def fleet_v1(taxi_fleet_antifraud):
    class FleetV1:
        async def change_park_check_settings(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.put(
                '/fleet/antifraud/v1/park-check/settings',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def get_park_check_settings(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
        ):
            return await taxi_fleet_antifraud.get(
                '/fleet/antifraud/v1/park-check/settings',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def retrieve_suspicious(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.post(
                '/fleet/antifraud/v1/park-check/suspicious/retrieve',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def approve_suspicious_orders(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.post(
                '/fleet/antifraud/v1/park-check/suspicious/approve',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def get_blocked_balance(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                contractor_id,
        ):
            return await taxi_fleet_antifraud.get(
                '/fleet/antifraud/v1/park-check/blocked-balance',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                params={'contractor_id': contractor_id},
            )

        async def get_park_check_blocked_balance(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                contractor_id,
                do_update,
        ):
            return await taxi_fleet_antifraud.get(
                '/v1/park-check/blocked-balance',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                },
                params={
                    'park_id': park_id,
                    'contractor_id': contractor_id,
                    'do_update': do_update,
                },
            )

        async def ip_change_park_check_settings(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.put(
                '/fleet/instant-payouts/v2/park-check/settings',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def ip_get_park_check_settings(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
        ):
            return await taxi_fleet_antifraud.get(
                '/fleet/instant-payouts/v2/park-check/settings',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def ip_retrieve_suspicious(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.post(
                '/fleet/instant-payouts/v2/park-check/suspicious/retrieve',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def ip_approve_suspicious_orders(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_fleet_antifraud.post(
                '/fleet/instant-payouts/v2/park-check/suspicious/approve',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def ip_get_blocked_balance(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                contractor_id,
        ):
            return await taxi_fleet_antifraud.get(
                '/fleet/instant-payouts/v2/park-check/blocked-balance',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                params={'contractor_id': contractor_id},
            )

    return FleetV1()
