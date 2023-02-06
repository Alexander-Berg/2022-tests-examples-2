import copy
import os

import yaml


DESCRIPTION_KEY_PATH = ['description']
REQUEST_PATH = ['parameters', 'body', 'schema']
RESPONSE_PATH = ['responses', '200', 'schema']

INDENT = ' ' * 4

SERVICES_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)


def test_docs_generation():
    for component in _get_doc_components():
        source_dir = _get_source_dir(component)
        if source_dir:
            _generate_md_files(component, source_dir)


def _get_doc_components():
    doc_components = os.listdir(SERVICES_DIR)
    doc_components.sort()
    return doc_components


def _get_source_dir(component):
    main_path_part = os.path.join(SERVICES_DIR, component)

    doc_dir = os.path.join(main_path_part, 'doc')
    docs_dir = os.path.join(main_path_part, 'docs')

    source_dir = None
    if os.path.exists(docs_dir):
        source_dir = docs_dir
    elif os.path.exists(docs_dir):
        source_dir = doc_dir

    return source_dir


def _generate_md_files(component, docs_dir):
    yaml_files = _get_yaml_files(docs_dir)

    path_data_dict = {}
    for filepath in yaml_files:
        docs_file_path = _get_docs_file_path(filepath, docs_dir)

        if filepath.endswith('definitions.yaml'):
            definitions = _get_definitions_md(filepath)
            if definitions:
                path_data_dict[docs_file_path] = definitions
            continue

        header_template = (
            '#[{component}](.{deep}/Index/#{component}) > {path_tokens}\n'
        )
        deep = '/..' * (len(docs_file_path.split('/')) + 1)
        header = header_template.format(
            component=component,
            deep=deep,
            path_tokens=os.path.splitext(docs_file_path.replace('/', ' > '))[
                0
            ],
        )
        doc_text = _process_yaml(filepath=filepath, yaml_files=yaml_files)
        if doc_text:
            path_data_dict[docs_file_path] = header + doc_text

    return path_data_dict


def _get_docs_file_path(filepath, docs_dir):
    path = filepath.replace('/yaml/', '/')
    path = os.path.relpath(os.path.splitext(path)[0], docs_dir)
    return '{}.md'.format(path)


def _process_yaml(filepath, yaml_files):
    text_lines = []

    yaml_doc = _load_yaml(filepath)
    formatted_doc = _get_formatted_yaml_doc(yaml_doc)
    final_doc = _expand_ref_links(formatted_doc, yaml_files)

    paths = _get_doc_elem(['paths'], final_doc)
    if not paths:
        return None

    for path, value in sorted(paths.items()):
        text_lines.append(_create_path_doc(path, value))

    return '\n'.join(text_lines)


def _get_formatted_yaml_doc(yaml_doc):
    """Convert int doc keys to str (200 to '200')."""
    yaml_doc = copy.deepcopy(yaml_doc)
    if isinstance(yaml_doc, dict):
        new_yaml_doc = {}
        for key, value in yaml_doc.items():
            key = _get_formatted_key(key)
            new_yaml_doc[key] = _get_formatted_yaml_doc(value)
    elif isinstance(yaml_doc, list):
        new_yaml_doc = []
        for item in yaml_doc:
            new_yaml_doc.append(_get_formatted_yaml_doc(item))
    else:
        new_yaml_doc = yaml_doc

    return new_yaml_doc


def _get_formatted_key(key):
    if isinstance(key, int):
        key = str(key)
    return key


