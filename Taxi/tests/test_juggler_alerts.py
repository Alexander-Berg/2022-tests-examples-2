import os.path
from typing import Dict

import collections
import jsonschema
import pytest
import scripts.common as common
import yaml


CHECK_DEF_SCHEMA = 'check_def.yaml'
DEFAULT_DEF_SCHEMA = 'default_def.yaml'
TEMPLATE_DEF_SCHEMA = 'template_def.yaml'
TELEGRAM_OPTIONS_DEF_SCHEMA = 'telegram_options_def.yaml'
DEPENDENCIES_ADD_SCHEMA = 'dependencies_add_def.yaml'
DEPENDENCIES_FILTER_SCHEMA = 'dependencies_filter_def.yaml'


@pytest.fixture(scope='session', name='check_validator')
def _check_validator():
    return common.get_validator(CHECK_DEF_SCHEMA)


@pytest.fixture(scope='session', name='default_validator')
def _default_validator():
    return common.get_validator(DEFAULT_DEF_SCHEMA)


@pytest.fixture(scope='session', name='template_validator')
def _template_validator():
    return common.get_validator(TEMPLATE_DEF_SCHEMA)


@pytest.fixture(scope='session', name='telegram_options')
def _telegram_options():
    return common.try_load_yaml(common.TELEGRAM_OPTIONS_FILEPATH)


@pytest.fixture(scope='session', name='juggler_host_has_primary')
def _juggler_host_has_primary():
    result = {}
    for info in common.get_all_checks_info():
        check = common.try_load_yaml(info.check_path)
        host = check['host']
        is_primary = not check.get('is_secondary_checkfile')

        result[host] = is_primary or bool(result.get(host))

    return result


def _normalize(data):
    if data is None:
        return []
    if isinstance(data, (list, tuple)):
        return list(data)
    return [data]


def _collect_param(data: Dict, is_default: bool, param: str):
    if is_default:
        result = []
        for _, params in data.items():
            result.extend(_normalize(params.get(param)))
        return result
    else:
        return _normalize(data.get(param))


@pytest.mark.parametrize(
    'namespace_path, check_path',
    [
        pytest.param(
            check_info.namespace_path,
            check_info.check_path,
            id=check_info.check_path,
        )
        for check_info in common.get_all_checks_info()
        + common.get_all_default_yaml()
    ],
)
def test_check(
        namespace_path,
        check_path,
        check_validator,
        default_validator,
        telegram_options,
):
    is_default = os.path.basename(check_path) == 'default.yaml'
    check = common.try_load_yaml(check_path)

    try:
        if is_default:
            default_validator.validate(check)
        else:
            check_validator.validate(check)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as exc:
        raise Exception(f'Validation of {check_path} failed: {exc.message}')

    default_templates = common.get_templates(common.DEFAULT_NAMESPACE)
    ns_templates = common.get_templates(namespace_path)
    available_templates = default_templates | ns_templates
    templates = _collect_param(check, is_default, 'templates')
    included_templates = [x['template'] for x in templates]
    diff_templates = set(included_templates) - available_templates

    assert (
        not diff_templates
    ), f'Check {check_path} includes non existing templates: {diff_templates}.'

    # TODO: enforce sorting for included templates after decision in task
    #   https://st.yandex-team.ru/TAXIPLATFORM-3073#600831dce8b08d4f752552f6
    # assert sorted(included_templates) == included_templates, (
    #     'Included templates should be sorted, run: ',
    #     'python3 ./scripts/sort_templates.py',
    # )

    telegrams = set()
    telegrams.update(_collect_param(check, is_default, 'telegram'))
    telegrams.update(_collect_param(check, is_default, 'additional_telegram'))
    for template in templates:
        telegrams.update(_normalize(template.get('telegram')))
    for service in _collect_param(check, is_default, 'services'):
        telegrams.update(_normalize(service.get('telegram')))
    for telegram in telegrams:
        if telegram is None:
            continue

        assert telegram in telegram_options, (
            f'Telegram {telegram} is not present in: '
            f'{common.TELEGRAM_OPTIONS_FILEPATH}'
        )


@pytest.mark.parametrize('template_path', common.get_all_template_paths())
def test_template(template_path, template_validator, telegram_options):
    template = common.try_load_yaml(template_path)

    try:
        template_validator.validate(template)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as exc:
        raise Exception(f'Validation of {template_path} failed: {exc.message}')

    telegrams = {
        service.get('telegram') for service in template.get('services', [])
    }
    for telegram in telegrams:
        if telegram is None:
            continue

        assert telegram in telegram_options


