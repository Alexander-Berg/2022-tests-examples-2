import dataclasses
from typing import List

import psycopg2
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_payouts_events_plugins import *  # noqa: F403 F401


@dataclasses.dataclass
class CoreSalaryAdjustment:
    id_: int = 1
    courier_id: int = 1
    reason: str = 'because'
    amount: float = 10
    comment: str = 'comment'
    date: str = '2001-04-01'
    related_id: int = 123
    order_nr: str = 'order_nr'


@dataclasses.dataclass
class CoreSalaryAdjustmentsContext:
    cursor: str = ''
    adjustments: List[CoreSalaryAdjustment] = dataclasses.field(
        default_factory=list,
    )

    def add_adjustments(self, cursor, adjustments):
        self.cursor = cursor
        self.adjustments = adjustments


@pytest.fixture(name='core_salary_adjustments')
def _core_salary_adjustments(mockserver):
    context = CoreSalaryAdjustmentsContext()

    def mock_core_salary_adjustments(request, context):
        if (
                'cursor' in request.query
                and request.query['cursor'] == context.cursor
        ):
            return {
                'cursor': 'another_cursor',
                'collection': [],
                'profiles': [],
            }

        return {'cursor': context.cursor, 'collection': context.adjustments}

    @mockserver.json_handler(
        '/eats-core-integration/internal-api/'
        'v1/courier-salary-adjustments/updates',
    )
    def _core_integration_update_handler(request):
        return mock_core_salary_adjustments(request, context)

    return context


@pytest.fixture(name='upsert_pulse')
def upsert_pulse(pgsql):
    def _upsert_pulse(pulse_name, pulse_value):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT
            INTO eats_payouts_events.pulses (key, value)
            VALUES ('{pulse_name}', '{pulse_value}'::TIMESTAMPTZ)
            ON CONFLICT (key)
            DO
                UPDATE
                SET value = EXCLUDED.value;
            """,
        )

    return _upsert_pulse


@pytest.fixture(name='check_last_pulse')
def check_last_pulse(pgsql):
    def _check_last_pulse(key, value):
        cursor = pgsql['eats_payouts_events'].cursor(
            cursor_factory=psycopg2.extras.DictCursor,
        )
        cursor.execute(
            f"""
            SELECT value::TEXT AS value FROM eats_payouts_events.pulses
            WHERE key = '{key}'
            ORDER BY updated_at DESC
            LIMIT 1;
            """,
        )
        last_pulse = cursor.fetchone()

        assert last_pulse
        assert last_pulse['value'] == value

    return _check_last_pulse


@pytest.fixture(name='insert_courier_services')
def insert_courier_services(pgsql):
    def _insert_courier_services(
            service_id=1,
            revision=1,
            name='Test',
            commission=0.0,
            marketing_commission=0.0,
            is_self_employed=False,
            is_self_employed_non_resident=False,
            is_courier_service=False,
    ):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payouts_events.courier_services
              (id, revision, name, commission, marketing_commission,
               is_self_employed, is_self_employed_non_resident,
               is_courier_service)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                service_id,
                revision,
                name,
                commission,
                marketing_commission,
                is_self_employed,
                is_self_employed_non_resident,
                is_courier_service,
            ),
        )

    return _insert_courier_services


@pytest.fixture(name='insert_courier_profile')
def insert_courier_profile(pgsql):
    def _insert_courier_profile(
            courier_profile_id='1',
            revision=1,
            courier_service_id=1,
            courier_service_revision=1,
            eats_region_id='eats_region_id',
            country_id='8',
            transport_type='pedestrian',
            pool='swimming',
            started_work_at='2001-04-01T10:00:00+03:00',
            username='username',
            billing_type='courier_service',
            is_picker=False,
            is_courier_plus=False,
            is_dedicated_picker=False,
            is_rover=False,
            is_storekeeper=False,
            is_ultima=False,
    ):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payouts_events.courier_profiles
              (id, revision, courier_service_id, courier_service_revision,
              eats_region_id, country_id, transport_type, pool,
              started_work_at, username, billing_type, is_picker,
              is_courier_plus, is_dedicated_picker, is_rover, is_storekeeper,
              is_ultima)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s);
            """,
            (
                courier_profile_id,
                revision,
                courier_service_id,
                courier_service_revision,
                eats_region_id,
                country_id,
                transport_type,
                pool,
                started_work_at,
                username,
                billing_type,
                is_picker,
                is_courier_plus,
                is_dedicated_picker,
                is_rover,
                is_storekeeper,
                is_ultima,
            ),
        )

    return _insert_courier_profile


