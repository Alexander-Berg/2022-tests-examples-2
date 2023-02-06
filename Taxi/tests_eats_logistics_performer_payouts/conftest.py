import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_logistics_performer_payouts_plugins import *  # noqa: F403 F401

# pylint: disable=import-error
from eats_catalog_storage_cache import eats_catalog_storage_cache  # noqa F401


# New 'pytest.mark' option
def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture of service cache',
    )


# courier services:
@pytest.fixture
def local_service(mockserver):
    @mockserver.json_handler(
        '/eats-core-integration/internal-api/v1/courier-service/updates',
    )
    def _core_integration_update_handler(request):

        if request.query['cursor'] == 'abc_1':
            return {'cursor': 'abc_2', 'collection': []}

        return {
            'cursor': 'abc_1',
            'collection': [
                {
                    'id': 1,
                    'name': 'someName',
                    'commissions': {
                        'commission': '1.3',
                        'marketing_commission': '2.6',
                    },
                    'available_billing_types': [
                        'courier_service',
                        'self_employed',
                    ],
                },
            ],
        }

    @mockserver.json_handler('/eats-logistics-performer-payouts/v1/subjects')
    def _payouts_subjects_handler(request):
        assert request.json == {
            'id': {'id': '1', 'type': 'courier_service'},
            'factors': [
                {'name': 'name', 'type': 'string', 'value': 'someName'},
                {'name': 'commission', 'type': 'decimal', 'value': '1.3'},
                {
                    'name': 'marketing_commission',
                    'type': 'decimal',
                    'value': '2.6',
                },
                {'name': 'is_self_employed', 'type': 'int', 'value': 1},
                {
                    'name': 'is_self_employed_non_resident',
                    'type': 'int',
                    'value': 0,
                },
                {'name': 'is_courier_service', 'type': 'int', 'value': 1},
            ],
        }
        return {}


@pytest.fixture
def local_service_with_double_call(mockserver):
    @mockserver.json_handler(
        '/eats-core-integration/internal-api/v1/courier-service/updates',
    )
    def _core_integration_update_handler(request):

        response = None

        if request.query['cursor'] == 'abc_1':
            response = {
                'cursor': 'abc_2',
                'collection': [
                    {
                        'id': 1,
                        'name': 'someName',
                        'commissions': {
                            'commission': '1.3',
                            'marketing_commission': '2.6',
                        },
                        'available_billing_types': [
                            'courier_service',
                            'self_employed',
                            'self_employed_nonresident',
                        ],
                    },
                ],
            }
        elif request.query['cursor'] == 'abc_2':
            response = {'cursor': 'abc_3', 'collection': []}
        else:
            response = {
                'cursor': 'abc_1',
                'collection': [
                    {
                        'id': 1,
                        'name': 'someName',
                        'commissions': {
                            'commission': '1.3',
                            'marketing_commission': '2.6',
                        },
                        'available_billing_types': [
                            'courier_service',
                            'self_employed',
                            'self_employed_nonresident',
                        ],
                    },
                ],
            }

        return response

    @mockserver.json_handler('/eats-logistics-performer-payouts/v1/subjects')
    def _payouts_subjects_handler(request):
        assert request.json == {
            'id': {'id': '1', 'type': 'courier_service'},
            'factors': [
                {'name': 'name', 'type': 'string', 'value': 'someName'},
                {'name': 'commission', 'type': 'decimal', 'value': '1.3'},
                {
                    'name': 'marketing_commission',
                    'type': 'decimal',
                    'value': '2.6',
                },
                {'name': 'is_self_employed', 'type': 'int', 'value': 1},
                {
                    'name': 'is_self_employed_non_resident',
                    'type': 'int',
                    'value': 1,
                },
                {'name': 'is_courier_service', 'type': 'int', 'value': 1},
            ],
        }
        return {}


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
    'courier_service_id': '34',
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
    'courier_service_id': '34',
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
    'courier_service_id': '34',
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
        if request.query['cursor'] == 'abc_1':
            return {'cursor': 'abc_2', 'profiles': []}

        return {
            'cursor': 'abc_1',
            'profiles': [
                PROFILES_PROFILE_1_JSON,
                PROFILES_PROFILE_2_JSON,
                PROFILES_PROFILE_3_JSON,
            ],
        }

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


# salary adjustments:


@pytest.fixture
def handlers_for_journal_salary(mockserver):
    @mockserver.json_handler(
        '/eats-core-integration/internal-api/'
        'v1/courier-salary-adjustments/updates',
    )
    def _core_integration_update_handler(request):

        if request.query['cursor'] == 'abc_1':
            return {'cursor': 'abc_2', 'collection': [], 'profiles': []}

        return {
            'cursor': 'abc_1',
            'collection': [
                {
                    'id': 1,
                    'courier_id': 321,
                    'reason': 'because',
                    'amount': 10.1,
                    'comment': 'comment',
                    'date': '2001-04-01',
                    'related_id': 123,
                    'order_nr': 'order_nr',
                },
            ],
        }
