import json
import os
import uuid

import click
import requests
import vh
from dict.mt.libs.python.utils import params

GRAPH_LABEL = 'Test ML package'
NIRVANA_QUOTA = 'mt-video'
DATA_TTL = 30
NIRVANA_API_BASE = 'https://nirvana.yandex-team.ru'

DOWNLOAD_RESOURCE_ID = '59fe50c4-f293-4c2b-acf1-ff0c703d3f50'

# https://nirvana.yandex-team.ru/layer/d94491af-e6af-4263-98b0-880988711d0a
JOB_LAYER_ID = 'd94491af-e6af-4263-98b0-880988711d0a'
PARENT_LAYER_ID = 'dcaef0d2-fd8e-4986-84cc-4c34a0fcd88c'
CONTAINER = vh.Porto([vh.data_from_str(JOB_LAYER_ID, data_type='binary', name='job_layer_id'),
                      vh.data_from_str(PARENT_LAYER_ID, data_type='binary', name='parent_layer_id')])


class ResourceDef(click.ParamType):
    name = 'resource'

    def convert(self, value, param, ctx):
        if isinstance(value, tuple):
            return value

        if '=' not in value:
            self.fail('Wrong definition: {}'.format(value))

        res_id, dest_path = value.split('=', 1)
        try:
            res_id = int(res_id)
        except ValueError:
            self.fail('Invalid resource ID format: {}'.format(res_id))

        return str(res_id), dest_path


@click.group()
def main():
    pass


@main.command()
@click.option('--code-package')
@click.option('--code-package-res-id')
@click.option('--test-command', required=True)
@click.option('--graph-id-result', required=True, type=click.File('w'))
@click.option('--config')
@click.option('--resource', multiple=True, type=ResourceDef())
@click.option('--nirvana-token-file', default='~/.tokens/nirvana', show_default=True)
@click.option('--test-env')
@click.option('--requirements-txt')
@click.option('--setup-requires-txt')
@click.option('--target-workflow')
def start(
    code_package, code_package_res_id, test_command, graph_id_result, config, resource,
    nirvana_token_file, test_env, requirements_txt, setup_requires_txt, target_workflow,
):
    nirvana_token = params.get_secret_value('NIRVANA_TOKEN', nirvana_token_file)
    if (code_package is None) == (code_package_res_id is None):
        raise ValueError('Eigther code package file or resource id should be specified at the same time')
    if code_package_res_id:
        code_package_data = vh.op(id='dae074c4-bcef-48fc-92f6-bb41f49f997b')(
            sky_id='sbr:' + code_package_res_id,
            _options={'max-tmpfs-disk': 10240}
        ).output
    else:
        with open(code_package, 'rb') as fp:
            code_package_data = vh.data_from_str(fp.read(), name='package.tar.gz')

    test_op_deps = []
    actions = []
    for idx, resource_item in enumerate(resource):
        res_id, dest_path = resource_item

        resource_data = vh.op(id=DOWNLOAD_RESOURCE_ID)(
            _name=f'Get {dest_path}',
            resource_id=res_id,
            do_pack=True,
            max_ram=256,
            max_disk=8192,
        )
        test_op_deps.append(resource_data)

        actions.extend((
            f'mkdir "{dest_path}"',
            'tar -xf {{ IN[%s] }} -C "%s"' % (idx, dest_path),
            f'export PATH="$(pwd)/{dest_path}:$PATH"',
            f'export PYTHONPATH="$(pwd)/{dest_path}:$PYTHONPATH"',
        ))

    if config:
        config_name = os.path.basename(config)
        with open(config, 'rb') as fp:
            config_data = vh.data_from_str(fp.read(), name='config.yaml')

        test_op_deps.append(config_data)
        actions.append(f'config_name="{config_name}"')

    if test_env:
        for env_def in test_env.split(' '):
            actions.append(f'export {env_def}')

    if requirements_txt:
        with open(requirements_txt, 'rb') as fp:
            requirements_txt_data = vh.data_from_str(fp.read(), name='requirements.txt')

        if setup_requires_txt:
            with open(setup_requires_txt, 'rb') as fp:
                setup_requires_txt_data = vh.data_from_str(fp.read(), name='setup_requires.txt')
        else:
            setup_requires_txt_data = vh.data_from_str("", name='setup_requires.txt')


        # noinspection PyProtectedMember
        with vh._uop_options({'job-use-dns64': True}):
            venv_data = vh.tgt(
                'venv', requirements_txt_data, setup_requires_txt_data,
                recipe="""
                set -x
                /usr/local/bin/python3.9 -m venv --copies py_venv
                ./py_venv/bin/python -m pip install -U pip==21.2.4 --index-url https://pypi.yandex-team.ru/simple/
                ./py_venv/bin/python -m pip install -r "{{ setup_requires_txt_data }}"
                ./py_venv/bin/python -m pip install -r "{{ requirements_txt_data }}"
                tar -czf "{{ OUT[0] }}" ./py_venv
                """,
                container=CONTAINER,
                hardware_params=vh.HardwareParams(
                    max_ram=1024,
                    max_disk=16384,
                ),
            )

        test_op_deps.append(venv_data)
        actions.extend((
            'tar -xzf "{{ venv_data }}"',
            'source ./py_venv/bin/activate',
        ))

    test_op_deps.append(code_package_data)

    # noinspection PyProtectedMember
    with vh._uop_options({'restrict-gpu-type': True}):
        vh.tgt(
            'test', *test_op_deps,
            recipe="""
            set -x
            config_name=
            %s

            if [[ -n "$config_name" ]]; then
                cp "{{ config_data }}" "$config_name"
            fi

            tar -xzf "{{ code_package_data }}"

            %s
            echo OK > "{{ OUT[0] }}"
            """ % ('\n'.join(actions), test_command),
            container=CONTAINER,
            hardware_params=vh.HardwareParams(
                cpu_guarantee=220,
                max_ram=10240,
                max_disk=64000,
                gpu_type=vh.GPUType.CUDA_7_0,
                gpu_count=2,
                gpu_max_ram=29000,
            ),
        )

    keeper = vh.run(
        label=GRAPH_LABEL,
        quota=NIRVANA_QUOTA,
        oauth_token=nirvana_token,
        workflow_ttl=DATA_TTL,
        data_ttl=DATA_TTL,
        workflow_guid=target_workflow,
        start=True,
    )

    wf_info = keeper.get_workflow_info()
    json.dump({
        'workflow_id': wf_info.workflow_id,
        'workflow_instance_id': wf_info.workflow_instance_id,
    }, graph_id_result)


