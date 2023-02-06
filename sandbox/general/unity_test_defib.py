#!/usr/bin/env python
# coding: utf-8

"""
Defibrillator - emergency assistance your Unity test!
Shock!
"""

import os
import sys
import abc
import pwd
import json
import shutil
import tarfile
import argparse
import textwrap
import datetime as dt

import api.copier


def first(iterable):
    return next(iter(iterable), None)


class FakeUserPrivileges(object):
    def __init__(self, user=None):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TaskDeployer(object):
    def __init__(self, skynet_id, fname, user):
        self.skynet_id = skynet_id
        self.fname = fname
        self.osUser = user

    def __call__(self):
        uname = pwd.getpwuid(os.geteuid()).pw_name
        if uname == 'zomb-sandbox':
            UserPrivileges = FakeUserPrivileges
        else:
            import kernel.util.sys.user
            UserPrivileges = kernel.util.sys.user.UserPrivileges

            assert os.getuid() == 0, 'Must be user zomb-sandbox or root ({})'.format(uname)

        with UserPrivileges('zomb-sandbox'):
            pkg_dir = '/samogon/1/active/user/server_launcher/srvdata/packages'

            if not os.path.exists(pkg_dir):
                raise ValueError('Path "{}" does not exist'.format(pkg_dir))

            # FIXME: fail with: AttributeError: 'NoneType' object has no attribute 'path_importer_cache'
            # copier = api.copier.Copier()
            # h = copier.get(self.skynet_id, dest=pkg_dir, user=True)
            # h.wait()

            # temporary crutch, because thruth API does not work
            import subprocess as sp
            sp.check_call(['sky', 'get', '-u', '-w', '-d', pkg_dir, self.skynet_id, ])

            full_path = os.path.join(pkg_dir, self.fname)

            if not os.path.exists(full_path):
                raise ValueError('Downloaded file "{}" does not exist'.format(pkg_dir))

            tasks_dir = os.path.join(pkg_dir, 'tasks')

            if os.path.islink(tasks_dir):
                os.remove(tasks_dir)

            if os.path.exists(tasks_dir):
                shutil.rmtree(tasks_dir)

            tmp_dir = tasks_dir + '~'
            with tarfile.open(full_path) as tar:
                tar.extractall(tmp_dir)

            os.rename(tmp_dir, tasks_dir)
            os.unlink(full_path)


