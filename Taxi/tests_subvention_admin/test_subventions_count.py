import pytest

from . import test_common as common

BR_MOSCOW = 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow'
MOSCOW_AGGLOMERATIONS = (
    'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow',
    'br_root/br_russia/br_tsentralnyj_fo/'
    'br_moskovskaja_obl/br_moscow/br_moscow_adm',
    'br_root/br_russia/br_tsentralnyj_fo/'
    'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow',
)


def _filter_counts(params, counts):
    result = []

    for zone, by_type in counts.items():
        if zone in (params.zones or ()):
            count_by_type = []

            for rule_type, count in by_type.items():
                if rule_type in (params.rule_types or ()) and not params.tags:
                    count_by_type.append(
                        {'rule_type': rule_type, 'count': count},
                    )

            result.append({'zone': zone, 'rules_count_by_type': count_by_type})

    return result


@pytest.fixture(name='mock_bsx_v2_rules_count')
def _mock_bsx_v2_rules_count(mockserver):
    class Context:
        def __init__(self):
            self.counts = {
                common.SelectParameters(
                    rule_types=('single_ride',),
                    tags=None,
                    tariff_classes=('econom',),
                    zones=('moscow',),
                    geoareas=None,  # ('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 3},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'goal', 'count': 5},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=False,
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'goal', 'count': 5},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=True,
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'goal', 'count': 9},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=('tag1', 'tag2'),
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'goal', 'count': 7},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=False,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 5},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=('econom',),
                    zones=MOSCOW_AGGLOMERATIONS,
                    geoareas=('moscow_center', 'moscow_ttk'),
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 13},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('goal',),
                    tags=None,
                    tariff_classes=None,
                    zones=None,
                    geoareas=None,
                    unique_driver_id=('mock_udid',),
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 17},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('single_ontop',),
                    tags=None,
                    tariff_classes=('econom',),
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 19},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('single_ontop',),
                    tags=False,
                    tariff_classes=('econom',),
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 19},
                        ],
                    },
                ],
                common.SelectParameters(
                    rule_types=('single_ontop',),
                    tags=('tag1',),
                    tariff_classes=('econom',),
                    zones=('moscow',),
                    geoareas=None,
                    unique_driver_id=None,
                    branding=None,
                ): [
                    {
                        'zone': 'moscow',
                        'rules_count_by_type': [
                            {'rule_type': 'single_ride', 'count': 23},
                        ],
                    },
                ],
            }
            self.request_params = set()
            self.v2_rules_count = None

        def set_counts(self, counts):
            self.counts = counts

        def get_request_params(self):
            return self.request_params

    ctx = Context()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/count')
    async def _v2_rules_count(request):
        select_params = common.extract_select_params(request.json)
        ctx.request_params.add(select_params)

        counts = ctx.counts.get(select_params)

        if counts is None:
            assert False, (
                'Unexpected request in mock_bsx_v2_rules_count: '
                + f'{select_params}'
            )

        return {'rules_count': counts}

    ctx.v2_rules_count = _v2_rules_count

    return ctx


@pytest.mark.parametrize(
    'request_body,expected_response',
    (
        (
            # request_body
            {
                'rule_types': ('single_ride',),
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 3, 'rule_type': 'single_ride'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 5, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('single_ride', 'goal'),
                'tags': None,
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 3, 'rule_type': 'single_ride'},
                            {'count': 5, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags': ('tag1', 'tag2'),
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 12, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags_constraint': {'exact': ['tag1', 'tag2']},
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 7, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags_constraint': {'for_support': ['tag1', 'tag2']},
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 12, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags_constraint': {'has_tag': True},
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 9, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags_constraint': {'has_tag': False},
                'tags': ('tag1', 'tag2'),
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 5, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tags_constraint': None,
                'tariff_classes': ('econom',),
                'subvention_geoareas': {
                    'suitable': ['moscow_center', 'moscow_ttk'],
                },
                'zones': ('moscow',),
                'unique_driver_ids': None,
                'branding': None,
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 18, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('goal',),
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
                'unique_driver_ids': ['mock_udid'],
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 22, 'rule_type': 'goal'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
        (
            # request_body
            {
                'rule_types': ('single_ontop',),
                'tags_constraint': {'for_support': ['tag1']},
                'tariff_classes': ('econom',),
                'zones': ('moscow',),
            },
            # expected_response
            {
                'rules_count': [
                    {
                        'rules_count_by_type': [
                            {'count': 42, 'rule_type': 'single_ontop'},
                        ],
                        'zone': 'moscow',
                    },
                ],
            },
        ),
    ),
)
async def test_subventions_count(
        taxi_subvention_admin,
        mock_bsx_v2_rules_count,
        request_body,
        expected_response,
):
    request_body['time_range'] = {
        'start': '2020-01-01T12:00:00+03:00',
        'end': '2020-01-01T12:00:01+03:00',
    }

    response = await taxi_subvention_admin.post(
        '/v1/subventions/count', json=request_body,
    )

    assert response.status_code == 200

    counts = response.json()

    assert counts == expected_response
