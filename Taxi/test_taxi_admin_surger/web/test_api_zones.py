import pytest

from taxi.util import dates

from taxi_admin_surger import zones_common


def sorted_zones(zones):
    def id_key(zone):
        return zone['id']

    return sorted(zones, key=id_key)


async def test_enumerate(web_app_client):
    response = await web_app_client.get('/enumerate_zones/')
    assert response.status == 200
    assert sorted_zones(await response.json()) == sorted_zones(
        [
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'name': 'MSK-airport-SVO',
                'geometry': [
                    [37.42341680849205, 55.94398687417875],
                    [37.37507927380975, 55.9510776995972],
                    [37.35210636343812, 55.9625639533571],
                    [37.42341680849205, 55.94398687417875],
                ],
            },
            {
                'id': '973db8f0605a4da2b8839c575bcad772',
                'name': 'EKB',
                'geometry': [
                    [60.97150402961129, 56.61976548203835],
                    [60.40993449264003, 56.635857397142466],
                    [60.23546136069812, 56.73326908562074],
                    [60.97150402961129, 56.61976548203835],
                ],
            },
        ],
    )


async def test_get(web_app_client, load_json):
    response = await web_app_client.get(
        '/get_zone/', params={'id': '094637bf71bd4675bf9d1103d6598426'},
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    assert (
        response_json['production_experiment_id']
        == '7999b840979b410b9347abc777a01053'
    )
    assert (
        response_json['alternative_experiment_id']
        == '9cedfa150f2544fd8ac04ee4d06381a4'
    )

    expected_fname = 'get_zone_094637bf71bd4675bf9d1103d6598426.json'

    del response_json['updated']

    assert load_json(expected_fname) == response_json

    # Attempt to get non-existent zone results in 404
    response = await web_app_client.get(
        '/get_zone/', params={'id': 'non_existent_zone'},
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'data,code',
    [
        ({}, 400),
        # Baseline 200
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'alternative_experiment_id': (
                    'c1e39cb193054aedab92235ed32914bf'
                ),
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'alternative_experiment_id': '',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                    },
                ],
            },
            200,
        ),
        # production_experiment_id must be one of experiment_id in forced[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': '4466b186e18b44db941db751e004f795',
                    },
                ],
            },
            400,
        ),
        # alternative_experiment_id must be one of experiment_id in forced[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': '4466b186e18b44db941db751e004f795',
                'alternative_experiment_id': (
                    'c1e39cb193054aedab92235ed32914bf'
                ),
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': '4466b186e18b44db941db751e004f795',
                    },
                ],
            },
            400,
        ),
        # surge/alpha/beta must be valid in forced[].rules.surge_rules[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'rules': {
                            'econom': {
                                'surge_rules': [
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.1,
                                    },
                                ],
                                'time_rules': [],
                            },
                        },
                    },
                ],
            },
            200,  # PASS
        ),
        # surge/alpha/beta must be valid in forced[].rules.surge_rules[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'rules': {
                            'econom': {
                                'surge_rules': [
                                    {
                                        'alpha': 0.0,
                                        'beta': 0.0,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.1,
                                    },
                                ],
                                'time_rules': [],
                            },
                        },
                    },
                ],
            },
            400,  # FAIL
        ),
        # surge/alpha/beta must be valid in forced[].balance.table_coef_ps[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'balance': {
                            'add_free': 0,
                            'add_total': 0,
                            'f_delta_left': 0,
                            'f_delta_right': 0,
                            'f_equal': 0,
                            'f_init': 0,
                            'fs_coef_chain': 0,
                            'fs_coef_total': 0,
                            'fs_intercept': 0,
                            'min_pins': 1,
                            'table_coef_ps': [
                                {
                                    'alpha': 0.2,
                                    'beta': 0.8,
                                    'coeff': 0.5,
                                    'ps': 1.0,
                                    'ps_b': 1.0,
                                    'surcharge': 200,
                                },
                            ],
                            'utilization_for_non_econom': False,
                        },
                    },
                ],
            },
            200,  # PASS
        ),
        # surge/alpha/beta must be valid in forced[].balance.table_coef_ps[]
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'balance': {
                            'add_free': 0,
                            'add_total': 0,
                            'f_delta_left': 0,
                            'f_delta_right': 0,
                            'f_equal': 0,
                            'f_init': 0,
                            'fs_coef_chain': 0,
                            'fs_coef_total': 0,
                            'fs_intercept': 0,
                            'min_pins': 1,
                            'table_coef_ps': [
                                {
                                    'alpha': 0.1,
                                    'beta': 0.5,
                                    'coeff': 0.5,
                                    'ps': 1.0,
                                    'surcharge': 200,
                                },
                            ],
                            'utilization_for_non_econom': False,
                        },
                    },
                ],
            },
            400,  # FAIL
        ),
        #
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'local_time_shift': 0,
                'type': 'some_other_type',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'pipeline_name': 'test_pipeline',
                        'rules': {
                            'econom': {
                                'time_rules': [],
                                'surge_rules': [
                                    {
                                        'min_coeff': 0.3,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.3,
                                    },
                                    {
                                        'min_coeff': 0.5,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.2,
                                    },
                                ],
                            },
                            'business': {
                                'time_rules': [],
                                'surge_rules': [
                                    {
                                        'min_coeff': 0.3,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.3,
                                    },
                                    {
                                        'min_coeff': 0.5,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.2,
                                    },
                                ],
                                'linear_dependency_formula': {
                                    'enabled': True,
                                    'from_class': 'econom',
                                    'surge_linear_coeff': 1.0,
                                },
                            },
                            'comfortplus': {
                                'time_rules': [],
                                'surge_rules': [
                                    {
                                        'min_coeff': 0.3,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.3,
                                    },
                                    {
                                        'min_coeff': 0.5,
                                        'alpha': 1,
                                        'beta': 0,
                                        'surcharge': 0,
                                        'surge_value': 1.2,
                                    },
                                ],
                                'linear_dependency_formula': {
                                    'enabled': True,
                                    'from_class': 'econom',
                                    'surge_linear_coeff': 1.0,
                                    'use_base_class_table': True,
                                },
                            },
                        },
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'rules': {
                            'econom': {
                                'surge_rules': [
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.1,
                                    },
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.2,
                                    },
                                ],
                                'time_rules': [],
                            },
                        },
                    },
                ],
            },
            200,  # OK: ascending surge_value is ok due to flat min_coeff
        ),
        # if method == 'linear', 'linear_dependency_formula' is required
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'rules': {
                            'econom': {
                                'surge_rules': [
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.1,
                                    },
                                ],
                                'time_rules': [],
                                'method': 'linear',
                                # linear_dependency_formula: {...}
                            },
                        },
                    },
                ],
            },
            400,
        ),
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'surcharge_enabled': False,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                        'rules': {
                            'econom': {
                                'surge_rules': [
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.5,
                                        'surcharge': 200,
                                        'surge_value': 1.1,
                                    },
                                    {
                                        'alpha': 0.2,
                                        'beta': 0.8,
                                        'min_coeff': 0.6,
                                        'surcharge': 200,
                                        'surge_value': 1.2,
                                    },
                                ],
                                'time_rules': [],
                            },
                        },
                    },
                ],
            },
            400,  # FAIL: ascending surge_value
        ),
    ],
)
@pytest.mark.config(ADMIN_AUDIT_USE_SERVICE=False)
async def test_update(web_app_client, db, data, code):
    old_alt_experiment_id = None
    if (
            isinstance(data, dict)
            and data
            and 'alternative_experiment_id' not in data
    ):
        old_db_dict = await db.surge_zones.find_one({'_id': data['id']})
        old_alt_experiment_id = old_db_dict.get('alternative_experiment_id')
    check_response = await web_app_client.post('/check_zone/', json=data)
    response = await web_app_client.post('/update_zone/', json=data)
    assert check_response.status == response.status == code
    if code == 200:
        check_json = await check_response.json()
        zone_json = await response.json()

        assert {'change_doc_id': data['id'], 'data': data} == check_json

        data['updated'] = zone_json['updated']
        data['square'] = 1
        data.setdefault('local_time_shift', zone_json['local_time_shift'])
        data.setdefault('type', zone_json['type'])

        if old_alt_experiment_id is not None:
            data['alternative_experiment_id'] = old_alt_experiment_id

        assert data == zone_json

        db_dict = zones_common.for_json(
            await db.surge_zones.find_one({'_id': zone_json['id']}),
        )
        zone_json['updated'] = dates.parse_timestring(zone_json['updated'])

        assert db_dict == zone_json

        clusters_snapshot = await db.surge_clusters_snapshot.find_one({})
        assert 'clusters' in clusters_snapshot


@pytest.mark.parametrize(
    'data,code',
    [
        (
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'removed': True,
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': 'not_existing',
                'removed': True,
                'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
                'tariff_class': 'econom',
                'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                'name': 'KARAGANDA',
                'forced': [
                    {
                        'is_active': True,
                        'experiment_name': 'BETTER_NOT_TO',
                        'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                    },
                ],
            },
            404,
        ),
    ],
)
@pytest.mark.config(ADMIN_AUDIT_USE_SERVICE=False)
async def test_delete(web_app_client, db, data, code):
    assert (
        await web_app_client.post('/update_zone/', json=data)
    ).status == code

    if code == 200:
        assert (
            await web_app_client.post('/update_zone/', json=data)
        ).status == 404

        clusters_snapshot = await db.surge_clusters_snapshot.find_one({})
        assert 'clusters' in clusters_snapshot
