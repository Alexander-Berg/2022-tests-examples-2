from __future__ import unicode_literals

# from taxi.external import billing   # uncomment to launch test standalone
import json
from django import test as django_test
import pytest
from taxi.core import db
from taxi.internal import dbh


def assert_same_items(x_seq, y_seq):
    assert sorted(x_seq) == sorted(y_seq)


@pytest.mark.asyncenv('blocking')
def test_enumarate_surge_zones():
    response = django_test.Client().get(
        '/api/enumerate_surge_zones/'
    )
    assert response.status_code == 200
    assert_same_items(
        json.loads(response.content),
        [
            {
                'id': '094637bf71bd4675bf9d1103d6598426',
                'name': 'MSK-airport-SVO',
                'geometry': [
                    [
                        37.42341680849205,
                        55.94398687417875
                    ],
                    [
                        37.37507927380975,
                        55.9510776995972
                    ],
                    [
                        37.35210636343812,
                        55.9625639533571
                    ],
                    [
                        37.42341680849205,
                        55.94398687417875
                    ]
                ]
            },
            {
                'id': '973db8f0605a4da2b8839c575bcad772',
                'name': 'EKB',
                'geometry': [
                    [
                        60.97150402961129,
                        56.61976548203835
                    ],
                    [
                        60.40993449264003,
                        56.635857397142466
                    ],
                    [
                        60.23546136069812,
                        56.73326908562074
                    ],
                    [
                        60.97150402961129,
                        56.61976548203835
                    ]
                ]
            }
        ]
    )


@pytest.mark.asyncenv('blocking')
def test_get_surge_zone():
    response = django_test.Client().get(
        '/api/get_surge_zone/',
        {'id': '094637bf71bd4675bf9d1103d6598426'}
    )
    assert response.status_code == 200
    response_json = json.loads(response.content)
    assert response_json['production_experiment_id'] == '7999b840979b410b9347abc777a01053'
    assert response_json['alternative_experiment_id'] == '9cedfa150f2544fd8ac04ee4d06381a4'

    # Attempt to get non-existent zone results in 404
    response = django_test.Client().get(
        '/api/get_surge_zone/',
        {'id': 'non_existent_zone'}
    )
    assert response.status_code == 404


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_surge_zone():
    # Attempt to delete non-existent zone results in 404 for better visibility
    assert django_test.Client().get(
        '/api/get_surge_zone/',
        {'id': 'non_existent_zone'}
    ).status_code == 404

    assert django_test.Client().post(
        '/api/delete_surge_zone/',
        json.dumps({'id': 'non_existent_zone'}),
        'application/json'
    ).status_code == 404

    # Delete an existing zone (check-delete-audit-check)
    zone_id = '973db8f0605a4da2b8839c575bcad772'

    response = django_test.Client().get(
        '/api/get_surge_zone/',
        {'id': zone_id}
    )
    assert response.status_code == 200

    assert django_test.Client().post(
        '/api/delete_surge_zone/',
        json.dumps({'id': zone_id}),
        'application/json'
    ).status_code == 200

    assert (yield db.log_admin.find_one({
        'action': 'delete_surge_zone',
    })) is not None

    assert django_test.Client().get(
        '/api/get_surge_zone/',
        {'id': zone_id}
    ).status_code == 404


@pytest.mark.parametrize('data, code', [
    ('', 400),
    ({}, 400),
    # Baseline 200
    ({
        'id': '094637bf71bd4675bf9d1103d6598426',
        'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
        'tariff_class': 'econom',
        'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'name': 'KARAGANDA',
        'forced': [
            {
                'is_active': True,
                'experiment_name': 'BETTER_NOT_TO',
                'experiment_id': 'c1e39cb193054aedab92235ed32914bf'
            }
        ]
    }, 200),
    ({
        'id': '094637bf71bd4675bf9d1103d6598426',
        'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
        'tariff_class': 'econom',
        'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'alternative_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'name': 'KARAGANDA',
        'forced': [
            {
                'is_active': True,
                'experiment_name': 'BETTER_NOT_TO',
                'experiment_id': 'c1e39cb193054aedab92235ed32914bf'
            }
        ]
    }, 200),
    ({
        'id': '094637bf71bd4675bf9d1103d6598426',
        'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
        'tariff_class': 'econom',
        'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'alternative_experiment_id': '',
        'name': 'KARAGANDA',
        'forced': [
            {
                'is_active': True,
                'experiment_name': 'BETTER_NOT_TO',
                'experiment_id': 'c1e39cb193054aedab92235ed32914bf'
            }
        ]
    }, 200),
    # production_experiment_id must be one of experiment_id in forced[]
    ({
        'id': '094637bf71bd4675bf9d1103d6598426',
        'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
        'tariff_class': 'econom',
        'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'name': 'KARAGANDA',
        'forced': [
            {
                'is_active': True,
                'experiment_name': 'BETTER_NOT_TO',
                'experiment_id': '4466b186e18b44db941db751e004f795'
            }
        ]
    }, 400),
    # alternative_experiment_id must be one of experiment_id in forced[]
    ({
        'id': '094637bf71bd4675bf9d1103d6598426',
        'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
        'tariff_class': 'econom',
        'production_experiment_id': '4466b186e18b44db941db751e004f795',
        'alternative_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        'name': 'KARAGANDA',
        'forced': [
            {
                'is_active': True,
                'experiment_name': 'BETTER_NOT_TO',
                'experiment_id': '4466b186e18b44db941db751e004f795'
            }
        ]
    }, 400),
    ({
         'id': '094637bf71bd4675bf9d1103d6598426',
         'geometry': [[1, 1], [1, 2], [2, 2], [2, 1]],
         'tariff_class': 'econom',
         'production_experiment_id': 'c1e39cb193054aedab92235ed32914bf',
         'name': 'KARAGANDA',
         'forced': [
             {
                 'is_active': True,
                 'experiment_name': 'BETTER_NOT_TO',
                 'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
                 'rules': {
                     'econom': {
                         'time_rules': [],
                         'surge_rules': [
                             {'min_coeff': 0.3, 'surge_value': 1.3},
                             {'min_coeff': 0.5, 'surge_value': 1.5}
                         ]
                     }
                 }
             }
         ]
     }, 200)
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_surge_zone(data, code):
    url = '/api/update_surge_zone/'
    request = data if isinstance(data, unicode) else json.dumps(data)
    if (isinstance(data, dict) and data and
        'alternative_experiment_id' not in data):
        old_db_dict = (yield db.surge_zones.find_one({
            '_id': data['id']
        }))
        old_alt_experiment_id = old_db_dict.get('alternative_experiment_id')
    response = django_test.Client().post(url, request, 'application/json')
    assert response.status_code == code
    if code == 200:
        zone_json = json.loads(response.content)

        data['updated'] = zone_json['updated']
        data['square'] = 1

        assert data == zone_json

        assert (yield db.log_admin.find_one({
            'action': 'update_surge_zone',
        })) is not None

        db_dict = (yield db.surge_zones.find_one({
            '_id': zone_json['id']
        }))

        # replace short keys with attribute names
        for name in dbh.surge_zones.Doc.mapped_attributes():
            key = getattr(dbh.surge_zones.Doc, name)
            if name != key:
                db_dict[name] = db_dict[key]
                del db_dict[key]

        db_dict['updated'] = str(db_dict['updated'])
        if 'alternative_experiment_id' not in data:
            assert db_dict['alternative_experiment_id'] == old_alt_experiment_id
            db_dict.pop('alternative_experiment_id')

        assert db_dict == zone_json
