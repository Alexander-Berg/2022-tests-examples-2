import typing
import uuid

import pytest


class ActiveClaims:
    claims: typing.List[dict]
    cache_chunk_size: int

    def __init__(self):
        self.claims = []
        self.cache_chunk_size = 2


@pytest.fixture(name='add_active_claim')
async def _add_active_claim(active_claims):
    def wrapper(claim_id=None, allowed_classes=None):
        if claim_id is None:
            claim_id = uuid.uuid4().hex
        if allowed_classes is None:
            allowed_classes = ['vip']

        active_claims.claims.append(
            {'claim_id': claim_id, 'allowed_classes': allowed_classes},
        )
        return claim_id

    return wrapper


@pytest.fixture(name='mock_active_claims')
async def _mock_active_claims(mockserver, active_claims):
    def _build_cursor(index: int):
        return str(index)

    def _get_index(cursor):
        if cursor:
            return int(cursor)
        return 0

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def mock(*, query):
        response_size_limit = active_claims.cache_chunk_size
        index = _get_index(query.get('cursor'))
        claims = active_claims.claims[index : index + response_size_limit]

        if not claims:
            cursor = None
        else:
            cursor = _build_cursor(index + len(claims))
        return {'claims': claims, 'cursor': cursor}

    return mock


@pytest.fixture(name='active_claims')
async def _active_claims():
    return ActiveClaims()


@pytest.mark.config(
    CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
        'classes_fallback_order': [['econom']],
    },
)
async def test_basic(taxi_candidates, driver_positions):
    """
    In this test and others

    Drivers final_classes:
    * uuid0 => [econom minivan uberx]
    * uuid1 => [uberblack]
    * uuid2 => [uberblack]

    Order allowed_classes:
      express econom business comfortplus vip minivan
      uberx uberselect uberblack uberkids uberselectplus cargo courier
    """
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == {'uuid0'}


@pytest.mark.config(
    CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
        'classes_fallback_order': [['minivan']],
    },
)
async def test_no_filter_for_no_cargo_ref_order(
        taxi_candidates, driver_positions,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == {'uuid0', 'uuid1', 'uuid2'}


@pytest.mark.parametrize(
    'config_classes, result_drivers',
    (
        ([], {'uuid0', 'uuid1', 'uuid2'}),
        ([['rutaxi']], {'uuid0', 'uuid1', 'uuid2'}),
        ([['uberblack']], {'uuid1', 'uuid2'}),
        ([['minivan']], {'uuid0'}),
        ([['minivan', 'econom']], {'uuid0'}),
        ([['rutaxi'], ['minivan', 'uberkids'], ['uberblack']], {'uuid0'}),
        ([['vip']], set()),
    ),
    ids=(
        'no-filter-cause-empty-config-fallback',
        'no-filter-cause-empty-config-fallback-intersection-with-allowed-clss',
        'filter-by-single-class-1',
        'filter-by-single-class-2',
        'filter-by-multi-class',
        'use-first-config-entry-with-nonempty-intersection-with-allowed-clss',
        'disallow-all-drivers-is-ok',
    ),
)
async def test_ok_filter_by_fallback_config(
        taxi_candidates,
        driver_positions,
        taxi_config,
        config_classes,
        result_drivers,
):

    taxi_config.set_values(
        dict(
            CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
                'classes_fallback_order': config_classes,
            },
        ),
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers


@pytest.mark.config(
    CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
        'classes_fallback_order': [['uberblack']],
    },
)
@pytest.mark.parametrize(
    'active_claims_response, result_drivers',
    (
        (
            {
                'claims': [
                    {'claim_id': '123456789', 'allowed_classes': ['minivan']},
                ],
            },
            {'uuid0'},
        ),
        (
            {
                'claims': [
                    {
                        'claim_id': '123456789',
                        'allowed_classes': ['minivan', 'uberx'],
                    },
                ],
            },
            {'uuid0'},
        ),
        (
            {
                'claims': [
                    {
                        'claim_id': '123456789',
                        'allowed_classes': ['uberblack'],
                    },
                ],
            },
            {'uuid1', 'uuid2'},
        ),
        (
            {
                'claims': [
                    {'claim_id': '123456789', 'allowed_classes': ['vip']},
                ],
            },
            set(),
        ),
        (
            {
                'claims': [
                    {'claim_id': 'another', 'allowed_classes': ['vip']},
                    {'claim_id': '123456789', 'allowed_classes': ['minivan']},
                ],
            },
            {'uuid0'},
        ),
        ({'claims': []}, {'uuid1', 'uuid2'}),
        (
            {
                'claims': [
                    {'claim_id': 'another', 'allowed_classes': ['minivan']},
                ],
            },
            {'uuid1', 'uuid2'},
        ),
        ({'claims': [{'claim_id': '123456789'}]}, {'uuid0', 'uuid1', 'uuid2'}),
        (
            {'claims': [{'claim_id': '123456789', 'allowed_classes': []}]},
            {'uuid0', 'uuid1', 'uuid2'},
        ),
        (
            {
                'claims': [
                    {'claim_id': '123456789', 'allowed_classes': ['rutaxi']},
                ],
            },
            {'uuid0', 'uuid1', 'uuid2'},
        ),
    ),
    ids=(
        'ok-filter-by-active-claim-1',
        'ok-filter-by-active-claim-2',
        'ok-filter-by-active-claim-3',
        'ok-filter-by-active-claim-4',
        'ok-filter-by-active-claim-5',
        'use-fallback-config-cause-no-active-claims-in-response',
        'use-fallback-config-cause-another-active-claims-in-response',
        'no-filter-cause-no-active-claim-allowed-classes',
        'no-filter-cause-empty-active-claim-intersection-with-allowed-clss-1',
        'no-filter-cause-empty-active-claim-intersection-with-allowed-clss-2',
    ),
)
async def test_ok_filter_by_active_claims_cache(
        mockserver,
        taxi_candidates,
        driver_positions,
        active_claims_response,
        result_drivers,
):

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _mock_active_claims(request):
        if isinstance(active_claims_response, int):
            return mockserver.make_response(
                json={}, status=active_claims_response,
            )
        return active_claims_response

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers


