# coding: utf-8

import os
import time

from sandbox.common import fs as common_fs
from sandbox.common.types import client as ctc
from sandbox import sdk2


HOST = 'localhost'


def _create_task(task_manager,
                 type='UNIT_TEST', status=None, owner=None, author=None,
                 parent_id=None, host=None, hidden=False,
                 arch=None, model=None, cores=None,
                 priority=None, parameters=None, context=None):
    if host is None:
        host = "host"
    if not author:
        author = "unspecified-author"
    if not owner:
        owner = author
    task = task_manager.create(
        task_type=type, owner=owner, author=author, parent_id=parent_id,
        host=host, model=model, cores=cores, arch=arch,
        priority=priority, parameters=parameters, context=context
    )
    if status:
        task.set_status(status, force=True)
    if hidden:
        task.hidden = 1
    task_manager.update(task)
    return task


def _create_resource(
    task_manager, parameters=None, mark_ready=True, task=None, make_dir=False, create_logs=True,
    resource_type='TEST_TASK_RESOURCE', content=None
):
    """
        Create a resource object via task manager.
        You can change default fields with 'parameters' parameter.
        'parameters' is a dict, its correct key values:
             resource_desc
             resource_filename
             resource_type
             complete
             arch
    """
    if not task:
        task = _create_task(task_manager, 'UNIT_TEST', owner=(parameters or {}).get('owner'), host=HOST)
    twd = common_fs.create_task_dir(task.id)
    if create_logs:
        log_dir = 'log' + str(len(task.list_resources('TASK_LOGS')) + 1)
        os.mkdir(os.path.join(twd, log_dir))
        task._log_resource = task._create_resource('Task logs', log_dir, 'TASK_LOGS')
    default_parameters = {
        'resource_desc': 'unit test resource description',
        'resource_filename': 'unit_test_resource',
        'resource_type': resource_type,
    }
    if parameters:
        default_parameters.update(parameters)
    default_parameters["resource_type"] = sdk2.Resource[str(default_parameters["resource_type"])]
    resource = task._create_resource(**default_parameters)
    if make_dir:
        os.makedirs(resource.abs_path())
        if content is not None:
            with open(os.path.join(resource.abs_path(), "file"), "w") as f:
                f.write(content)
    else:
        with open(resource.abs_path(), "w") as f:
            f.write(content or "")
    if mark_ready:
        resource.mark_ready()
    return resource


def _create_resources(task_manager, count, fake=False):
    result = []
    for i in range(count):
        if fake:
            resource = _create_fake_resource()
        else:
            resource = _create_real_resource(task_manager)
        result.append(resource)
    return result


def _create_real_resource(task_manager, parameters=None, mark_ready=True, task=None, make_dir=False, content=None):
    """
        Create a real Sandbox resource via manager
    """
    return _create_resource(task_manager, parameters, mark_ready, task=task, make_dir=make_dir, content=content)


def _create_fake_resource(parameters=None):
    """
        Create a fake resource object.
        You can change default fields with 'parameters' parameter.
        'parameters' is a dict, its correct key values:
            'resource_id'
            'name'
            'file_name'
            'file_md5'
            'resource_type'
            'task_id'
    """
    from yasandbox.proxy import resource as resource_proxy
    default_resource_parameters = {
        'resource_id': 1,
        'name': 'resource name',
        'file_name': 'resource',
        'file_md5': '',
        'resource_type': 'TEST_TASK_RESOURCE',
        'task_id': 1,
        'owner': 'unittester'
    }
    if parameters:
        default_resource_parameters.update(parameters)
    res = resource_proxy.Resource(**default_resource_parameters)
    return res


def _create_task_with_resources(task_manager, count=5, types=None):
    types = types or ['TEST_TASK_RESOURCE']
    if isinstance(types, str):
        types = [types]
    task = _create_task(task_manager)
    types_count = len(types)
    for i in range(count):
        resource_type = types[i % types_count]
        task._create_resource(resource_desc='test_list_task_resources',
                              resource_filename='test_list_task_resources{}'.format(i),
                              resource_type=resource_type,
                              complete=0,
                              arch='any')
    return task


def _create_client(client_manager, host='host_1', arch='freebsd', ncpu=4, ram=64000, model='e5-2660',
                   freespace=500000, alive=True, platform='test_platform', lxc=False, tags=None):
    client = client_manager.load(host, create=True)
    client.arch = arch
    client.ncpu = ncpu
    client.ram = ram
    client.model = model
    client.freespace = freespace
    client.info = {'system': {'platform': platform, 'lxc': lxc}}
    client.update_tags(tags or (ctc.Tag.GENERIC, ), client.TagsOp.SET)
    if alive:
        client.update_ts = time.time()
    client_manager.update(client)
    return client


def _get_current_host_name():
    from common import config
    return config.Registry().this.id
