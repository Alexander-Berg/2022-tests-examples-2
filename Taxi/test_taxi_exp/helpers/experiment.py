import copy
import datetime
import json
import logging
import typing
from typing import Callable

from taxi_exp.util import predicate_helpers

logger = logging.getLogger(__name__)

CURRENT_YEAR = datetime.datetime.now().year

DEFAULT_NAMESPACE = None
DEFAULT_PREDICATE = {'type': 'true'}
DEFAULT_QUERY = 'TRUE'
DEFAULT_SCHEMA = """
description: 'default schema'
additionalProperties: true
    """
FROM_TIME = f'{CURRENT_YEAR - 1}-12-31T23:59:59+03:00'
TO_TIME = f'{CURRENT_YEAR}-12-31T23:59:59+03:00'
DEFAULT_ACTION_TIME = {'from': FROM_TIME, 'to': TO_TIME}
DEFAULT_VALUE: typing.Dict = {}
DEFAULT_CLAUSES = [
    {'title': 'default', 'predicate': DEFAULT_PREDICATE, 'value': {}},
]
DEFAULT_CONSUMERS = [{'name': 'test_consumer'}]

DEFAULT_ARG_NAME = 'phone_id'
DEFAULT_ELEM_TYPE = 'string'

DEFAULT_EXP_SHUTDOWN_MODE = 'instant_shutdown'
DEFAULT_CONFIG_SHUTDOWN_MODE = 'config_no_shutdown'
DEFAULT = object()
DEFAULT_EXPERIMENT_NAME = 'Default_Experiment_Name'
DEFAULT_DEPARTMENT = 'common'
DEFAULT_SERVICE = None

is_bool: Callable = lambda x: isinstance(x, bool)
is_string: Callable = lambda x: isinstance(x, str)


def infile_predicate(file_id, arg_name=DEFAULT, set_elem_type=DEFAULT):
    if arg_name is DEFAULT:
        arg_name = DEFAULT_ARG_NAME
    if set_elem_type is DEFAULT:
        set_elem_type = DEFAULT_ELEM_TYPE
    return {
        'type': 'in_file',
        'init': {
            'file': file_id,
            'arg_name': arg_name,
            'set_elem_type': set_elem_type,
        },
    }


def userhas_predicate(tag):
    return {'type': 'user_has', 'init': {'tag': tag}}


def not_predicate(predicate):
    return {'type': 'not', 'init': {'predicate': predicate}}


def _uni_predicate(name, predicates):
    return {'type': name, 'init': {'predicates': predicates}}


def anyof_predicate(predicates):
    return _uni_predicate('any_of', predicates)


def allof_predicate(predicates):
    return _uni_predicate('all_of', predicates)


def inset_predicate(
        set_,
        arg_name=DEFAULT,
        set_elem_type=DEFAULT,
        transform=None,
        phone_type=None,
):
    if arg_name is DEFAULT:
        arg_name = DEFAULT_ARG_NAME
    if set_elem_type is DEFAULT:
        set_elem_type = DEFAULT_ELEM_TYPE
    result = {
        'type': 'in_set',
        'init': {
            'set': set_,
            'arg_name': arg_name,
            'set_elem_type': set_elem_type,
        },
    }

    if transform:
        if transform == 'replace_phone_to_phone_id':
            assert phone_type in {'yandex', 'uber'}
            result['init']['transform'] = transform
            result['init']['phone_type'] = phone_type
        elif transform == 'replace_phone_to_personal_phone_id':
            result['init']['transform'] = transform
        else:
            assert False, (
                'transform must be replace_phone_to_phone_id or '
                'replace_phone_to_personal_phone_id only'
            )
    return result


def segmentation_predicate(
        arg_name=DEFAULT_ARG_NAME,
        range_from=DEFAULT,
        range_to=DEFAULT,
        salt=DEFAULT,
        divisor=DEFAULT,
):
    return _segmentation(
        predicate_type='segmentation',
        arg_name=arg_name,
        range_from=range_from,
        range_to=range_to,
        salt=salt,
        divisor=divisor,
    )


