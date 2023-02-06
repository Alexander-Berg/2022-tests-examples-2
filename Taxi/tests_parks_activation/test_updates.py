import pytest


# TODO uncomment logistics after
#  https://st.yandex-team.ru/CARGODEV-8360#61bb2328ee8b8d148c4413ee
async def test_updates_empty_params(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 3,
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': True,
                    'can_corp_without_vat': True,
                    'can_logistic': False,
                    'can_subsidy': True,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }


async def test_updates_limit(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'limit': 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 1,
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }


async def test_updates_revision(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 3,
        'parks_activation': [
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': True,
                    'can_corp_without_vat': True,
                    'can_logistic': False,
                    'can_subsidy': True,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }


async def test_updates_empty(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 999},
    )
    assert response.status_code == 200
    assert response.json() == {'last_revision': 999, 'parks_activation': []}


async def test_updates_limit_revision(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates',
        json={'limit': 1, 'last_known_revision': 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 2,
        'parks_activation': [
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }

    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates',
        json={'limit': 1, 'last_known_revision': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 3,
        'parks_activation': [
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': True,
                    'can_corp_without_vat': True,
                    'can_logistic': False,
                    'can_subsidy': True,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }


async def test_updates_additional_revisions(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates',
        json={'last_known_revision': 2, 'additional_revisions': [1]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 3,
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': True,
                    'can_corp_without_vat': True,
                    'can_logistic': False,
                    'can_subsidy': True,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates',
        json={'last_known_revision': 2, 'additional_revisions': [1, 2]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 3,
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'has_corp_without_vat_contract': True,
                    'can_corp_without_vat': True,
                    'can_logistic': False,
                    'can_subsidy': True,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }


@pytest.mark.config(
    PARKS_ACTIVATION_UPDATES_HANDLER={
        'max_answer_count': 1,
        'get_park_updates_db_timeout_ms': 250,
    },
    PARKS_ACTIVATION_HISTORY_HANDLER={
        'max_answer_count': 1000,
        'get_park_history_db_timeout_ms': 250,
    },
)
async def test_updates_limit_config(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_revision': 1,
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'has_corp_without_vat_contract': False,
                    'can_corp_without_vat': False,
                    'can_logistic': False,
                    'can_subsidy': False,
                    # 'logistic_deactivated': False,
                    # 'logistic_can_cash': False,
                    # 'logistic_can_card': False,
                },
            },
        ],
    }