def test_telegram_options(telegram_options):
    validator = common.get_validator(TELEGRAM_OPTIONS_DEF_SCHEMA)
    try:
        validator.validate(telegram_options)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as exc:
        raise Exception(
            (
                f'Validation of {common.TELEGRAM_OPTIONS_FILEPATH} '
                f'failed: {exc.message}'
            ),
        )


def test_unique_primary_checkfile():
    juggler_host_filepaths = collections.defaultdict(list)
    for info in common.get_all_checks_info():
        checkfile = common.try_load_yaml(info.check_path)
        if checkfile.get('is_secondary_checkfile', False):
            continue
        juggler_host_filepaths[checkfile['host']].append(info.check_path)

    for host, paths in juggler_host_filepaths.items():
        has_unique_primary = len(paths) <= 1
        assert has_unique_primary, (
            '\nCheck for uniqueness of primary checkfile has been failed '
            f'for host: {host}.\n'
            'You should either mark secondary checkfiles with '
            '\'is_secondary_checkfile: true\', or merge the checkfiles with'
            'the same host into one file.\n   List of primary checkfiles:\n'
            + '\n'.join(paths)
        )


@pytest.mark.parametrize(
    'filepath, schema_name',
    [
        (common.DEPENDENCIES_ADD_FILEPATH, DEPENDENCIES_ADD_SCHEMA),
        (common.DEPENDENCIES_FILTER_FILEPATH, DEPENDENCIES_FILTER_SCHEMA),
    ],
)
def test_dependencies_schemas(filepath, schema_name):
    validator = common.get_validator(schema_name)
    with open(filepath) as infile:
        config = yaml.safe_load(infile)

    try:
        validator.validate(config)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as exc:
        raise Exception(
            f'Validation of {os.path.basename(filepath)} '
            f'failed: {exc.message}',
        )


def test_dependencies_filter(juggler_host_has_primary):
    with open(common.DEPENDENCIES_FILTER_FILEPATH) as infile:
        config = yaml.safe_load(infile)

    for index, item in enumerate(config):
        for key in ['source', 'target']:
            if not item.get(key):
                raise Exception(
                    f'Item index={index} of dependencies_filter.yaml has '
                    f'empty "{key}", that\'s not allowed',
                )

            host = item[key].get('host')
            if host is not None:
                assert host in juggler_host_has_primary, (
                    f'host={host} not found in repo, but used in '
                    f'dependencies_filter.yaml'
                )


def test_dependencies_add(juggler_host_has_primary):
    with open(common.DEPENDENCIES_ADD_FILEPATH) as infile:
        config = yaml.safe_load(infile)

    for source_host, target_hosts in config.items():
        assert juggler_host_has_primary.get(source_host), (
            f'host={source_host} is used as source in dependencies_add.yaml, '
            f'it must have primary checkfile, but it doesn\'t'
        )

        for target_host in target_hosts:
            assert target_host in juggler_host_has_primary, (
                f'host={target_host} not found in repo, but used in '
                f'dependencies_add.yaml'
            )


def test_directory_structure():
    assert not os.path.exists(
        os.path.join(common.CHECKS_DIR_PATH, common.DEFAULT_YAML),
    ), 'root default.yaml is prohibited'
    assert not os.path.exists(
        os.path.join(common.CHECKS_DIR_PATH, common.TEMPLATES_DIR),
    ), 'root templates/ is prohibited'

    namespace_paths = common.get_all_namespace_paths()

    namespace_counter = collections.Counter(
        map(os.path.basename, namespace_paths),
    )
    for namespace_name, count in namespace_counter.most_common(1):
        assert (
            count == 1
        ), f'namespace "{namespace_name}" occurs multiple times in repo'

    for template_dir in common.get_all_template_dirs():
        assert not common.list_dir_dir_names(
            template_dir,
        ), 'templates/ dir must contain template files only'

    for dirpath, dirnames, filenames in os.walk(common.CHECKS_DIR_PATH):
        default_yaml = os.path.join(dirpath, common.DEFAULT_YAML)
        assert not os.path.exists(default_yaml) or os.path.isfile(
            default_yaml,
        ), 'default.yaml is a reserved name'

        templates = os.path.join(dirpath, common.TEMPLATES_DIR)
        assert not os.path.exists(templates) or os.path.isdir(
            templates,
        ), 'templates is a reserved name'

        assert (
            common.TEMPLATES_DIR not in dirnames or dirpath in namespace_paths
        ), 'templates/ dirs must reside directly in namespace dirs only'

    for env in common.ENV_DIRS:
        env_path = os.path.join(common.CHECKS_DIR_PATH, env)
        if os.path.exists(env_path):
            assert os.path.isdir(env_path)
            assert set(common.list_dir_files(env_path)).issubset(
                {common.DEFAULT_YAML},
            ), 'no checkfile can reside in environment directory'
