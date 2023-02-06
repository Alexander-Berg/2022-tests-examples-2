#!/usr/bin/env python
# coding: utf-8

import logging
import base64
import codecs
import hashlib
import json
import random

import sandbox.common.types.task as ctt
from sandbox.sandboxsdk.parameters import SandboxBoolParameter
from sandbox.sandboxsdk.parameters import SandboxFloatParameter
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.parameters import ResourceSelector
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.common.errors import TaskFailure
from sandbox.common.errors import TaskError
from sandbox.projects import resource_types


class SuccessWeightParameter(SandboxFloatParameter):
    name = "success_weight"
    description = "SUCCESS weight (probability)."
    default_value = 0.5


class FailureWeightParameter(SandboxFloatParameter):
    name = "failure_weight"
    description = "FAILURE weight (probability)."
    default_value = 0.5


class ExceptionWeightParameter(SandboxFloatParameter):
    name = "exception_weight"
    description = "EXCEPTION weight (probability)."
    default_value = 0.0


class GenerateMetatestsParameter(SandboxBoolParameter):
    name = "generate_metatests"
    description = "Generate metatest results resource."
    default_value = False


class ResourceParameter(ResourceSelector):
    name = 'resource_id'
    description = 'some resource'
    resource_type = resource_types.TEST_ENVIRONMENT_PACKAGE
    group = 'some group'


class ResourceAssertParameter(SandboxBoolParameter):
    name = 'assert_resource'
    description = 'Assert resource is not None'
    default_value = False


class MakeDiffParameter(SandboxBoolParameter):
    name = 'make_diff'
    description = 'Makes diff'
    default_value = False


class ForDiff1Parameter(SandboxStringParameter):
    name = 'for_diff_1'
    description = 'First parameter for diff'
    default_value = ''


class ForDiff2Parameter(SandboxStringParameter):
    name = 'for_diff_2'
    description = 'Second parameter for diff'
    default_value = ''


class AdditionalMetatestParameter(SandboxBoolParameter):
    name = 'additional_metatests'
    description = 'additional metatests'
    default_value = False


class TestEnvironmentDummy(SandboxTask):
    """
    Dummy task that emulates different kind of failures.
    """

    type = "TEST_ENVIRONMENT_DUMMY"
    input_parameters = [
        SuccessWeightParameter,
        FailureWeightParameter,
        ExceptionWeightParameter,
        GenerateMetatestsParameter,
        ResourceParameter,
        ResourceAssertParameter,
        AdditionalMetatestParameter,
        MakeDiffParameter,
        ForDiff1Parameter,
        ForDiff2Parameter,
    ]

    SE_TAGS = {
        'limit1': 1,
        'limit3': 3,
        'limit5': 5,
        'limit100': 100,
    }

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        if self.se_tag:
            sem_name = "{}/{}".format(self.type, self.se_tag)
            self.semaphores(ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name=sem_name, capacity=self.SE_TAGS[self.se_tag])
                ]
            ))

    def on_execute(self):

        if self.ctx[ResourceAssertParameter.name]:
            resource = self.ctx[ResourceParameter.name]
            logging.info('[resource for execution] %s', resource)
            if resource is None:
                self.do_fail()

        if self.ctx[MakeDiffParameter.name]:
            self.ctx['has_diff'] = (
                self.ctx[ForDiff1Parameter.name] != self.ctx[ForDiff2Parameter.name]
            )

        weighted_handlers = [
            (self.ctx[SuccessWeightParameter.name], self.do_success),
            (self.ctx[FailureWeightParameter.name], self.do_fail),
            (self.ctx[ExceptionWeightParameter.name], self.do_exception),
        ]
        self.choose(weighted_handlers)()
        if self.ctx[GenerateMetatestsParameter.name]:
            self.generate_metatests(self.ctx[AdditionalMetatestParameter.name])

    def generate_metatests(self, additional_metatest):
        """
        Generates dummy metatest results resource.
        """
        results = []
        metatests = ADDITIONAL_METATESTS if additional_metatest else METATESTS
        for tests in metatests:
            for test in tests:
                results.append(test.get_result())
        self.results = results
        results2 = {
            "results": results
        }
        with codecs.open(self.abs_path("results2.json"), "wt", encoding="utf-8") as results_file:
            json.dump(results2, results_file, indent=2)
        self.create_resource("Dummy Metatest Results", self.abs_path("results2.json"), resource_types.TEST_ENVIRONMENT_JSON_V2, {"ttl": 14})

    def choose(self, weighted_items):
        random_value = random.uniform(0.0, sum(weight for weight, _ in weighted_items))

        accumulated_weight = 0.0
        for weight, item in weighted_items:
            accumulated_weight += weight
            if random_value < accumulated_weight:
                return item

    def do_success(self):
        pass  # Do nothing.

    def do_fail(self):
        raise TaskFailure("emulated failure")

    def do_exception(self):
        raise TaskError("emulated exception")

    def do_no_res(self):
        self.sync_resource(145722259)


