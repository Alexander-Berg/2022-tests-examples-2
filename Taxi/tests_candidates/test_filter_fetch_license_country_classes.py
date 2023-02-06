import pytest

CANDIDATES_LICENSE_COUNTRY_SETTINGS = {
    '__default__': [
        {
            'issue_country': ['null', 'tjk', 'uzb'],
            'classes': ['econom'],
            'skip_tag': 'tjk_no_license_skip',
            'is_allowing': True,
        },
    ],
    'countries': [
        {
            'names': ['rus'],
            'rules': [
                {
                    'issue_country': ['uzb', 'tjk'],
                    'classes': ['econom', 'minivan'],
                    'is_allowing': True,
                },
                {
                    'issue_country': ['null'],
                    'classes': ['vip'],
                    'is_allowing': False,
                },
            ],
        },
    ],
    'zones': [
        {
            'names': ['moscow'],
            'rules': [
                {
                    'issue_country': ['uzb', 'tjk', 'null'],
                    'classes': ['minivan'],
                    'skip_tag': 'uzb_msk_econom_skip',
                    'is_allowing': False,
                },
                {
                    'issue_country': ['null'],
                    'classes': ['econom'],
                    'is_allowing': False,
                },
            ],
        },
    ],
}


@pytest.mark.config(
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    CANDIDATES_LICENSE_COUNTRY_SETTINGS=CANDIDATES_LICENSE_COUNTRY_SETTINGS,
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid1', 'uzb_msk_econom_skip'),
        ('dbid_uuid', 'dbid0_uuid2', 'tjk_no_license_skip'),
    ],
)
@pytest.mark.parametrize(
    'zone_id, dbid_uuid, allowed_classes, count_drivers',
    [
        ('moscow', 'dbid0_uuid0', ['vip'], 0),  # -> "moscow" zone clause
        ('moscow', 'dbid0_uuid1', ['uberx'], 1),
        ('moscow', 'dbid0_uuid1', ['minivan'], 1),
        ('moscow', 'dbid0_uuid2', ['minivan'], 0),
        ('spb', 'dbid0_uuid0', ['vip'], 0),  # -> "rus" country clause
        ('spb', 'dbid0_uuid1', ['minivan'], 1),
        ('spb', 'dbid0_uuid1', ['econom'], 1),
        ('riga', 'dbid0_uuid0', ['minivan'], 0),  # -> __default__ clause
        ('riga', 'dbid0_uuid0', ['econom'], 1),
        ('riga', 'dbid0_uuid1', ['minivan'], 0),
        ('riga', 'dbid0_uuid2', ['minivan'], 1),
    ],
)
async def test_fetch_licence_country_classes(
        taxi_candidates,
        driver_positions,
        zone_id,
        dbid_uuid,
        count_drivers,
        allowed_classes,
):
    await driver_positions(
        [{'dbid_uuid': dbid_uuid, 'position': [55.5, 37.5]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'point': [55.5, 37.5],
        'filters': ['infra/class'],
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    drivers = response.json().get('drivers')
    assert len(drivers) == count_drivers
