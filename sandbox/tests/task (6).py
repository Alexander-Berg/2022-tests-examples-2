import time
import datetime as dt
import collections

import pytest

from sandbox import common
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc

from sandbox.yasandbox import manager
from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping
import sandbox.yasandbox.proxy.client as proxy_client
import sandbox.yasandbox.manager.tests as manager_tests
import sandbox.yasandbox.manager.tests.client as manager_tests_client


class TestTask(object):

    @pytest.mark.usefixtures("server")
    def test__open_execute_interval(self, client_manager, serviceq, task_manager, monkeypatch):
        client_names = ["client1", "client2"]
        clients = [client_manager.create(client_name) for client_name in client_names]
        clients[1].update_tags([ctc.Tag.GENERIC, ctc.Tag.HDD, ctc.Tag.LINUX_PRECISE], clients[1].TagsOp.SET)

        pool_name = "LINUX_GENERIC_HDD"
        serviceq.add_quota_pool(pool_name, list(map(str, [ctc.Tag.GENERIC, ctc.Tag.HDD, ctc.Tag.Group.LINUX])))
        monkeypatch.setattr(controller.task.TaskQueue, "qclient", serviceq)

        # No host specified
        task = task_manager.create("TEST_TASK", owner="user", author="user")
        controller.task.Task().set_status(
            mapping.Task.objects.with_id(task.id), ctt.Status.ASSIGNED, force=True
        )
        assert mapping.Task.objects.with_id(task.id).execution.intervals.execute[0].start
        assert mapping.Task.objects.with_id(task.id).execution.intervals.execute[0].pool is None
        # Host doesn't match any pool
        task = task_manager.create("TEST_TASK", owner="user", author="user")
        controller.task.Task().set_status(
            mapping.Task.objects.with_id(task.id), ctt.Status.ASSIGNED, force=True, host=client_names[0]
        )
        assert mapping.Task.objects.with_id(task.id).execution.intervals.execute[0].pool is None
        # Host match pool
        task = task_manager.create("TEST_TASK", owner="user", author="user")
        controller.task.Task().set_status(
            mapping.Task.objects.with_id(task.id), ctt.Status.ASSIGNED, force=True, host=client_names[1]
        )
        assert mapping.Task.objects.with_id(task.id).execution.intervals.execute[0].pool == pool_name

    def test__set_status(self):
        task = mapping.Task()
        task.host = "host"
        task.author = task.owner = "unspecified-author"
        task.type = "TEST_TASK_2"
        wrapper = controller.TaskWrapper(task)
        wrapper.create()

        status = ctt.Status.ENQUEUED
        controller.Task.set_status(task, status, force=True)
        task = mapping.Task.objects.with_id(task.id)
        assert task and task.execution.status == status and len(task.status_events) == 1, task
        events = mapping.TaskStatusEvent.objects(task_id=task.id)
        assert len(events) == 1
        event = events[0]
        assert str(event.id) == task.status_events[0]
        assert event.status == status
        assert event.created < dt.datetime.utcnow()

        status = ctt.Status.SUCCESS
        controller.Task.set_status(task, status, force=True)
        task = mapping.Task.objects.with_id(task.id)
        assert task and task.execution.status == status and len(task.status_events) == 2, task
        events = mapping.TaskStatusEvent.objects(task_id=task.id).order_by("created")
        assert len(events) == 2
        event = events[1]
        assert str(event.id) == task.status_events[1]
        assert event.status == status