def mod_sha1_predicate(
        arg_name=DEFAULT_ARG_NAME,
        range_from=DEFAULT,
        range_to=DEFAULT,
        salt=DEFAULT,
        divisor=DEFAULT,
):
    return _segmentation(
        predicate_type='mod_sha1_with_salt',
        arg_name=arg_name,
        range_from=range_from,
        range_to=range_to,
        salt=salt,
        divisor=divisor,
    )


def _segmentation(
        predicate_type,
        arg_name=DEFAULT_ARG_NAME,
        range_from=DEFAULT,
        range_to=DEFAULT,
        salt=DEFAULT,
        divisor=DEFAULT,
):
    range_from = 0 if range_from is DEFAULT else range_from
    range_to = 100 if range_to is DEFAULT else range_to
    assert range_from < range_to
    salt = 'salt' if salt is DEFAULT else salt
    divisor = 100 if divisor is DEFAULT else divisor

    return {
        'type': predicate_type,
        'init': {
            'arg_name': arg_name,
            'range_from': range_from,
            'range_to': range_to,
            'salt': salt,
            'divisor': divisor,
        },
    }


def _comparison(name, value, arg_type=DEFAULT, arg_name=DEFAULT):
    if arg_name is DEFAULT:
        arg_name = DEFAULT_ARG_NAME
    if arg_type is DEFAULT:
        arg_type = DEFAULT_ELEM_TYPE
    return {
        'type': name,
        'init': {'value': value, 'arg_name': arg_name, 'arg_type': arg_type},
    }


def gt_predicate(value, arg_type=DEFAULT, arg_name=DEFAULT):
    return _comparison('gt', value, arg_type=arg_type, arg_name=arg_name)


def eq_predicate(value, arg_type=DEFAULT, arg_name=DEFAULT):
    return _comparison('eq', value, arg_type=arg_type, arg_name=arg_name)


def lt_predicate(value, arg_type=DEFAULT, arg_name=DEFAULT):
    return _comparison('lt', value, arg_type=arg_type, arg_name=arg_name)


def time_segmentation(
        arg_name=DEFAULT_ARG_NAME,
        start_time=DEFAULT,
        range_from=DEFAULT,
        range_to=DEFAULT,
        period=DEFAULT,
        salt=None,
        daily_timestamp_increment=None,
):
    start_time = (
        '2022-02-17T00:00:00+03:00' if start_time is DEFAULT else start_time
    )
    range_from = 0 if range_from is DEFAULT else range_from
    range_to = 40 if range_to is DEFAULT else range_to
    period = 120 if period is DEFAULT else period

    init = {
        'arg_name': arg_name,
        'start_time': start_time,
        'range_from': range_from,
        'range_to': range_to,
        'period': period,
    }
    if salt:
        init['salt'] = salt
    if daily_timestamp_increment:
        init['daily_timestamp_increment'] = daily_timestamp_increment
    return {'init': init, 'type': 'time_segmentation'}


def make_clause(
        title,
        predicate=DEFAULT,
        value=DEFAULT,
        extended_value=None,
        extension_method=None,
        is_signal=None,
        is_paired_signal=None,
        query=None,
        alias=None,
        is_tech_group=None,
        enabled=None,
):
    if predicate is DEFAULT:
        predicate = DEFAULT_PREDICATE
    if value is DEFAULT:
        value = DEFAULT_VALUE

    clause = {'title': title, 'value': value}
    if extended_value is not None:
        assert extension_method in ['replace', 'extend', 'deep_extend']
        clause['extended_value'] = extended_value
        clause['extension_method'] = extension_method
    if query is not None:
        assert isinstance(query, str)
        clause['query'] = query
    else:
        clause['predicate'] = predicate

    for field, field_value, check in (
            ('alias', alias, is_string),
            ('enabled', enabled, is_bool),
            ('is_paired_signal', is_paired_signal, is_bool),
            ('is_signal', is_signal, is_bool),
            ('is_tech_group', is_tech_group, is_bool),
    ):
        if field_value is not None:
            assert check(field_value)
            clause[field] = field_value

    return clause


