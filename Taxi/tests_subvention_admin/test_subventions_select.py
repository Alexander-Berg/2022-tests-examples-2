# pylint: disable=C0302
import pytest

from . import test_common as common

_MOSCOW_AGGLOMERATIONS = [
    (
        'br_root/br_russia/br_tsentralnyj_fo/'
        'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow'
    ),
    (
        'br_root/br_russia/br_tsentralnyj_fo/'
        'br_moskovskaja_obl/br_moscow/br_moscow_adm'
    ),
    'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow',
]


def _build_single_ride_rule(rule_id, tag=None):
    rule = {
        'start': '2021-03-10T19:00:00+00:00',
        'end': '2022-03-09T19:00:00+00:00',
        'budget_id': '232a04eb-96bc-43ec-b6e6-0c33da308446',
        'tariff_class': 'econom',
        'id': rule_id,
        'draft_id': '139930',
        'schedule_ref': '139930',
        'updated_at': '2021-03-10T18:56:29.757587+00:00',
        'rule_type': 'single_ride',
        'geoarea': 'msk_iter7_pol31',
        'activity_points': 47,
        'zone': 'moscow',
        'rates': [
            {'week_day': 'mon', 'bonus_amount': '234', 'start': '07:00'},
        ],
        'branding_type': 'without_sticker',
    }
    if tag is not None:
        rule['tag'] = tag
    return rule


def _build_non_personal_goal_rule(rule_id, tag=None):
    rule = {
        'counters': {
            'schedule': [
                {'start': '00:00', 'week_day': 'mon', 'counter': 'A'},
            ],
            'steps': [{'id': 'A', 'steps': [{'nrides': 1, 'amount': '1288'}]}],
        },
        'rule_type': 'goal',
        'end': '2021-04-28T21:00:00+00:00',
        'start': '2021-04-19T21:00:00+00:00',
        'activity_points': 41,
        'currency': 'RUB',
        'budget_id': '9c150206-2972-4be9-88a2-10ac249bd274',
        'branding_type': 'without_sticker',
        'window': 1,
        'updated_at': '2021-04-20T07:45:17.91114+00:00',
        'tariff_class': 'econom',
        'id': rule_id,
        'geonode': (
            'br_root/br_russia/br_tsentralnyj_fo/'
            'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow'
        ),
        'global_counters': [{'global': '157009:A', 'local': 'A'}],
        'draft_id': '157009',
        'schedule_ref': '157009',
    }
    if tag is not None:
        rule['tag'] = tag
    return rule


def _build_personal_goal_rule(rule_id, tag=None):
    rule = {
        'geonode': (
            'br_root/br_russia/br_tsentralnyj_fo/'
            'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow'
        ),
        'tariff_class': 'econom',
        'window': 1,
        'counters': {
            'schedule': [
                {'start': '00:00', 'week_day': 'mon', 'counter': 'A'},
            ],
            'steps': [{'id': 'A', 'steps': [{'nrides': 1, 'amount': '1288'}]}],
        },
        'global_counters': [{'global': '157009:A', 'local': 'A'}],
        'currency': 'RUB',
        'start': '2021-04-19T21:00:00+00:00',
        'end': '2021-04-28T21:00:00+00:00',
        'updated_at': '2021-04-20T07:45:17.91114+00:00',
        'id': rule_id,
        'budget_id': '9c150206-2972-4be9-88a2-10ac249bd274',
        'draft_id': '157009',
        'schedule_ref': '157009',
        'rule_type': 'goal',
        'unique_driver_id': 'mock_udid',
        'branding_type': 'without_sticker',
    }
    if tag is not None:
        rule['tag'] = tag
    return rule