class TestFilters(object):

    PRECISE_ALIAS = "linux_ubuntu_12.04_precise"

    LUCID_PLATFORMS = common.platform.PLATFORM_ALIASES["linux_ubuntu_10.04_lucid"]
    PRECISE_PLATFORMS = common.platform.PLATFORM_ALIASES[PRECISE_ALIAS]
    OSX_YOSEMITE_PLATFORMS = common.platform.PLATFORM_ALIASES["osx_10.10_yosemite"]

    @staticmethod
    def _create_test_client(ncpu=32, client_tags=None):
        client = proxy_client.Client(hostname="test_host", ncpu=ncpu)
        if client_tags:
            client._tags = set(map(str, ctc.Tag.filter(common.utils.chain(client_tags))))
        return client

    @staticmethod
    def _create_task():
        return controller.TaskWrapper(
            controller.Task.Model(requirements=controller.Task.Model.Requirements())
        )

    @classmethod
    def _check_clients(cls, method, task, client_params, expect=True):
        for kwargs in client_params:
            client_proxy = cls._create_test_client(**kwargs)
            client = client_proxy.mapping()
            client.tags = list(client_proxy._tags) if client_proxy._tags else []
            assert bool(method(task.model, client)) == expect, kwargs

    @classmethod
    def _check_client_parameter(cls, method, task, param_name, accept, not_accept):
        cls._check_clients(method, task, [{param_name: _} for _ in accept])
        cls._check_clients(method, task, [{param_name: _} for _ in not_accept], False)

    @pytest.mark.usefixtures("initialize")
    def test__platform_filter(self):
        task = self._create_task()

        task.model.requirements.platform = "lucid"
        task.model.requirements.client_tags = task.cls.client_tags
        self._check_client_parameter(
            controller.Task.check_platform_filter, task, "client_tags",
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_LUCID]],
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE], [ctc.Tag.GENERIC, ctc.Tag.OSX_YOSEMITE]]
        )

        task.model.requirements.platform = "precise"
        self._check_client_parameter(
            controller.Task.check_platform_filter, task, "client_tags",
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE]],
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_LUCID], [ctc.Tag.GENERIC, ctc.Tag.OSX_YOSEMITE]]
        )

        task.model.requirements.platform = "linux"
        self._check_client_parameter(
            controller.Task.check_platform_filter, task, "client_tags",
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE], [ctc.Tag.GENERIC, ctc.Tag.LINUX_LUCID]],
            [[ctc.Tag.GENERIC, ctc.Tag.OSX_YOSEMITE]]
        )

        task.model.requirements.platform = "osx"
        self._check_client_parameter(
            controller.Task.check_platform_filter, task, "client_tags",
            [[ctc.Tag.GENERIC, ctc.Tag.OSX_YOSEMITE]],
            [[ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE], [ctc.Tag.GENERIC, ctc.Tag.LINUX_LUCID]]
        )

    @pytest.mark.usefixtures("initialize")
    def test__cpu_filter(self):
        task = self._create_task()

        self._check_client_parameter(
            controller.Task.check_model_cpu_filter, task, "ncpu", range(1, 40, 2), []
        )

        task.model.requirements.cores = 10
        self._check_client_parameter(
            controller.Task.check_model_cpu_filter, task, "ncpu", [10, 15, 30], [1, 9]
        )

        task.model.requirements.cores = 32
        self._check_client_parameter(
            controller.Task.check_model_cpu_filter, task, "ncpu", [32, 33, 52], [1, 10, 31]
        )


