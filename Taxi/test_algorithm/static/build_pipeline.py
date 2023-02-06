#!python3

import json
import os
import re


TPL_FNAME = 'tpl_surge_pipeline.json'
RES_FNAME = 'default/surge_pipeline.json'

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TPL_PATH = os.path.join(DIR_PATH, TPL_FNAME)
RES_PATH = os.path.join(DIR_PATH, RES_FNAME)


def walk_stages(stages, on_stage):
    for maybe_stage in stages:
        if 'stages' in maybe_stage:
            walk_stages(maybe_stage['stages'], on_stage)
        else:
            on_stage(maybe_stage)


def fill_source_code(stage):
    source_code = stage['source_code']
    filename_match = re.search(r'^<(\w+\.js)>$', source_code)
    if filename_match:
        source_path = os.path.join(DIR_PATH, filename_match.group(1))
        source_code = open(source_path, 'r').read()
        source_code, _, _ = re.sub(
            r'.*?function.*?{', '', source_code, flags=re.DOTALL, count=1,
        ).rpartition('}')

    stage['source_code'] = source_code


def flatten_in_bindings(stage):
    def walk_in_binding(
            node: dict, in_binding: dict, flat_query: str, out: list,
    ):
        if flat_query:
            flat_query += '.'
        flat_query += node['query']
        children = node.get('children')
        if children:
            for child in children:
                walk_in_binding(child, in_binding, flat_query, out)
        else:
            if out and '*' in flat_query:
                raise Exception(
                    f'Flattening will produce iteration multiplication: '
                    f'at stage "{stage["name"]}"',
                )
            flat_in_binding = in_binding.copy()
            flat_in_binding['query'] = flat_query
            if 'children' in flat_in_binding:
                del flat_in_binding['children']
            out.append(flat_in_binding)

    flat_in_bindings = []

    for in_binding in stage['in_bindings']:
        local_flat_in_bindings = []
        walk_in_binding(in_binding, in_binding, '', local_flat_in_bindings)
        flat_in_bindings.extend(local_flat_in_bindings)

    stage['in_bindings'] = flat_in_bindings


def convert_stage(stage):
    flatten_in_bindings(stage)
    fill_source_code(stage)


def main():
    pipeline = json.load(open(TPL_PATH, 'r'))
    walk_stages(pipeline['stages'], on_stage=convert_stage)

    fp = open(RES_PATH, 'w')
    json.dump(pipeline, fp, indent=2, ensure_ascii=False)
    fp.write('\n')


if __name__ == '__main__':
    main()