@pytest.mark.parametrize(
    'config_enabled, result_drivers',
    ((True, {'uuid0'}), (False, {'uuid1', 'uuid2'})),
)
async def test_disable_cache_by_config(
        mockserver,
        taxi_candidates,
        driver_positions,
        taxi_config,
        config_enabled,
        result_drivers,
):

    taxi_config.set_values(
        dict(
            CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
                'classes_fallback_order': [['uberblack']],
            },
            CARGO_CANDIDATES_ACTIVE_CLAIMS_CACHE_SETTINGS={
                'candidates_cache_enabled': config_enabled,
                'cargo_claims_cache_enabled': True,
                'delay_claims_settings': {
                    'not_actual_after_due_sec': 3600,
                    'not_actual_before_due_sec': 1800,
                },
                'soon_claims_settings': {
                    'not_actual_after_last_status_change_sec': 3600,
                },
            },
        ),
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _mock_active_claims(request):

        return {
            'claims': [
                {'claim_id': '123456789', 'allowed_classes': ['minivan']},
            ],
        }

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'order': {'cargo_ref_id': '123456789'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers


@pytest.mark.config(
    CARGO_DELAY_EXPENSIVE_TARIFFS_SETTINGS={
        'classes_fallback_order': [['uberblack']],
    },
)
@pytest.mark.parametrize(
    'active_claims_response, result_drivers',
    (
        (
            {
                'claims': [
                    {'claim_id': 'claim1', 'allowed_classes': ['vip']},
                    {'claim_id': 'claim2', 'allowed_classes': ['vip']},
                ],
            },
            set(),
        ),
        (
            {
                'claims': [
                    {'claim_id': 'claim1', 'allowed_classes': ['minivan']},
                    {'claim_id': 'claim2', 'allowed_classes': ['minivan']},
                ],
            },
            {'uuid0'},
        ),
        (
            {
                'claims': [
                    {
                        'claim_id': 'claim1',
                        'allowed_classes': ['vip', 'minivan'],
                    },
                    {'claim_id': 'claim2', 'allowed_classes': ['vip']},
                ],
            },
            {'uuid0'},
        ),
        (
            {
                'claims': [
                    {'claim_id': 'claim1', 'allowed_classes': ['minivan']},
                ],
            },
            {'uuid1', 'uuid2'},
        ),
    ),
    ids=(
        'ok-filtered-vip',
        'ok-filtered-minivan',
        'ok-filtered-vip-minivan-merge',
        'fallback-claim2-not-in-cache',
    ),
)
async def test_merged(
        mockserver,
        taxi_candidates,
        driver_positions,
        active_claims_response,
        result_drivers,
):

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _mock_active_claims(request):
        if isinstance(active_claims_response, int):
            return mockserver.make_response(
                json={}, status=active_claims_response,
            )
        return active_claims_response

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/delay_expensive_tariffs'],
        'point': [55, 35],
        'order': {'cargo_ref_ids': ['claim1', 'claim2']},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == result_drivers


async def test_fetch_with_cursor(
        taxi_candidates, active_claims, add_active_claim, mock_active_claims,
):
    active_claims.cache_chunk_size = 2
    for _ in range(4):
        add_active_claim()

    mock_active_claims.flush()
    await taxi_candidates.invalidate_caches()

    # returned claims: 2, 2, 0
    assert mock_active_claims.times_called == 3