class DummyMetatest:
    """
    Emulates behavior of a metatest.
    """

    def __init__(self, name, subtest_name, path, broken_probability=None):
        self._name = name
        self._subtest_name = subtest_name
        self._path = path
        self._broken_probability = broken_probability

    def get_result(self):
        broken = (self._broken_probability is not None) and (random.random() < self._broken_probability)
        tag = "%r\0%r\0%r" % (self._name, self._path, broken)
        result = {
            "id": hashlib.md5("%s\x00%s" % (self._name, self._subtest_name)).hexdigest(),
            "type": "test",
            "path": self._path,
            "name": self._name,
            "subtest_name": self._subtest_name,
            "toolchain": "linux",
            "status": "OK" if not broken else "FAILED",
            "size": "SMALL",
            "uid": base64.b64encode(hashlib.sha1(tag).digest()),
            "duration": random.random(),
            "owners": {
                "logins": [],
                "groups": []
            }
        }
        if broken:
            result["status"] = "FAILED"
            result["error_type"] = "REGULAR"
        else:
            result["status"] = "OK"
        return result


METATESTS = (
    (
        DummyMetatest("0%", "success-1", "success/1"),
        DummyMetatest("0%", "success-2", "success/2"),
    ),
    (
        DummyMetatest("100%", "fail-1", "fail/1", 1.0),
        DummyMetatest("100%", "fail-2", "fail/2", 1.0),
    ),
    (
        DummyMetatest("20%", "20p-1", "20p/1", 0.2),
        DummyMetatest("20%", "20p-2", "20p/2", 0.2),
        DummyMetatest("20%", "20p-3", "20p/3", 0.2),
    ),
    (
        DummyMetatest("50%", "50p-1", "50/1", 0.5),
        DummyMetatest("50%", "50p-2", "50/2", 0.5),
        DummyMetatest("50%", "50p-3", "50/3", 0.5),
    ),
    (
        DummyMetatest("80%", "80-1", "80/1", 0.8),
        DummyMetatest("80%", "80-2", "80/2", 0.8),
        DummyMetatest("80%", "80-3", "80/3", 0.8),
    ),
)


ADDITIONAL_METATESTS = (
    (
        DummyMetatest("0%", "additional-success-1", "success/1"),
        DummyMetatest("0%", "additional-success-2", "success/2"),
    ),
    (
        DummyMetatest("100%", "additional-fail-1", "fail/1", 1.0),
        DummyMetatest("100%", "additional-fail-2", "fail/2", 1.0),
    ),
    (
        DummyMetatest("20%", "additional-20p-1", "20p/1", 0.2),
        DummyMetatest("20%", "additional-20p-2", "20p/2", 0.2),
        DummyMetatest("20%", "additional-20p-3", "20p/3", 0.2),
    ),
    (
        DummyMetatest("50%", "additional-50p-1", "50/1", 0.5),
        DummyMetatest("50%", "additional-50p-2", "50/2", 0.5),
        DummyMetatest("50%", "additional-50p-3", "50/3", 0.5),
    ),
    (
        DummyMetatest("80%", "additional-80-1", "80/1", 0.8),
        DummyMetatest("80%", "additional-80-2", "80/2", 0.8),
        DummyMetatest("80%", "additional-80-3", "80/3", 0.8),
    ),
)


__Task__ = TestEnvironmentDummy