class Env(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def mongo_hosts(self):
        pass

    @abc.abstractproperty
    def mongo_db_name(self):
        pass

    mongo_port = 22222

    def resolve_mongo_hosts(self):
        host_resolver = library.sky.hostresolver.Resolver()
        return host_resolver.resolveHosts(self.mongo_hosts)

    @property
    def mongo_uri(self):
        return 'mongodb://{}'.format(
            ','.join('{}:{}'.format(h, self.mongo_port) for h in self.resolve_mongo_hosts())
        )

    def __init__(self):
        hosts = self.resolve_mongo_hosts()
        hosts_count = len(hosts)
        if hosts_count == 0:
            raise ValueError('No mongo hosts')

        self.conn = pymongo.MongoClient(self.mongo_uri)
        self.db = self.conn[self.mongo_db_name]

    @property
    def service_UpdateSandboxResources(self):
        col = self.db['service']
        return first(col.find({'_id': 'UpdateSandboxResources'}))

    @service_UpdateSandboxResources.setter
    def service_UpdateSandboxResources(self, value):
        col = self.db['service']
        col.update({'_id': 'UpdateSandboxResources'}, {'$set': {'context': value}})

    def most_recent_task_resource(self):
        col = self.db['resource']
        return first(col.find({
            'type': 'SANDBOX_TASKS_ARCHIVE',
            'state': 'READY',
            'attrs': {'$elemMatch': {'k': 'auto_deploy'}}
        }).sort('-id').limit(1))


class UnityTest(Env):
    mongo_hosts = 'k@sandbox1_mongo'
    mongo_db_name = 'sandbox_restored'

    def create_most_recent_task_resource(self, data):
        yasandbox.database.me.connect(
            self.mongo_db_name,
            host=self.mongo_uri,
            port=self.mongo_port,
        )

        # Create fake task
        task = yasandbox.proxy.task.Task()
        task.type = 'TEST_TASK'
        task.status = yasandbox.proxy.task.Task.Status.SUCCESS
        task.descr = 'Defibrillator: import tasks'
        task.author = 'zomb-sandbox'
        task.owner = 'SANDBOX'

        task.save()

        yasandbox.database.mapping.Audit(
            task_id=task.id,
            content='Created by Defibrillator{}'.format(unichr(0x2122).encode('utf8')),
            status=task.status,
            author=task.author,
            source=None
        ).save()

        res = yasandbox.database.mapping.Resource()
        res.type = data['type']
        res.name = data['description']
        res.path = data['file_name']
        res.owner = data['owner']
        res.task_id = yasandbox.database.mapping.ObjectId(task.id)
        res.arch = data['arch']  # data['']
        res.time = yasandbox.database.mapping.Resource.Time()
        res.time.created = dt.datetime.utcnow()
        res.time.accessed = dt.datetime.utcnow()
        # Mean: ttl = 'inf'
        res.time.expires = None
        res.state = data['state']
        res.size = data['size']
        res.md5 = data['md5']
        res.skynet_id = data['skynet_id']
        attrs = data['attributes']
        attrs['ttl'] = 'inf'
        res.attributes = [
            yasandbox.database.mapping.Resource.Attribute(key=str(k), value=str(v))
            for k, v in attrs.iteritems()
        ]

        for src in data['sources']:
            res.hosts_states.append(
                yasandbox.database.mapping.Resource.HostState(
                    host=src,
                    state=yasandbox.database.mapping.Resource.HostState.State.OK
                )
            )

        res.save()

        print 'Created task: {} resource: {}'.format(task.id, res.id)


def confirm(question, color_func=None):
    question = '{} ([y]/n): '.format(question)

    if color_func:
        question = color_func(question)

    answer = None
    while answer not in ('', 'y', 'n'):
        answer = raw_input(question).strip()

    return answer in ('', 'y')


def main(args):
    cz = common.console.AnsiColorizer()

    resolver = library.sky.hostresolver.Resolver()
    hosts = resolver.resolveHosts(args.hosts)

    hosts_set = frozenset(hosts)
    standard_ut_hosts = frozenset(resolver.resolveHosts('k@sandbox1_server'))

    unnecessary = hosts_set - standard_ut_hosts
    if unnecessary:
        print cz.red('Forbiddent hosts: "{}"'.format(', '.join(unnecessary)))
        return -2

    if args.cquser not in ('zomb-sandbox', 'root'):
        if not confirm('You must connect to servers as `zomb-sandbox` or `root`. Do you want to continue?', cz.red):
            return

    prod_rest = common.rest.Client('https://sandbox.yandex-team.ru/api/v1.0')

    # === Find most recent tasks ===

    params = {
        'limit': 1,
        'type': 'SANDBOX_TASKS_ARCHIVE',
        'state': 'READY',
        'owner': 'SANDBOX',
        'attrs': json.dumps({
            'auto_deploy': 'True',
        })
    }

    with common.console.LongOperation('Search recent resource with tasks archive...'):
        last_task_res = prod_rest.resource.read(params)

    items = last_task_res['items']
    if len(items) != 1:
        print 'No tasks found! Exit'
        return

    res_info = prod_rest.resource[items[0]['id']].read()
    print 'Found resource #{} {}'.format(res_info['id'], cz.blue(res_info['url']))

    skynet_id = res_info['skynet_id']
    fname = res_info['file_name']

    # === Deploy tasks on server hosts ===
    user_name = args.cquser
    failed_hosts = []
    with api.cqueue.Client(implementation='cqudp') as client:
        with client.run(hosts, TaskDeployer(skynet_id, fname, user_name)) as session:
            timeout = 10
            with common.console.LongOperation('Upload tasks on {} hosts. Wait {} secs'.format(len(hosts), timeout)):
                print
                for host, result, err in session.wait(timeout):
                    if not err:
                        print '\thost {} {}'.format(host, cz.green('ready')), result
                    else:
                        print '\t{} on host {}: {}'.format(cz.red('error'), host, err)
                        failed_hosts.append(host)

    if failed_hosts:
        if not confirm('There are failed jobs. Do you want to continue?', cz.red):
            return

    ut = UnityTest()

    # === Create in mongo last task resource ===
    ut.create_most_recent_task_resource(res_info)
    print cz.green('Create fake resource with last tasks code')

    # === Null Service ===
    ut.service_UpdateSandboxResources = {}
    print cz.green('Clear service thread "UpdateSandboxResources" context')

    print cz.green('Successfully complete')
    return 0


if __name__ == '__main__':
    if '__DEFIBRILLATOR' not in os.environ:
        print 'Try find true python to run script'

        # First of all, add source root to system's libraries lookup path.
        abspath = os.path.abspath(__file__)
        root = os.path.dirname(os.path.dirname(abspath))
        sys.path.insert(0, root)
        sys.path.insert(0, '/skynet')

        executable = os.path.join(os.path.expanduser('~zomb-sandbox'), 'venv', 'bin', 'python')

        print 'Try run "{}"'.format(executable)

        env = os.environ.copy()
        env['PYTHONPATH'] = '/skynet:{0}'.format(root)
        env['__DEFIBRILLATOR'] = ''
        cmd = [executable, abspath] + sys.argv[1:]

        os.execve(executable, cmd, env)

    import common.rest
    import common.utils
    import common.console
    import common.types.task

    import api.cqueue
    import library.sky.hostresolver

    import pymongo

    import yasandbox.proxy.task
    import yasandbox.proxy.resource
    import yasandbox.database.mapping
    yasandbox.database.mapping.disconnect()

    class Formatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
        Unity test Defibrilator.

            `robot-sandboxdev` on sandbox-server01 have root access to Unity test.
        """),
        formatter_class=Formatter
    )
    parser.add_argument(
        '--hosts',
        default='k@sandbox1_server',
        help='conductor group/tag for servers'
    )
    parser.add_argument(
        '--cquser',
        default=pwd.getpwuid(os.geteuid()).pw_name,
        help='user for CQueue. Should be zomb-sandbox or root'
    )
    parser.add_argument(
        '--mongodb-hosts',
        default='k@sandbox_test_mongo',
        help='conductor group/tag for mongodb'
    )

    args = parser.parse_args()

    # Suppress warnings from requests and cqueue
    import warnings
    warnings.filterwarnings("ignore")

    rcode = main(args)
    sys.exit(rcode if isinstance(rcode, int) else -1)