def _build_single_ontop_rule(rule_id, tag=None):
    rule = {
        'rule_type': 'single_ontop',  # required
        'rates': [
            {'week_day': 'mon', 'start': '00:00', 'bonus_amount': '345'},
            {'start': '00:00', 'week_day': 'sun', 'bonus_amount': '0'},
        ],  # required
        'schedule_ref': '379d5ce7-dea8-401d-b2a6-554b0bb94aa3',  # required
        'end': '2022-02-19T13:00:00+00:00',  # required
        'branding_type': 'without_sticker',
        'draft_id': '522013',  # required
        'tariff_class': 'econom',  # required
        'budget_id': 'bf39382d-6287-4d84-910a-cc063f74f397',  # required
        'zone': 'moscow',  # required
        'updated_at': '2022-01-18T12:53:10.881534+00:00',  # required
        'id': rule_id,  # required
        'start': '2022-01-18T13:00:00+00:00',  # required
        # 'activity_points' : 43,
        # 'tag' : '123',
        # 'geoarea' : 'lyberci_iter_1_pol3',
    }

    if tag is not None:
        rule['tag'] = tag

    return rule


def _get_rule_ids(rules):
    return [r['id'] for r in rules]


def _does_rule_match(rule, select_params):
    if select_params.rule_types is not None:
        if (
                'rule_type' not in rule
                or rule['rule_type'] not in select_params.rule_types
        ):
            return False

    if select_params.tags is not None:
        if select_params.tags is False:
            if 'tag' in rule:
                return False
        elif select_params.tags is True:
            if 'tag' not in rule:
                return False
        elif 'tag' not in rule or rule['tag'] not in select_params.tags:
            return False

    if select_params.tariff_classes is not None:
        if (
                'tariff_class' not in rule
                or rule['tariff_class'] not in select_params.tariff_classes
        ):
            return False

    if select_params.zones is not None:
        if 'geonode' not in rule and 'zone' not in rule:
            return False
        if 'geonode' in rule and rule['geonode'] not in select_params.zones:
            return False
        if 'zone' in rule and rule['zone'] not in select_params.zones:
            return False

    if select_params.unique_driver_id is not None:
        if (
                'unique_driver_id' not in rule
                or rule['unique_driver_id']
                not in select_params.unique_driver_id
        ):
            return False

    if 'unique_driver_id' in rule and select_params.unique_driver_id is None:
        return False

    if select_params.branding is not None:
        if (
                'branding_type' not in rule
                or rule['branding_type'] not in select_params.branding
        ):
            return False

    return True


@pytest.fixture(name='mock_bsx_v2_rules_select')
def _mock_bsx_v2_rules_select(mockserver):
    class Context:
        def __init__(self):
            self.rules = []
            self.params_of_requests = set()
            self.v2_rules_select = None

        def set_rules(self, rules):
            self.rules = rules

        def get_params_of_requests(self):
            return self.params_of_requests

    ctx = Context()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _v2_rules_select(request):
        select_params = common.extract_select_params(request.json)
        ctx.params_of_requests.add(select_params)
        rules = [r for r in ctx.rules if _does_rule_match(r, select_params)]
        return {'rules': rules}

    ctx.v2_rules_select = _v2_rules_select

    return ctx


