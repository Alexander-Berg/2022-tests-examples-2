import glob
import os.path
import yaml


import pytest

from openapi_core import create_spec


def _all_yaml():
    docs = []
    for yf in glob.glob('doc/api/**/*.yaml', recursive=True):
        if 'models' in yf.split(os.sep):
            continue
        docs.append(yf)
    # TODO: перейти на свой валидатор или поменять саму спеку
    docs = set(docs)
    docs -= {'doc/api/admin/true_marks.yaml'}
    docs = list(docs)
    return docs

@pytest.mark.parametrize('api_yaml', _all_yaml())
def test_yaml(tap, api_yaml):
    with tap.plan(1, api_yaml):
        with tap.subtest(2, api_yaml) as tp:
            with open(api_yaml, 'r') as fh:
                spec_dict = yaml.load(fh, Loader=yaml.FullLoader)
                tp.ok(spec_dict, f'yaml прочитан: {api_yaml}')

                path = os.path.abspath(api_yaml)
                try:
                    spec = create_spec(spec_dict,
                                       spec_url=f'file://{path}')
                    tp.ok(spec, f'спецификация загружена {api_yaml}')
                except Exception as x:
                    tp.failed(f'спецификация загружена {api_yaml}')
                    tp.diag(f'{x}')