def make_fallback(
        short_description='',
        what_happens_when_turn_off='',
        need_turn_off=False,
        placeholder=None,
):
    result = {
        'short_description': short_description,
        'what_happens_when_turn_off': what_happens_when_turn_off,
        'need_turn_off': need_turn_off,
    }
    if placeholder is not None:
        result['placeholder'] = placeholder
    return result


def make_prestable_flow(wait_on_prestable: int, rollout_stable_time=None):
    settings = {'wait_on_prestable': wait_on_prestable}
    if rollout_stable_time is not None:
        settings['rollout_stable_time'] = rollout_stable_time
    return settings


def make_consumers(*names):
    return [{'name': name} for name in names]


def generate_default(**kwargs):
    if 'name' in kwargs:
        kwargs.pop('name')
    if 'applications' in kwargs:
        kwargs.pop('applications')

    return generate(
        name='Experiment',
        applications=[
            {
                'name': 'ios',
                'version_range': {'from': '0.0.0', 'to': '99.99.99'},
            },
            {
                'name': 'android',
                'version_range': {'from': '0.0.0', 'to': '99.99.99'},
            },
        ],
        **kwargs,
    )


def generate_config(**kwargs):
    response = generate(**kwargs)

    response['match'] = {
        key: value
        for key, value in response['match'].items()
        if key not in {'action_time', 'applications'}
    }

    if 'predicate' in response['match']:
        response['match']['predicate'] = DEFAULT_PREDICATE
    else:
        response['match']['query'] = DEFAULT_QUERY

    if response['default_value'] is None:
        response['default_value'] = DEFAULT_VALUE

    if response['shutdown_mode'] == DEFAULT_EXP_SHUTDOWN_MODE:
        response['shutdown_mode'] = DEFAULT_CONFIG_SHUTDOWN_MODE

    if 'is_technical' not in response:
        response['is_technical'] = False

    logger.debug('GENERATED CONFIG FOR TEST: %s', response)
    return response


def generate_default_history_item(**kwargs):
    id_ = kwargs.pop('id', 1)
    rev = kwargs.pop('rev', 1)
    closed = kwargs.pop('closed', False)
    removed = kwargs.pop('removed', False)
    is_config = kwargs.pop('is_config', False)
    financial = kwargs.pop('financial', True)
    removed_stamp = kwargs.pop('removed_stamp', None)

    experiment = generate_default(**kwargs)
    files_data = predicate_helpers.extract_files_data(
        [experiment['match']['predicate']]
        + [clause['predicate'] for clause in experiment['clauses']],
    )
    tags = files_data.file_tags
    files = files_data.file_ids
    applications = []
    for app in experiment['match'].get('applications', []):
        item = {
            'name': app['name'],
            'version_from': app['version_range']['from'],
        }
        version_to = app['version_range'].get('to')
        if version_to is not None:
            item['version_to'] = version_to
        applications.append(item)
    consumers = [
        consumer['name'] for consumer in experiment['match']['consumers']
    ]

    return {
        'id': id_,
        'rev': rev,
        'name': kwargs.get('name', DEFAULT_EXPERIMENT_NAME),
        'tags': tags,
        'files': files,
        'closed': closed,
        'enabled': experiment['match']['enabled'],
        'removed': removed,
        'financial': financial,
        'is_config': is_config,
        'schema': experiment['match']['schema'],
        'clauses': experiment['clauses'],
        'date_to': experiment['match']['action_time'].get('to'),
        'date_from': experiment['match']['action_time']['to'],
        'consumers': consumers,
        'predicate': experiment['match']['predicate'],
        'description': experiment['description'],
        'applications': applications,
        'default_value': experiment['default_value'],
        'removed_stamp': removed_stamp,
        'shutdown_mode': DEFAULT_EXP_SHUTDOWN_MODE,
    }