@pytest.mark.config(
    SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS=True,
)
async def test_subventions_select(
        taxi_subvention_admin, mock_bsx_v2_rules_select,
):
    mock_bsx_v2_rules_select.set_rules(
        [
            _build_single_ride_rule('single_ride_with_tags', tag='tag1'),
            _build_single_ride_rule('single_ride_without_tags'),
            _build_personal_goal_rule('personal_goal_with_tags', tag='tag1'),
            _build_personal_goal_rule('personal_goal_without_tags'),
            _build_non_personal_goal_rule('goal_with_tags', tag='tag1'),
            _build_non_personal_goal_rule('goal_without_tags'),
            _build_single_ontop_rule('single_ontop_with_tags', tag='tag1'),
            _build_single_ontop_rule('single_ontop_without_tags'),
        ],
    )

    request_body = {
        'zones': ['moscow'],
        'tariff_classes': ['econom'],
        'subvention_geoareas': {'exact': ['moscow_center', 'moscow_ttk']},
        'branding': ['without_sticker'],
        'time_range': {
            'start': '2020-01-01T12:00:00+03:00',
            'end': '2020-01-01T12:00:01+03:00',
        },
        'tags': ['tag1', 'tag2'],
        'rule_types': ['goal', 'single_ride', 'single_ontop'],
        'unique_driver_ids': ['mock_udid'],
    }

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=request_body,
    )
    assert response.status_code == 200

    expected_rule_ids = [
        'single_ride_with_tags',
        'single_ride_without_tags',
        'personal_goal_with_tags',
        'personal_goal_without_tags',
        'goal_with_tags',
        'goal_without_tags',
        'single_ontop_with_tags',
        'single_ontop_without_tags',
    ]

    rules = response.json()['rules']
    assert sorted(_get_rule_ids(rules)) == sorted(expected_rule_ids)

    assert mock_bsx_v2_rules_select.get_params_of_requests() == {
        common.SelectParameters(
            rule_types=('single_ride',),
            tags=('tag1', 'tag2'),
            tariff_classes=('econom',),
            zones=('moscow',),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('single_ride',),
            tags=False,
            tariff_classes=('econom',),
            zones=('moscow',),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('goal',),
            tags=('tag1', 'tag2'),
            tariff_classes=('econom',),
            zones=None,
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=('mock_udid',),
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('goal',),
            tags=False,
            tariff_classes=('econom',),
            zones=None,
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=('mock_udid',),
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('goal',),
            tags=('tag1', 'tag2'),
            tariff_classes=('econom',),
            zones=common.make_hashable(_MOSCOW_AGGLOMERATIONS),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('goal',),
            tags=False,
            tariff_classes=('econom',),
            zones=common.make_hashable(_MOSCOW_AGGLOMERATIONS),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('single_ontop',),
            tags=('tag1', 'tag2'),
            tariff_classes=('econom',),
            zones=('moscow',),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
        common.SelectParameters(
            rule_types=('single_ontop',),
            tags=False,
            tariff_classes=('econom',),
            zones=('moscow',),
            geoareas=('moscow_center', 'moscow_ttk'),
            unique_driver_id=None,
            branding=('without_sticker',),
        ),
    }


@pytest.mark.parametrize(
    'driver_tags,expected_rule_ids',
    [
        pytest.param(
            # driver_tags
            ['subv_disable_goal', 'tag1'],
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'single_ride_without_tags',
                'personal_goal_with_tags',
                'personal_goal_without_tags',
                'single_ontop_with_tags',
                'single_ontop_without_tags',
            ],
            id='subv_disable_goal',
        ),
        pytest.param(
            # driver_tags
            ['subv_disable_all', 'tag1'],
            # expected_rule_ids
            [],
            id='subv_disable_all',
        ),
        pytest.param(
            # driver_tags
            ['subv_disable_personal_goal', 'tag1'],
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'single_ride_without_tags',
                'goal_with_tags',
                'goal_without_tags',
                'single_ontop_with_tags',
                'single_ontop_without_tags',
            ],
            id='subv_disable_personal_goal',
        ),
        pytest.param(
            # driver_tags
            ['subv_disable_single_ride', 'tag1'],
            # expected_rule_ids
            [
                'goal_with_tags',
                'goal_without_tags',
                'personal_goal_with_tags',
                'personal_goal_without_tags',
                'single_ontop_with_tags',
                'single_ontop_without_tags',
            ],
            id='subv_disable_single_ride',
        ),
        pytest.param(
            # driver_tags
            ['subv_disable_single_ontop', 'tag1'],
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'single_ride_without_tags',
                'goal_with_tags',
                'goal_without_tags',
                'personal_goal_with_tags',
                'personal_goal_without_tags',
            ],
            id='subv_disable_single_ontop',
        ),
    ],
)
async def test_filter_by_tags(
        taxi_subvention_admin,
        mock_bsx_v2_rules_select,
        driver_tags,
        expected_rule_ids,
):
    mock_bsx_v2_rules_select.set_rules(
        [
            _build_single_ride_rule('single_ride_with_tags', tag='tag1'),
            _build_single_ride_rule('single_ride_without_tags'),
            _build_personal_goal_rule('personal_goal_with_tags', tag='tag1'),
            _build_personal_goal_rule('personal_goal_without_tags'),
            _build_non_personal_goal_rule('goal_with_tags', tag='tag1'),
            _build_non_personal_goal_rule('goal_without_tags'),
            _build_single_ontop_rule('single_ontop_with_tags', tag='tag1'),
            _build_single_ontop_rule('single_ontop_without_tags'),
        ],
    )

    request_body = {
        'zones': ['moscow'],
        'tariff_classes': ['econom'],
        'geoareas': ['moscow_center', 'moscow_ttk'],
        'branding': ['without_sticker'],
        'time_range': {
            'start': '2020-01-01T12:00:00+03:00',
            'end': '2020-01-01T12:00:01+03:00',
        },
        'tags': driver_tags,
        'rule_types': ['goal', 'single_ride', 'single_ontop'],
        'unique_driver_ids': ['mock_udid'],
    }

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=request_body,
    )
    assert response.status_code == 200

    rules = response.json()['rules']
    assert sorted(_get_rule_ids(rules)) == sorted(expected_rule_ids)