@pytest.fixture(name='insert_fraud_event')
def insert_fraud_event(pgsql):
    def _insert_fraud_event(
            driver_uuid='1',
            event_type='fake_gps_protector',
            event_time='2022-07-30T14:00:01+03:00',
    ):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT
            INTO eats_payouts_events.shift_fraud_event_cache (
                driver_uuid, event_type, event_time
            )
            VALUES (
                '{driver_uuid}',
                '{event_type}',
                '{event_time}'::TIMESTAMPTZ
            );
            """,
        )

    return _insert_fraud_event


@pytest.fixture(name='insert_driver_profile')
def insert_driver_profile(pgsql):
    def _insert_driver_profile(driver_id='1_1', courier_profile_id='1'):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payouts_events.driver_profiles (
                id, courier_profile_id
            )
            VALUES (
                '{driver_id}',
                '{courier_profile_id}'
            );
            """,
        )

    return _insert_driver_profile


@pytest.fixture(name='insert_shift')
def insert_shift(pgsql):
    def _insert_shift(
            shift_id='1',
            courier_profile_id='1',
            courier_profile_revision=1,
            driver_profile_id='1_1',
            travel_type='bicycle',
            eats_region_id=3,
            type_='planned',
            status='in_progress',
            post='courier',
            service='eda',
            planned_start_at='2022-07-30T14:00:00+03:00',
            actual_start_at='2022-07-30T14:00:00+03:00',
            planned_end_at='2022-07-30T18:00:00+03:00',
            actual_end_at=None,
            duration=None,
            offline_time=None,
            guarantee=None,
            pause_duration=None,
            is_newbie=None,
            fraud_on_start=None,
    ):
        cursor = pgsql['eats_payouts_events'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_payouts_events.shifts
              (id, courier_profile_id, courier_profile_revision,
               driver_profile_id, travel_type, eats_region_id, type, status,
               post, service, planned_start_at, actual_start_at,
               planned_end_at, actual_end_at, duration, offline_time,
               guarantee, pause_duration, is_newbie, fraud_on_start)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s);
            """,
            (
                shift_id,
                courier_profile_id,
                courier_profile_revision,
                driver_profile_id,
                travel_type,
                eats_region_id,
                type_,
                status,
                post,
                service,
                planned_start_at,
                actual_start_at,
                planned_end_at,
                actual_end_at,
                duration,
                offline_time,
                guarantee,
                pause_duration,
                is_newbie,
                fraud_on_start,
            ),
        )

    return _insert_shift


@pytest.fixture(name='check_last_cursor')
def check_last_cursor(pgsql):
    def _check_last_cursor(key, value):
        cursor = pgsql['eats_payouts_events'].cursor(
            cursor_factory=psycopg2.extras.DictCursor,
        )
        cursor.execute(
            f"""
            SELECT value FROM eats_payouts_events.cursors
            WHERE key = '{key}'
            ORDER BY updated_at DESC
            LIMIT 1;
            """,
        )
        last_cursor = cursor.fetchone()

        assert last_cursor
        assert last_cursor['value'] == value

    return _check_last_cursor


# courier profiles:
PROFILES_PROFILE_1_JSON = {
    'id': '1',
    'region_id': '1',
    'country_id': '35',
    'travel_type': 'pedestrian',
    'orders_provider': 'some_provider',
    'started_work_at': '2001-04-01T10:00:00+03:00',
    'first_name': 'first_name',
    'surname': 'surname',
    'patronymic': 'patronymic',
    'billing_type': 'courier_service',
    'is_picker': False,
    'is_dedicated_picker': False,
    'is_rover': False,
    'is_storekeeper': False,
    'full_name': 'first_name surname',
    'courier_service_id': '1',
    'transport_type': 'pedestrian',
    'phone_pd_id': 'phone_pd_id',
    'cursor': 'abc_1',
    'is_fixed_shifts_option_enabled': False,
    'is_dedicated_courier': False,
    'is_hard_of_hearing': False,
    'has_health_card': False,
    'has_own_bicycle': False,
    'has_terminal_for_payment_on_site': False,
    'work_status': 'active',
}

PROFILES_PROFILE_2_JSON = {
    'id': '2',
    'region_id': '1',
    'country_id': '35',
    'travel_type': 'pedestrian',
    'orders_provider': 'lavka',
    'started_work_at': '2001-04-01T10:00:00+03:00',
    'first_name': 'Kurier',
    'surname': 'Lavochnikov',
    'patronymic': 'Kurierovich',
    'billing_type': 'courier_service',
    'is_picker': False,
    'is_dedicated_picker': False,
    'is_rover': False,
    'is_storekeeper': False,
    'full_name': 'Kurier Lavochnikov',
    'courier_service_id': '1',
    'transport_type': 'pedestrian',
    'phone_pd_id': 'phone_pd_id',
    'cursor': 'abc_1',
    'is_fixed_shifts_option_enabled': False,
    'is_dedicated_courier': False,
    'is_hard_of_hearing': False,
    'has_health_card': False,
    'has_own_bicycle': False,
    'has_terminal_for_payment_on_site': False,
    'work_status': 'active',
}

PROFILES_PROFILE_3_JSON = {
    'id': '3',
    'region_id': '1',
    'country_id': '35',
    'travel_type': 'pedestrian',
    'orders_provider': 'some_provider',
    'started_work_at': '2001-04-01T10:00:00+03:00',
    'first_name': 'Kurier',
    'surname': 'Beztaxishnich',
    'patronymic': 'Kurierovich',
    'billing_type': 'courier_service',
    'is_picker': False,
    'is_dedicated_picker': False,
    'is_rover': False,
    'is_storekeeper': False,
    'full_name': 'Kurier Beztaxishnich',
    'courier_service_id': '1',
    'transport_type': 'pedestrian',
    'phone_pd_id': 'phone_pd_id',
    'cursor': 'abc_1',
    'is_fixed_shifts_option_enabled': False,
    'is_dedicated_courier': False,
    'is_hard_of_hearing': False,
    'has_health_card': False,
    'has_own_bicycle': False,
    'has_terminal_for_payment_on_site': False,
    'work_status': 'active',
}

DRIVER_PROFILES_PROJECTION_JSON = [
    'data.orders_provider.eda',
    'data.orders_provider.retail',
    'data.park_id',
    'data.uuid',
]

DRIVER_PROFILES_PROFILE_1_JSON = {
    'eats_courier_id': '1',
    'profiles': [
        {
            'park_driver_profile_id': 'pdp_1',
            'data': {'park_id': 'park_id', 'uuid': 'uuid'},
        },
    ],
}

DRIVER_PROFILES_PROFILE_2_JSON = {
    'eats_courier_id': '1',
    'profiles': [
        {
            'park_driver_profile_id': 'pdp_2',
            'data': {'park_id': 'park_id_2', 'uuid': 'uuid_2'},
        },
    ],
}


@pytest.fixture
def _core_integration_profiles_update(mockserver):
    @mockserver.json_handler(
        '/eats-core-integration/server/api/v1/courier/profiles/update',
    )
    def _handler(request):
        if 'cursor' not in request.query or (
                'cursor' in request.query and request.query['cursor'] == ''
        ):
            return {
                'cursor': 'abc_1',
                'profiles': [
                    PROFILES_PROFILE_1_JSON,
                    PROFILES_PROFILE_2_JSON,
                    PROFILES_PROFILE_3_JSON,
                ],
            }

        return {'cursor': 'abc_2', 'profiles': []}

    return _handler


@pytest.fixture
def _driver_profiles_retrieve_by_eats_id(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    def _handler(request):
        assert request.json['projection'] == DRIVER_PROFILES_PROJECTION_JSON
        eats_ids = request.json.get('eats_courier_id_in_set')
        dp_by_eats_id = []

        assert eats_ids is not None
        for eats_id in eats_ids:
            if eats_id == '1':
                dp_by_eats_id.append(DRIVER_PROFILES_PROFILE_1_JSON)
            elif eats_id == '2':
                dp_by_eats_id.append(DRIVER_PROFILES_PROFILE_2_JSON)
            else:
                dp_profile_empty_json = {
                    'eats_courier_id': eats_id,
                    'profiles': [],
                }
                dp_by_eats_id.append(dp_profile_empty_json)

        return {'courier_by_eats_id': dp_by_eats_id}

    return _handler