def _expand_ref_links(yaml_doc, yaml_files):
    _definitions_cache = {}
    _in_search = set()

    def _traverse_definitions(doc):
        if isinstance(doc, dict):
            new_doc = copy.deepcopy(doc)
            for key, value in sorted(doc.items(), key=str, reverse=False):
                if key == '$ref':
                    if 'definitions.yaml' in value:
                        continue

                    if value in _definitions_cache:
                        expanded = _definitions_cache[value]
                    else:
                        if value in _in_search:
                            continue
                        elif '.yaml' in value:
                            if '#' in value:
                                yaml_path, path_in = value.split('#')
                                path_in_yaml = path_in.strip('/').split('/')
                            else:
                                yaml_path = value
                                path_in_yaml = []

                            if yaml_path in _definitions_cache:
                                ref_yaml = _definitions_cache[yaml_path]
                            else:
                                ref_yaml = _get_ref_yaml(yaml_path, yaml_files)
                                _definitions_cache[yaml_path] = ref_yaml

                            expanded = _get_doc_elem(path_in_yaml, ref_yaml)
                            expanded = expanded if expanded else {}
                        else:
                            _in_search.add(value)
                            path_in_doc = value.lstrip('#/').split('/')
                            expanded = _get_doc_elem(path_in_doc, yaml_doc)
                            expanded = _traverse_definitions(expanded)
                            if not expanded:
                                print('Warning - wrong_ref_link %s' % value)
                            expanded = expanded if expanded else {}
                            _definitions_cache[value] = expanded

                    new_doc.update(expanded)
                    new_doc.pop(key, None)
                else:
                    new_doc[key] = _traverse_definitions(value)
            return new_doc
        elif isinstance(doc, list):
            return [_traverse_definitions(item) for item in doc]
        else:
            return doc

    result = _traverse_definitions(yaml_doc)
    return result


def _get_ref_yaml(yaml_path, yaml_files):
    if not yaml_files:
        return None
    ref_yamls = [path for path in yaml_files if yaml_path.strip('./') in path]

    if len(ref_yamls) == 1:
        ref_yaml = ref_yamls[0]

        yaml_doc = _load_yaml(ref_yaml)
        next_yaml_files = copy.deepcopy(yaml_files).remove(ref_yaml)
        final_doc = _expand_ref_links(yaml_doc, next_yaml_files)
        return final_doc
    return None


def _create_path_doc(path, value):
    path_text_lines = ['##%s\n' % path]
    request_types = list(value.keys())
    for request_type in request_types:
        descr_path = [request_type] + DESCRIPTION_KEY_PATH
        request_path = [request_type] + REQUEST_PATH
        response_path = [request_type] + RESPONSE_PATH

        desc = _get_doc_elem(descr_path, value)
        _add_description(desc, path_text_lines)
        _add_request_info(request_type, request_path, value, path_text_lines)
        _add_response_info(response_path, value, path_text_lines)
    return '\n'.join(path_text_lines)


def _add_description(desc, text_lines):
    if isinstance(desc, str):
        if not desc.endswith('\n'):
            desc += '\n'
        text_lines.append(desc)


def _add_request_info(request_type, request_path, value, text_lines):
    request_info = _get_info_if_present(doc=value, doc_path=request_path)
    if request_info:
        text_lines.append(
            '### Допустимые параметры запроса' ' (%s)\n' % request_type,
        )
        text_lines.append(request_info)


def _add_response_info(response_path, value, text_lines):
    response_info = _get_info_if_present(doc=value, doc_path=response_path)
    if response_info:
        text_lines.append('### Допустимые параметры ответа\n')
        text_lines.append(response_info)


def _get_info_if_present(doc, doc_path):
    info = _get_doc_elem(doc_path, doc)
    if info:
        return '%s\n' % _unwind(info)


def _get_definitions_md(filepath):
    md_lines = []
    definitions = _load_yaml(filepath)
    if 'definitions' in definitions:
        definitions = definitions['definitions']

    md_lines.append('## Дополнительные типы данных\n')
    for key, value in sorted(definitions.items()):
        md_lines.append('### %s' % key)
        md_lines.append(_format('', value, -1, False))
        md_lines.append('%s' % _unwind(value))

    return '\n'.join(md_lines)


def _form_description(str, level):
    if str is None:
        return '?'
    else:
        return (INDENT * level).join(str.splitlines(True))