@main.command()
@click.option('--nirvana-token-file', default='~/.tokens/nirvana', show_default=True)
@click.option('--graph-id-result', required=True, type=click.File('r'))
def get_result(nirvana_token_file, graph_id_result):
    nirvana_token = params.get_secret_value('NIRVANA_TOKEN', nirvana_token_file)
    graph_ids = json.load(graph_id_result)

    exec_state = make_nirvana_api_request(nirvana_token, 'getExecutionState', params={
        'workflowId': graph_ids['workflow_id'],
        'workflowInstanceId': graph_ids['workflow_instance_id'],
    })

    result = {name: exec_state[name] for name in ('status', 'result', 'progress')}
    if exec_state['status'] != 'completed':
        print(json.dumps(result))
        return

    block_logs_data = make_nirvana_api_request(nirvana_token, 'getBlockLogs', params={
        'workflowId': graph_ids['workflow_id'],
        'workflowInstanceId': graph_ids['workflow_instance_id'],
        'blocks': [{'code': 'RunScript_2'}],
        'logNames': ['stdout.log', 'stderr.log'],
    })

    logs = {}
    for block_data in block_logs_data:
        for log_data in block_data['logs']:
            logs[log_data['logName']] = make_nirvana_http_request(nirvana_token, log_data['storagePath'])
    result.update(logs)

    print(json.dumps(result))


def make_nirvana_api_request(nirvana_token, api_method, params=None):
    resp = requests.post(
        '{}/api/public/v1/{}'.format(NIRVANA_API_BASE, api_method),
        headers={'Authorization': 'OAuth {}'.format(nirvana_token)},
        json={'jsonrpc': '2.0', 'method': api_method, 'params': params, 'id': str(uuid.uuid4())},
    )

    resp.raise_for_status()
    resp_json = resp.json()
    if 'error' in resp_json:
        raise RuntimeError('Nirvana error: {}'.format(resp_json['error']))
    return resp_json['result']


def make_nirvana_http_request(nirvana_token, url, http_method='GET'):
    resp = requests.request(
        http_method, url,
        headers={'Authorization': 'OAuth {}'.format(nirvana_token)},
    )
    resp.raise_for_status()
    return resp.text
