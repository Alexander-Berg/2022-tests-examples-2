import json

import pytest

from taxi_buildagent.clients import sandbox as sandbox_module


class Sandbox:
    def __init__(self, patch_requests, load_binary):
        self.patch_requests = patch_requests
        self.load_binary = load_binary
        self.task_id = 123456789
        self.resources = []
        self.task_revision = '666666666'
        self.task_resources = None
        self.task_context = None
        self.task = None
        self.task_create = None
        self.batch_tasks_start = None
        self.resource = None
        self.download_resource = None

    def append_resource(
            self,
            type_,
            id_,
            name=None,
            package=None,
            task_id=None,
            state='READY',
            version=None,
    ):
        resource = {'type': type_, 'id': id_, 'state': state}
        if name is not None:
            resource.setdefault('attributes', {})['resource_name'] = name
        if version is not None:
            resource.setdefault('attributes', {})['version'] = version
        if package is not None:
            resource['package'] = package
        if task_id is not None:
            resource['task'] = {'id': task_id}
        self.resources.append(resource)

    def patch_all(self):
        @self.patch_requests(
            sandbox_module.API_URL + f'task/{self.task_id}/resources',
        )
        def task_resources(method, url, **kwargs):
            return self.patch_requests.response(
                status_code=200, json={'items': self.resources},
            )

        @self.patch_requests(
            sandbox_module.API_URL + f'task/{self.task_id}/context',
        )
        def task_context(method, url, **kwargs):
            return self.patch_requests.response(
                status_code=200, json={'revision': self.task_revision},
            )

        @self.patch_requests(sandbox_module.API_URL + f'task/{self.task_id}')
        def task(method, url, **kwargs):
            return self.patch_requests.response(
                status_code=200,
                json={'status': 'SUCCESS', 'id': self.task_id, 'type': 'TYPE'},
            )

        @self.patch_requests(sandbox_module.API_URL + 'task')
        def task_create(method, url, **kwargs):
            task_type = kwargs['json']['type']
            if task_type == 'INCORRECT_TASK':
                err_json = {
                    'reason': 'Incorrect task type u\'INCORRECT_TASK\'',
                }
                return self.patch_requests.response(
                    status_code=400, json=err_json, text=json.dumps(err_json),
                )
            return self.patch_requests.response(
                status_code=201, json={'id': self.task_id},
            )

        @self.patch_requests(sandbox_module.API_URL + 'batch/tasks/start')
        def batch_tasks_start(method, url, **kwargs):
            return self.patch_requests.response(
                status_code=200, json=[{'status': 'SUCCESS'}],
            )

        @self.patch_requests(sandbox_module.API_URL + 'resource')
        def resource(method, url, **kwargs):
            if '/attribute/' in url:
                return self.patch_requests.response(status_code=204)
            splitted_url = url.split('/')
            if splitted_url[-2] == 'resource' and splitted_url[-1].isnumeric:
                id_ = splitted_url[-1]
                for res in self.resources:
                    if str(res['id']) == id_:
                        return self.patch_requests.response(
                            status_code=200, json={'type': res['type']},
                        )

            found_resources = []
            resource_type = kwargs.get('params', {}).get('type')
            for resource in self.resources:
                if resource.get('type') == resource_type:
                    found_resources.append(resource)
            return self.patch_requests.response(
                status_code=200, json={'items': found_resources},
            )

        @self.patch_requests(sandbox_module.PROXY_URL)
        def download_resource(method, url, **kwargs):
            res_id = int(url.rsplit('/', maxsplit=1)[-1])
            for resource in self.resources:
                if resource['id'] == res_id:
                    return self.patch_requests.response(
                        status_code=200,
                        content=self.load_binary(resource['package']),
                    )
            err_json = {
                'error': 'Not Found',
                'reason': f'Resource #{res_id} not found.',
            }
            return self.patch_requests.response(
                status_code=404, json=err_json, text=json.dumps(err_json),
            )

        self.task_resources = task_resources
        self.task_context = task_context
        self.task = task
        self.task_create = task_create
        self.batch_tasks_start = batch_tasks_start
        self.resource = resource
        self.download_resource = download_resource


@pytest.fixture
def sandbox(monkeypatch, patch_requests, load_binary):
    monkeypatch.setenv('SANDBOX_TOKEN', 'sandbox-token')
    return Sandbox(patch_requests, load_binary)