class TestTaskQueue(object):

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__task_hosts_list_performance(self, client_manager, client_node_id, test_task_2, rest_session_login):
        tasks = []
        client = manager.client_manager.load(client_node_id)
        client_tags = (ctc.Tag.GENERIC, ctc.Tag.IPV4, ctc.Tag.LINUX_TRUSTY, ctc.Tag.LXC)
        client.update_tags(client_tags, client.TagsOp.SET)

        for i in xrange(1000):
            client._mapping = None
            client.hostname = "__tthc_{}".format(i)
            client.save()
            client.update_tags(client_tags, client.TagsOp.SET)

        print "Total clients:", mapping.Client.objects.count()

        task_params = {"owner": rest_session_login}
        for i in xrange(20):
            task = test_task_2(None, **task_params)
            task.Requirements.client_tags = manager_tests_client.TestClientManager.test_tags
            task.save()
            tasks.append(controller.TaskWrapper(controller.Task.get(task.id)))

        cache = controller.TaskQueue.HostsCache()

        # preload data from mongodb so that database calls don't affect performance
        start = time.time()
        for task in tasks:
            task._task()
        db_time = time.time() - start

        start = time.time()
        for task in tasks:
            controller.TaskQueue.task_hosts_list(task.model, cache=cache)
        total_time = time.time() - start
        print "Total:", total_time, "Avg:", total_time / len(tasks), "Db time:", db_time

        assert total_time < 8, total_time

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__task_hosts_list_with_cores(
        self, client_manager, task_manager, client_node_id, test_task_2, rest_session_login
    ):
        mapping.Client.objects(hostname=client_node_id).delete()

        update_tags = lambda client, tags: client.update_tags(tags, proxy_client.Client.TagsOp.SET)

        client_lxc_multislot = client_manager.create("test-client-multislot", ncpu=64, ram=131072)
        update_tags(
            client_lxc_multislot,
            [ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE, ctc.Tag.LXC, ctc.Tag.MULTISLOT]
        )

        client_lxc_browser_multislot = client_manager.create(
            "test-client-browser-multislot", ncpu=64, ram=131072
        )
        update_tags(
            client_lxc_browser_multislot,
            [ctc.Tag.BROWSER, ctc.Tag.LINUX_PRECISE, ctc.Tag.LXC, ctc.Tag.MULTISLOT]
        )

        client_lxc_singleslot = client_manager.create("test-client-singleslot", ncpu=64, ram=131072)
        update_tags(
            client_lxc_singleslot,
            [ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE, ctc.Tag.LXC, ctc.Tag.CORES16, ctc.Tag.CORES24]
        )

        client_porto_multislot = client_manager.create("test-porto-client-multislot", ncpu=64, ram=131072)
        update_tags(
            client_porto_multislot,
            [ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE, ctc.Tag.PORTOD, ctc.Tag.MULTISLOT]
        )

        client_porto_singleslot = client_manager.create("test-porto-client-singleslot", ncpu=64, ram=131072)
        update_tags(
            client_porto_singleslot,
            [ctc.Tag.GENERIC, ctc.Tag.LINUX_PRECISE, ctc.Tag.PORTOD, ctc.Tag.CORES16, ctc.Tag.CORES24]
        )

        porto_layer = manager_tests._create_resource(
            task_manager, parameters={"resource_type": "BASE_PORTO_LAYER"}, create_logs=False
        )

        task_params = {"owner": rest_session_login}
        task = test_task_2(None, **task_params)

        Sample = collections.namedtuple("Sample", "caches cores ram tags privileged porto_layers matched")
        Sample.__new__.__defaults__ = (None,) * len(Sample._fields)
        # noinspection PyArgumentList
        test_samples = [
            Sample(caches=True, cores=1, ram=8192, tags=ctc.Tag.GENERIC, matched=[client_lxc_singleslot]),
            Sample(caches=False, matched=[client_lxc_multislot]),
            Sample(ram=16384, matched=[client_lxc_multislot]),
            Sample(cores=4, matched=[client_lxc_multislot]),
            Sample(ram=32768, matched=[client_lxc_multislot]),
            Sample(cores=8, matched=[client_lxc_multislot]),
            Sample(ram=65536, matched=[client_lxc_multislot]),
            Sample(cores=16, matched=[client_lxc_multislot]),
            Sample(cores=17, matched=[client_lxc_singleslot]),
            Sample(cores=16, ram=65537, matched=[client_lxc_singleslot]),
            Sample(caches=False, cores=17, ram=65536, tags=ctc.Tag.BROWSER, matched=[client_lxc_browser_multislot]),
            Sample(
                caches=False, cores=17, ram=65536, tags=ctc.Tag.BROWSER | ctc.Tag.GENERIC,
                matched=[client_lxc_browser_multislot, client_lxc_singleslot]
            ),
            Sample(privileged=True, cores=16, ram=65537, tags=ctc.Tag.GENERIC, matched=[client_lxc_singleslot]),
            Sample(privileged=False, cores=25, matched=False),
            Sample(privileged=True, cores=1, ram=65536, matched=[client_lxc_singleslot]),
            Sample(privileged=False, matched=[client_lxc_multislot]),
            Sample(cores=4, matched=[client_lxc_multislot]),
            Sample(cores=5, matched=[client_lxc_multislot]),
            Sample(cores=8, matched=[client_lxc_multislot]),
            Sample(cores=16, matched=[client_lxc_multislot]),
            Sample(cores=17, matched=[client_lxc_singleslot]),
            Sample(cores=1, ram=8193, matched=[client_lxc_multislot]),
            Sample(ram=16384, matched=[client_lxc_multislot]),
            Sample(ram=16385, matched=[client_lxc_multislot]),
            Sample(ram=32768, matched=[client_lxc_multislot]),
            Sample(ram=65536, matched=[client_lxc_multislot]),
            Sample(ram=65537, matched=[client_lxc_singleslot]),
            Sample(privileged=True, cores=4, ram=16384, matched=[client_lxc_singleslot]),
            Sample(privileged=False, matched=[client_lxc_multislot]),
            Sample(privileged=True, cores=8, ram=32768, matched=[client_lxc_singleslot]),
            Sample(privileged=False, matched=[client_lxc_multislot]),
            Sample(privileged=True, cores=16, ram=65536, matched=[client_lxc_singleslot]),
            Sample(privileged=False, matched=[client_lxc_multislot]),
            Sample(caches=True, cores=1, ram=8192, porto_layers=[porto_layer.id], matched=[client_porto_singleslot]),
            Sample(caches=False, matched=[client_porto_multislot]),
            Sample(privileged=True, matched=[client_porto_singleslot]),
            Sample(ram=65537, privileged=False, matched=[client_porto_singleslot]),
            Sample(ram=65536, matched=[client_porto_multislot]),
            Sample(cores=17, matched=[client_porto_singleslot]),
            Sample(cores=16, matched=[client_porto_multislot]),
            Sample(tags=ctc.Tag.LXC, matched=[client_lxc_multislot, client_porto_multislot]),
            Sample(tags=ctc.Tag.PORTOD, porto_layers=[], matched=[client_porto_multislot]),
        ]

        # noinspection PyArgumentList
        effective_sample = Sample()
        for i, sample in enumerate(test_samples):
            effective_sample = effective_sample._replace(**{
                k: v
                for k, v in sample._asdict().iteritems()
                if v is not None
            })
            if sample.caches is True:
                del task.Requirements.Caches[...]
            elif sample.caches is False:
                # Reset caches requirement
                task.Requirements.Caches.qwer = None
                del task.Requirements.Caches.qwer

            if sample.cores is not None:
                task.Requirements.cores = sample.cores

            if sample.ram is not None:
                task.Requirements.ram = sample.ram

            if sample.tags is not None:
                task.Requirements.client_tags = sample.tags

            if sample.privileged is not None:
                task.Parameters.privileged = sample.privileged

            if sample.porto_layers is not None:
                task.Requirements.porto_layers = sample.porto_layers

            task.save()
            task_wrapper = controller.TaskWrapper(controller.Task.get(task.id))
            matched_clients = controller.TaskQueue.task_hosts_list(task_wrapper.model)[0]
            assert (
                sorted(_.hostname for _ in matched_clients) == sorted(_.hostname for _ in sample.matched)
                if sample.matched else
                matched_clients is None
            ), (i, effective_sample, task_wrapper.effective_client_tags, map(lambda _: _.hostname, matched_clients))