def generate(
        name=None,
        consumers=DEFAULT,
        applications=None,
        match_predicate=DEFAULT,
        clauses=DEFAULT,
        schema=DEFAULT,
        action_time=DEFAULT,
        enabled=True,
        closed=False,
        description=None,
        default_value=None,
        fallback=None,
        owners=None,
        watchers=None,
        self_ok=False,
        financial=True,
        is_technical=None,
        enable_debug=False,
        merge_values_by=None,
        trait_tags=None,
        st_tickets=None,
        department=None,
        service_id=None,
        service_name=None,
        namespace=DEFAULT,
        shutdown_mode=None,
        prestable_flow=None,
        last_modified_at=None,
        gradual_shutdown_time_step=None,
        gradual_shutdown_percentage_step=None,
        schema_id=None,
        allow_empty_schema=None,
):
    assert DEFAULT_CLAUSES
    if consumers is DEFAULT:
        consumers = copy.deepcopy(DEFAULT_CONSUMERS)
    if match_predicate is DEFAULT:
        match_predicate = copy.deepcopy(DEFAULT_PREDICATE)
    if clauses is DEFAULT:
        clauses = copy.deepcopy(DEFAULT_CLAUSES)
    if action_time is DEFAULT:
        action_time = copy.deepcopy(DEFAULT_ACTION_TIME)
    if schema is DEFAULT:
        schema = DEFAULT_SCHEMA
    if namespace is DEFAULT:
        namespace = DEFAULT_NAMESPACE
    if isinstance(schema, dict):
        schema = json.dumps(schema)

    experiment = {
        'description': description or f'Description for {name}',
        'match': {
            'enabled': enabled,
            'schema': schema,
            'action_time': action_time,
            'consumers': consumers,
            'predicate': match_predicate,
        },
        'closed': closed,
        'clauses': clauses,
        'default_value': default_value,
        'self_ok': self_ok,
        'enable_debug': enable_debug,
    }

    if financial is not None:
        experiment['financial'] = financial

    if (
            gradual_shutdown_time_step is not None
            and gradual_shutdown_percentage_step is not None
    ):
        experiment['gradual_shutdown_settings'] = {
            'time_step': gradual_shutdown_time_step,
            'percentage_step': gradual_shutdown_percentage_step,
        }

    for field, field_name, is_match, default_field_value in (
            (name, 'name', False, None),
            (department, 'department', False, DEFAULT_DEPARTMENT),
            (service_id, 'service_id', False, DEFAULT_SERVICE),
            (service_name, 'service_name', False, None),
            (namespace, 'namespace', False, DEFAULT_NAMESPACE),
            (shutdown_mode, 'shutdown_mode', False, DEFAULT_EXP_SHUTDOWN_MODE),
            (applications, 'applications', True, None),
            (fallback, 'fallback', False, None),
            (owners, 'owners', False, None),
            (watchers, 'watchers', False, None),
            (merge_values_by, 'merge_values_by', False, None),
            (trait_tags, 'trait_tags', False, []),
            (st_tickets, 'st_tickets', False, []),
            (prestable_flow, 'prestable_flow', False, None),
            (last_modified_at, 'last_modified_at', False, None),
            (is_technical, 'is_technical', False, None),
            (schema_id, 'schema_id', False, None),
            (allow_empty_schema, 'allow_empty_schema', False, None),
    ):
        exp = experiment
        if is_match:
            exp = experiment['match']
        if field is not None:
            exp[field_name] = field
        elif default_field_value is not None:
            exp[field_name] = default_field_value

    logger.debug('GENERATED EXPERIMENT FOR TEST: %s', experiment)

    return experiment
