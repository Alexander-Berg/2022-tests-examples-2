import pytest


import tests_candidates.helpers

_TAGS_LIST = [
    ('car_number', '\u0425492\u041d\u041a77', 'car_number_tag'),
    ('dbid_uuid', 'dbid0_uuid0', 'dbid_uuid_tag'),
    ('dbid_uuid', 'dbid0_uuid0', 'option_1_tag'),
    ('dbid_uuid', 'dbid0_uuid0', 'option_2_tag'),
    ('udid', '56f968f07c0aa65c44998e4b', 'udid_tag'),
    ('dbid_uuid', 'dbid1_uuid1', 'missing_option_tag'),
    ('dbid_uuid', 'dbid1_uuid1', 'missing_tag_1'),
    ('dbid_uuid', 'dbid1_uuid1', 'missing_tag_2'),
]
_KNOWN_TAGS = set({tag[2] for tag in _TAGS_LIST})


_STATIC_TAGS = pytest.mark.tags_v2_index(tags_list=_TAGS_LIST)
_TAXIMETER_VERSION_SETTINGS_BY_BUILD = pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': [],
            'feature_support': {
                'supported_1': '1.00',
                'supported_2': '1.01',
                'unsupported_1': '99.00',
                'unsupported_2': '99.00',
            },
            'min': '7.00',
        },
    },
)


def _is_known_tag(*tag_lists):
    for tag_list in tag_lists:
        if tag_list is None:
            continue
        for tag in tag_list:
            if tag not in _KNOWN_TAGS:
                return False
    return True