@pytest.mark.parametrize(
    'our_request,expected_rules_select_params',
    [
        (
            # our_request
            {
                'subvention_geoareas': {
                    'exact': ['moscow_center', 'moscow_ttk'],
                },
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'subvention_geoareas': {
                    'suitable': ['moscow_center', 'moscow_ttk'],
                },
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=False,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=False,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'subvention_geoareas': {'has_geoarea': True},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=True,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=True,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=True,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'subvention_geoareas': {'has_geoarea': False},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=False,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=False,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=False,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
    ],
)
async def test_subvention_geoareas_constraint(
        taxi_subvention_admin,
        mock_bsx_v2_rules_select,
        our_request,
        expected_rules_select_params,
):
    mock_bsx_v2_rules_select.set_rules([])

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=our_request,
    )
    assert response.status_code == 200

    assert (
        mock_bsx_v2_rules_select.get_params_of_requests()
        == expected_rules_select_params
    )


@pytest.mark.parametrize(
    'our_request,expected_rules_select_params',
    [
        (
            # our_request
            {
                'tags_constraint': {'exact': ['tag1', 'tag2']},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=('tag1', 'tag2'),
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=('tag1', 'tag2'),
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'tags_constraint': {'for_support': ['tag1', 'tag2']},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=('tag1', 'tag2'),
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=('tag1', 'tag2'),
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'tags_constraint': {'has_tag': True},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=True,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=True,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'tags_constraint': {'has_tag': False},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
            },
        ),
        (  # 'tags_constraint' priority is more than 'tag'
            # our_request
            {
                'tags_constraint': {'has_tag': False},
                'tags': ['ignored_tag_1', 'ignored_tag_2'],
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=False,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
            },
        ),
    ],
)
async def test_subvention_tags_constraint(
        taxi_subvention_admin,
        mock_bsx_v2_rules_select,
        our_request,
        expected_rules_select_params,
):
    mock_bsx_v2_rules_select.set_rules([])

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=our_request,
    )
    assert response.status_code == 200
    assert (
        mock_bsx_v2_rules_select.get_params_of_requests()
        == expected_rules_select_params
    )


