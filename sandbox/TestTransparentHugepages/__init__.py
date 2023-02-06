# -*- coding: utf-8 -*-
import time

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxBoolParameter

from sandbox.common.types.client import Tag

# from projects import resource_types

from sandbox.projects.common.yabs.server.components.hugepage_warmup import warm_task_up
from sandbox.projects.common.utils import get_or_default


class CompactMemory(SandboxBoolParameter):
    name = 'compact_memory'
    description = 'Be privileged and use /proc/sys/vm/compact_memory.'
    default_value = False


def run_compact_memory():
    while True:
        with open('/proc/sys/vm/compact_memory', 'w') as cm:
            cm.write('1\n')
        time.sleep(0.1)


class TestTransparentHugepages(SandboxTask):
    execution_space = 1 * 1024
    type = 'TEST_TRANSPARENT_HUGEPAGES'
    description = 'Attempt to acquire as much AnonHugePages as possible. BSSERVER-1299.'

    client_tags = Tag.GENERIC & Tag.INTEL_E5_2650
    required_ram = 110 * 1024
    max_restarts = 10

    input_parameters = [CompactMemory]

    @property
    def privileged(self):
        return get_or_default(self.ctx, CompactMemory)

    def on_execute(self):
        warm_task_up(self)


__Task__ = TestTransparentHugepages