# 2 drivers: dbid0_uuid0 (with tags), dbid0_uuid1 (without any tag)
#
#
@pytest.fixture(name='prepare_state')
async def _prepare_state(
        taxi_candidates, taxi_config, driver_positions, exp_required_options,
):
    async def wrapper(**kwargs):
        await exp_required_options(**kwargs)

        taxi_config.set_values(
            dict(
                TAGS_INDEX={'enabled': True},
                ROUTER_SELECT=[
                    {'routers': ['yamaps']},
                    {'ids': ['moscow'], 'routers': ['linear-fallback']},
                ],
                EXTRA_EXAMS_BY_ZONE={},
            ),
        )
        await driver_positions(
            [
                {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
                {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            ],
        )

        await taxi_candidates.invalidate_caches(clean_update=False)

    return wrapper


@pytest.fixture(name='do_order_search')
async def _do_order_search(taxi_candidates, testpoint):
    async def wrapper(expect_missing_tag=False, expect_missing_feature=False):
        @testpoint(
            'cargo/fetch_required_options_classes::missing-taximeter-features',
        )
        def _testpoint_missing_taximeter_feature(param):
            pass

        @testpoint('cargo/fetch_required_options_classes::missing-tag')
        def _testpoint_missing_tag(param):
            pass

        response = await taxi_candidates.post(
            'order-search',
            json={
                'geoindex': 'kdtree',
                'limit': 3,
                'allowed_classes': ['econom', 'minivan', 'vip'],
                'zone_id': 'moscow',
                'point': [55, 35],
            },
        )
        assert response.status_code == 200

        if expect_missing_tag:
            assert _testpoint_missing_tag.has_calls
        else:
            assert not _testpoint_missing_tag.has_calls

        if expect_missing_feature:
            assert _testpoint_missing_taximeter_feature.has_calls
        else:
            assert not _testpoint_missing_taximeter_feature.has_calls

        return response.json()

    return wrapper


@pytest.fixture(name='do_order_satisfy')
async def _do_order_satisfy(taxi_candidates):
    async def wrapper():
        response = await taxi_candidates.post(
            'order-satisfy',
            json={
                'driver_ids': [{'uuid': 'uuid0', 'dbid': 'dbid0'}],
                'allowed_classes': ['econom', 'minivan', 'vip'],
                'zone_id': 'moscow',
                'point': [55, 35],
            },
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='do_satisfy')
async def _do_satisfy(taxi_candidates):
    async def wrapper():
        response = await taxi_candidates.post(
            'satisfy',
            json={
                'driver_ids': [{'uuid': 'uuid0', 'dbid': 'dbid0'}],
                'allowed_classes': ['econom', 'minivan', 'vip'],
                'zone_id': 'moscow',
                # 'point': [55, 35],
            },
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


def _second_candidate(matched_classes):
    return {
        'position': [55.0, 35.0],
        'id': 'dbid0_uuid1',
        'dbid': 'dbid0',
        'uuid': 'uuid1',
        'car_number': 'Х495НК77',
        'classes': matched_classes,
        'license_id': 'AB0256_id',
        'route_info': {'time': 0, 'distance': 0, 'approximate': False},
        'status': {
            'status': 'online',
            'orders': [],
            'driver': 'free',
            'taximeter': 'free',
        },
        'transport': {'type': 'car'},
        'unique_driver_id': '56f968f07c0aa65c44998e4e',
    }


def _first_candidate(matched_classes):
    return {
        'id': 'dbid0_uuid0',
        'dbid': 'dbid0',
        'uuid': 'uuid0',
        'car_number': '\u0425492\u041d\u041a77',
        'classes': matched_classes,
        'position': [55.0, 35.0],
        'route_info': {'distance': 0, 'time': 0, 'approximate': False},
        'status': {
            'driver': 'free',
            'orders': [],
            'status': 'online',
            'taximeter': 'free',
        },
        'unique_driver_id': '56f968f07c0aa65c44998e4b',
        'license_id': 'AB0253_id',
        'transport': {'type': 'car'},
    }


def _check_response(
        response_body,
        first_matched_classes=None,
        second_matched_classes=None,
        **kwargs,
):
    if first_matched_classes is None:
        first_matched_classes = ['econom', 'minivan']
    if second_matched_classes is None:
        second_matched_classes = ['vip']
    candidates = []
    if first_matched_classes:
        candidates.append(_first_candidate(first_matched_classes))
    if second_matched_classes:
        candidates.append(_second_candidate(second_matched_classes))

    actual, expected = tests_candidates.helpers.normalize(
        actual=response_body, expected={'candidates': candidates},
    )
    assert actual == expected


def _make_required_options_check(
        *,
        required_options=None,
        taxi_classes=None,
        with_tags=None,
        without_tags=None,
        supported_features=None,
        **kwargs,
):
    # default values
    if required_options is None:
        required_options = ['missing_option_tag']
    if taxi_classes is None:
        taxi_classes = ['econom']

    result = {
        'required_options': required_options,
        'taxi_classes': taxi_classes,
    }
    condition = {}
    if with_tags is not None:
        condition['with_tags'] = with_tags
    if without_tags is not None:
        condition['without_tags'] = without_tags
    if supported_features is not None:
        condition['supported_features'] = supported_features
    result['condition'] = condition
    return result


@pytest.fixture(name='exp_required_options')
async def _exp_required_options(experiments3, taxi_candidates):
    async def wrapper(*, enabled=True, checks=None, **kwargs):
        default_value = {'enabled': enabled}
        if checks is not None:
            default_value = {**default_value, **checks}
        else:
            default_value['common'] = [_make_required_options_check(**kwargs)]

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='required_options',
            consumers=['candidates/user'],
            clauses=[],
            default_value=default_value,
        )

        await taxi_candidates.invalidate_caches(clean_update=False)

    return wrapper


@_STATIC_TAGS
async def test_option_required(prepare_state, do_order_search):
    """
        'econom' was disabled for 'dbid0_uuid0'.
    """
    await prepare_state()

    response_body = await do_order_search()
    _check_response(response_body, first_matched_classes=['minivan'])


@_STATIC_TAGS
@pytest.mark.parametrize(
    'with_tags,without_tags,expected_classes',
    [  # checks passed
        [None, None, ['minivan']],
        [['dbid_uuid_tag', 'option_1_tag'], None, ['minivan']],
        [None, ['missing_tag_1', 'missing_tag_2'], ['minivan']],
        # checks not passed
        [None, ['unknown_tag'], ['econom', 'minivan']],  # fallback -> nocheck
        [['missing_tag_1'], None, ['econom', 'minivan']],
        [['missing_tag_1', 'dbid_uuid_tag'], None, ['econom', 'minivan']],
        [['missing_tag_1', 'missing_tag_2'], None, ['econom', 'minivan']],
        [None, ['dbid_uuid_tag'], ['econom', 'minivan']],
        [None, ['dbid_uuid_tag', 'missing_tag_1'], ['econom', 'minivan']],
        [None, ['dbid_uuid_tag', 'option_1_tag'], ['econom', 'minivan']],
    ],
)
async def test_tags_conditions(
        prepare_state,
        do_order_search,
        with_tags,
        without_tags,
        expected_classes,
):
    """
        Test different tags conditions.
        required_options config3.0 fields:
          - condition.with_tags
          - condition.without_tags
    """
    await prepare_state(with_tags=with_tags, without_tags=without_tags)

    response_body = await do_order_search(
        expect_missing_tag=not _is_known_tag(with_tags, without_tags),
    )

    _check_response(response_body, first_matched_classes=expected_classes)


@_STATIC_TAGS
async def test_multiple_taxi_classes(prepare_state, do_order_search):
    """
        'econom' and 'minivan' was disabled for 'dbid0_uuid0'.
        configured via taxi_classes
    """
    await prepare_state(taxi_classes=['econom', 'minivan'])

    response_body = await do_order_search()
    _check_response(response_body, first_matched_classes=[])


@_STATIC_TAGS
async def test_multiple_checks(prepare_state, do_order_search):
    """
        'econom' and 'minivan' was disabled for 'dbid0_uuid0'.
        configured via different checks
    """
    await prepare_state(
        checks={
            'common': [
                _make_required_options_check(taxi_classes=['econom']),
                _make_required_options_check(taxi_classes=['minivan']),
            ],
        },
    )

    response_body = await do_order_search()
    _check_response(response_body, first_matched_classes=[])


@_STATIC_TAGS
@_TAXIMETER_VERSION_SETTINGS_BY_BUILD
@pytest.mark.parametrize(
    'supported_features,expected_classes',
    [  # checks passed
        [None, ['minivan']],
        [['supported_1'], ['minivan']],
        [['supported_1', 'supported_2'], ['minivan']],
        # checks not passed
        [['unknown_1'], ['econom', 'minivan']],  # fallback -> nocheck
        [['unsupported_1'], ['econom', 'minivan']],
        [['supported_1', 'unsupported_1'], ['econom', 'minivan']],
        [['unsupported_1', 'unsupported_2'], ['econom', 'minivan']],
    ],
)
async def test_supported_features(
        prepare_state, do_order_search, supported_features, expected_classes,
):
    """
        Test different supported_features conditions.
        required_options config3.0 field condition.supported_features
    """
    await prepare_state(supported_features=supported_features)

    response_body = await do_order_search()

    _check_response(response_body, first_matched_classes=expected_classes)


def _check_diagnostics(
        response_body, expected, dbid='dbid0', uuid='uuid0', key='candidates',
):
    candidate = next(
        iter(
            candidate
            for candidate in response_body[key]
            if candidate['dbid'] == dbid and candidate['uuid'] == uuid
        ),
        None,
    )
    diagnostics = candidate.get('details', {}).get(
        'cargo/fetch_required_options_classes',
    )
    if diagnostics is not None:
        diagnostics.sort()

    assert diagnostics == expected


def _filtered_class_meta(class_type, required_options):
    return '{} by required_options: {}'.format(
        class_type, ', '.join(required_options),
    )


@_STATIC_TAGS
async def test_diagnostics(prepare_state, do_order_satisfy):
    """
        Check diagnostics returned on satisfy.
    """
    await prepare_state(taxi_classes=['econom', 'minivan'])

    response_body = await do_order_satisfy()

    _check_diagnostics(
        response_body,
        [
            _filtered_class_meta('econom', ['missing_option_tag']),
            _filtered_class_meta('minivan', ['missing_option_tag']),
        ],
    )


@_STATIC_TAGS
async def test_diagnostics_satisfy(prepare_state, do_satisfy):
    """
        Check diagnostics returned on satisfy.
    """
    await prepare_state(taxi_classes=['econom', 'minivan'])

    response_body = await do_satisfy()

    _check_diagnostics(
        response_body,
        [
            _filtered_class_meta('econom', ['missing_option_tag']),
            _filtered_class_meta('minivan', ['missing_option_tag']),
        ],
        key='drivers',
    )


@_STATIC_TAGS
async def test_statistics_missing_tags(prepare_state, do_order_search):
    """
        Check diagnostics returned on satisfy.
    """
    await prepare_state(required_options=['unknown_tag'])

    await do_order_search(expect_missing_tag=True)