@pytest.mark.parametrize(
    'driver_tags,expected_rule_ids',
    [
        pytest.param(
            # driver_tags
            {
                'exact': [
                    'subv_disable_all',
                    'subv_disable_goal',
                    'subv_disable_personal_goal',
                    'subv_disable_single_ride',
                    'tag1',
                ],
            },
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'goal_with_tags',
                'personal_goal_with_tags',
                'single_ontop_with_tags',
            ],
            id='exact',
        ),
        pytest.param(
            # driver_tags
            {
                'for_support': [
                    'subv_disable_all',
                    'subv_disable_goal',
                    'subv_disable_personal_goal',
                    'subv_disable_single_ride',
                    'tag1',
                ],
            },
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'single_ride_without_tags',
                'goal_with_tags',
                'goal_without_tags',
                'personal_goal_with_tags',
                'personal_goal_without_tags',
                'single_ontop_with_tags',
                'single_ontop_without_tags',
            ],
            id='exact',
        ),
        pytest.param(
            # driver_tags
            {'has_tag': True},
            # expected_rule_ids
            [
                'single_ride_with_tags',
                'goal_with_tags',
                'personal_goal_with_tags',
                'single_ontop_with_tags',
            ],
            id='exact',
        ),
        pytest.param(
            # driver_tags
            {'has_tag': False},
            # expected_rule_ids
            [
                'single_ride_without_tags',
                'goal_without_tags',
                'personal_goal_without_tags',
                'single_ontop_without_tags',
            ],
            id='exact',
        ),
    ],
)
async def test_filter_by_tags_using_constraint(
        taxi_subvention_admin,
        mock_bsx_v2_rules_select,
        driver_tags,
        expected_rule_ids,
):
    mock_bsx_v2_rules_select.set_rules(
        [
            _build_single_ride_rule('single_ride_with_tags', tag='tag1'),
            _build_single_ride_rule('single_ride_without_tags'),
            _build_personal_goal_rule('personal_goal_with_tags', tag='tag1'),
            _build_personal_goal_rule('personal_goal_without_tags'),
            _build_non_personal_goal_rule('goal_with_tags', tag='tag1'),
            _build_non_personal_goal_rule('goal_without_tags'),
            _build_non_personal_goal_rule(
                'single_ontop_with_tags', tag='tag1',
            ),
            _build_non_personal_goal_rule('single_ontop_without_tags'),
        ],
    )
    request_body = {
        'zones': ['moscow'],
        'tariff_classes': ['econom'],
        'geoareas': ['moscow_center', 'moscow_ttk'],
        'branding': ['without_sticker'],
        'time_range': {
            'start': '2020-01-01T12:00:00+03:00',
            'end': '2020-01-01T12:00:01+03:00',
        },
        'tags_constraint': driver_tags,
        'rule_types': ['goal', 'single_ride', 'single_ontop'],
        'unique_driver_ids': ['mock_udid'],
    }

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=request_body,
    )
    assert response.status_code == 200

    rules = response.json()['rules']
    assert sorted(_get_rule_ids(rules)) == sorted(expected_rule_ids)


@pytest.mark.parametrize(
    'should_use_by_filters',
    [
        pytest.param(False, id='Use rules/select'),
        pytest.param(
            True,
            id='Use rules/by_filters',
            marks=[
                pytest.mark.config(SUBVENTION_ADMIN_USE_RULES_BY_FILTERS=True),
            ],
        ),
    ],
)
async def test_fetch_from_by_filters(
        taxi_subvention_admin, mockserver, should_use_by_filters,
):
    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _v2_rules_select(request):
        return {'rules': []}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/by_filters')
    async def _v2_rules_by_filters(request):
        return {'rules': []}

    request_body = {
        'zones': ['moscow'],
        'tariff_classes': ['econom'],
        'geoareas': ['moscow_center', 'moscow_ttk'],
        'time_range': {
            'start': '2020-01-01T12:00:00+03:00',
            'end': '2020-01-01T12:00:01+03:00',
        },
        'rule_types': ['goal'],
    }

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=request_body,
    )

    assert response.status_code == 200

    assert _v2_rules_by_filters.times_called == should_use_by_filters
    assert _v2_rules_select.times_called == (not should_use_by_filters)


@pytest.mark.parametrize(
    'our_request,expected_rules_select_params',
    [
        (
            # our_request
            {
                'zones': {'exact': ['moscow']},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=common.make_hashable(_MOSCOW_AGGLOMERATIONS),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=common.make_hashable(_MOSCOW_AGGLOMERATIONS),
                    geoareas=None,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
        (
            # our_request
            {
                'zones': {'suitable': ['moscow']},
                'rule_types': ['goal', 'single_ride'],
                'time_range': {
                    'start': '2020-01-01T12:00:00+03:00',
                    'end': '2020-01-01T12:00:01+03:00',
                },
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_rules_select_params
            {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=None,
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=common.make_hashable(_MOSCOW_AGGLOMERATIONS),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ),
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ),
            },
        ),
    ],
)
async def test_subvention_tariff_zone_constraint(
        taxi_subvention_admin,
        mock_bsx_v2_rules_select,
        our_request,
        expected_rules_select_params,
):
    mock_bsx_v2_rules_select.set_rules([])

    response = await taxi_subvention_admin.post(
        '/v1/subventions/select', json=our_request,
    )
    assert response.status_code == 200
    assert (
        mock_bsx_v2_rules_select.get_params_of_requests()
        == expected_rules_select_params
    )