def _format(key, value, level, required):
    types = []

    if isinstance(value, str):
        value = {'description': value}
    elif 'type' in value:
        # Account for possible list types like ["string", "null"]
        types.append(str(value['type']))

    for variants in ['oneOf', 'anyOf', 'allOf']:
        for variant in value.get(variants, []):
            if 'type' in variant:
                types.append(str(variant['type']))

    if '$ref' in value:
        definitions_type = value['$ref'].replace('definitions.yaml', '')
        definitions_type = definitions_type.replace('#/definitions/', '')

        type_with_link = '<u><a href="../definitions/#%s">%s</a></u>' % (
            definitions_type,
            definitions_type,
        )
        types.append(type_with_link)

    list_item_tag = '*  ' if level > -1 else ''
    key_name = '__%s__' % key if key else ''
    key_required = (
        '<code style="color: Green">required</code>' if required else ''
    )
    key_type = '<code>type: %s</code>' % '/'.join(types) or '`type: Unknown`'

    one_of = '/'.join(map(str, value['enum'])) if 'enum' in value else ''

    key_format = '`format: %s`' % value['format'] if 'format' in value else ''
    key_re = '`re: %s`' % value['pattern'] if 'pattern' in value else ''
    min_length = (
        '`min-length: %i`' % value['minLength'] if 'minLength' in value else ''
    )
    description = _form_description(value.get('description'), level)

    return INDENT * level + '%s %s %s %s %s %s %s %s %s\n' % (
        list_item_tag,
        key_name,
        key_required,
        key_type,
        one_of,
        key_format,
        key_re,
        min_length,
        description,
    )


def _unwind(schema, level=0):
    description = ''

    alternatives = []

    if 'properties' in schema or 'patternProperties' in schema:
        alternatives.append(
            {
                'properties': schema.get('properties', {}),
                'patternProperties': schema.get('patternProperties', {}),
                'required': schema.get('required', []),
            },
        )
    for variants in ['oneOf', 'anyOf']:
        for variant in schema.get(variants, []):
            if 'properties' in variant or 'patternProperties' in variant:
                alternatives.append(
                    {
                        'properties': variant.get('properties', {}),
                        'patternProperties': variant.get(
                            'patternProperties', {},
                        ),
                        'required': variant.get('required', []),
                    },
                )

    for i, alt in enumerate(alternatives, start=1):
        deeper = 0
        if len(alternatives) > 1:
            description += '    ' * level + '*  Вариант %d\n' % i
            deeper = 1
        sorted_dict = sorted(
            alt['properties'].items(),
            key=lambda x: (x[0] not in alt['required'], x[0]),
        )
        for key, value in sorted_dict:
            if isinstance(value, str):
                description += _format(key, value, level + deeper, False)
                continue
            if key == 'required':
                continue
            description += _format(
                key, value, level + deeper, key in alt['required'],
            )
            description += _unwind(value, level + 1 + deeper)
        for key, value in sorted(alt['patternProperties'].items()):
            description += _format(key, value, level + deeper, False)
            description += _unwind(value, level + 1 + deeper)

    if isinstance(schema.get('items'), dict):
        description += _unwind(schema['items'], level)

    return description


def _get_yaml_files(docs_dir):
    yaml_files = []
    for root, subdirs, files in os.walk(docs_dir):
        for filename in files:
            if filename.endswith('.yaml'):
                yaml_files.append(os.path.join(root, filename))

    return yaml_files


def _get_doc_elem(path_in_doc, doc):
    if not path_in_doc:
        return doc
    sub_doc, attempt = _try_get_sub_node(path_in_doc, doc)
    if sub_doc is None:
        return None

    return _get_doc_elem(path_in_doc[attempt:], sub_doc)


def _try_get_sub_node(path_in_doc, doc):
    for attempt in range(1, len(path_in_doc) + 1):
        base_options = '/'.join(path_in_doc[0:attempt])

        path_options = [base_options]
        path_options.append('/{}'.format(base_options))
        path_options.append('{}/'.format(base_options))
        path_options.append('/{}/'.format(base_options))

        for path_option in path_options:
            value = None
            if isinstance(doc, dict):
                value = doc.get(path_option, None)
            elif isinstance(doc, list):
                item = [
                    i
                    for i in doc
                    if isinstance(i, dict) and i.get('name') == path_option
                ]
                if len(item) == 1:
                    value = item[0]

            if value is None:
                continue
            else:
                return value, attempt

    return None, None


def _load_yaml(path):
    with open(path, 'r', encoding='utf-8') as fin:
        yaml_doc = yaml.load(fin)
        return yaml_doc
