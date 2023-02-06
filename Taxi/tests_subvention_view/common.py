import copy
import dataclasses
import datetime
import functools
from typing import Optional
import urllib.parse

import dateutil.parser
import pytest
import pytz

DEFAULT_RULE_SETTINGS = [
    {
        'rule_type': 'daily_guarantee',
        'priority': 3,
        'deeplink': (
            'taximeter://screen/subvention_goals?show_no_data_dialog=true'
        ),
    },
    {
        'rule_type': 'goals',
        'priority': 2,
        'deeplink': (
            'taximeter://screen/subvention_goals?show_no_data_dialog=true'
        ),
    },
    {
        'rule_type': 'single_ride',
        'priority': 1,
        'deeplink': (
            'taximeter://screen/subvention_geo?show_no_data_dialog=true'
        ),
    },
]


TALLINN_GEONODES = pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_estonia',
            'name_en': 'Estonia',
            'name_ru': 'Эстония',
            'node_type': 'country',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_tallinn',
            'name_en': 'Tallinn',
            'name_ru': 'Таллин',
            'node_type': 'agglomeration',
            'parent_name': 'br_estonia',
            'tariff_zones': ['tallinn'],
            'tanker_key': 'name.br_tallinn',
            'region_id': '213',
        },
    ],
)


@dataclasses.dataclass
class SummaryExperimentData:
    agglomeration: Optional[str] = None
    node: Optional[str] = None


def _make_string_eq_predicate(key, value):
    return {
        'init': {'arg_name': key, 'arg_type': 'string', 'value': value},
        'type': 'eq',
    }


def _make_string_contains_predicate(key, value):
    return {
        'init': {'value': value, 'arg_name': key, 'set_elem_type': 'string'},
        'type': 'contains',
    }


def add_summary_exp3_config(
        exp3,
        rules_settings=None,
        fetch_smart_goals=False,
        use_banner=True,
        summary_exp_data=None,
):
    if rules_settings is None:
        rules_settings = DEFAULT_RULE_SETTINGS

    exp3_summary_value = {
        'use_banner': use_banner,
        'rules_settings': rules_settings,
        'fetch_smart_goals': fetch_smart_goals,
    }

    predicates = [{'type': 'true', 'init': {}}]
    if summary_exp_data is not None:
        if summary_exp_data.agglomeration is not None:
            predicates.append(
                _make_string_eq_predicate(
                    key='agglomeration', value=summary_exp_data.agglomeration,
                ),
            )
        if summary_exp_data.node is not None:
            predicates.append(
                _make_string_contains_predicate(
                    key='geo_nodes', value=summary_exp_data.node,
                ),
            )

    default_value = copy.deepcopy(exp3_summary_value)
    default_value['fetch_smart_goals'] = False

    exp3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_settings',
        consumers=[
            'subvention-view/v1/summary',
            'subvention-view/v1/personal/status',
        ],
        clauses=[
            {
                'title': 'test_experiment',
                'value': exp3_summary_value,
                'predicate': {
                    'init': {'predicates': predicates},
                    'type': 'all_of',
                },
            },
        ],
        default_value=default_value,
    )


def smart_subventions_matching(func):
    """Enables getting of single_rides from subvention-schedule"""

    @pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_smart_matching',
        consumers=[
            'subvention-view/v1/summary',
            'subvention-view/v1/schedule',
        ],
        clauses=[],
        default_value=True,
    )
    @functools.wraps(func)
    async def new_func(*args, **kwargs):
        return await func(*args, **kwargs)

    return new_func


def add_summary_exp3_links_config(exp3, deeplink_args_supported=True):

    exp3_summary_value = {
        'are_deeplink_args_supported': deeplink_args_supported,
        'goals_screen_deeplink': 'taximeter://screen/subvention_goals_v2?',
        'goals_details_screen_deeplink': (
            'taximeter://screen/subvention_goals_v2/details?'
        ),
    }

    predicates = [{'type': 'true', 'init': {}}]

    default_value = copy.deepcopy(exp3_summary_value)
    default_value['are_deeplink_args_supported'] = False

    exp3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_goals_deeplinks',
        consumers=['subvention-view/v1/summary'],
        clauses=[
            {
                'title': 'test_experiment',
                'value': exp3_summary_value,
                'predicate': {
                    'init': {'predicates': predicates},
                    'type': 'all_of',
                },
            },
        ],
        default_value=default_value,
    )


def add_candidates_request_mode_exp(exp3, mode):
    exp3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_candidates_request_mode',
        consumers=['subvention_view_fetch_driver_info'],
        clauses=[
            {
                'title': 'candidates_request_always_true',
                'value': {'mode': mode},
                'predicate': {
                    'init': {'predicates': [{'type': 'true', 'init': {}}]},
                    'type': 'all_of',
                },
            },
        ],
    )


def add_geo_experiment(exp3, name, geo_exp_tag):
    exp3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name=name,
        consumers=['geo_experiment_consumer'],
        clauses=[
            {
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'is_tech_group': False,
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'always_true',
                'value': {'geo_exp_tag': geo_exp_tag},
            },
        ],
        default_value={},
    )


def add_single_ontop_experiment(
        exp3, match_ontops=True, cover_in_summary=True,
):
    exp3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_cover_single_ontop',
        consumers=['subvention-view/v1/summary'],
        clauses=[],
        default_value={'enable': cover_in_summary},
    )

    exp3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_single_ontop',
        consumers=[
            'subvention-view/v1/summary',
            'subvention-view/v1/schedule',
        ],
        clauses=[],
        default_value=match_ontops,
    )


def enable_single_ontop(func):
    """Enables getting of single_ontop"""

    @pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_cover_single_ontop',
        consumers=['subvention-view/v1/summary'],
        clauses=[],
        default_value={'enable': True},
    )
    @pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_single_ontop',
        consumers=[
            'subvention-view/v1/summary',
            'subvention-view/v1/schedule',
        ],
        clauses=[],
        default_value=True,
    )
    @functools.wraps(func)
    async def new_func(*args, **kwargs):
        return await func(*args, **kwargs)

    return new_func


def is_floats_equal(fl1, fl2, eps=1e-6):
    return abs(fl1 - fl2) < eps


def parse_time(as_str: str, default_tz='UTC') -> datetime.datetime:
    """
    Parses string with time of almost any format to datetime.datetime
    with awared timezone. You can compare returned datetimes between
    each other and don't care about difference in time zones.
    """
    _dt = dateutil.parser.parse(as_str)
    if not _dt.tzinfo:
        utc = pytz.timezone(default_tz)
        _dt = utc.localize(_dt)
    return _dt


def parse_url_with_args(url):
    """
    Parses url to tuple of components so that args are stored into dict.
    You can compare returned url representations insensitively to args order.
    """
    split = urllib.parse.urlsplit(url)
    args_dict = urllib.parse.parse_qs(split.query)
    return (split.scheme, split.netloc, split.path, args_dict, split.fragment)


def make_polling_policy(polling_delay):
    return f'full={polling_delay}s, background=disabled'
