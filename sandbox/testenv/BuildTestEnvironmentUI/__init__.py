#!/usr/bin/env python
# coding: utf-8

import tarfile

import sandbox.common.types.misc as ctm
from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk import task
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.svn import Arcadia

from sandbox.projects import resource_types
from sandbox.projects.common.ui import build_ui

import sandbox.common.types.client as ctc


class UIurlParameter(parameters.SandboxStringParameter):
    name = 'ui_sources'
    default_value = 'arcadia:/arc/trunk/arcadia/search/garden/test_environment/te_frontend'
    description = 'UI sources URL'
    required = True


class RevisionParameter(parameters.SandboxIntegerParameter):
    name = "revision"
    description = "Revision"
    default_value = None


class BuildTestEnvironmentUI(task.SandboxTask):

    type = "BUILD_TEST_ENVIRONMENT_UI"

    input_parameters = [
        UIurlParameter,
        RevisionParameter,
    ]

    dns = ctm.DnsType.DNS64
    client_tags = ctc.Tag.LINUX_PRECISE

    def on_enqueue(self):
        task.SandboxTask.on_enqueue(self)

        self.ctx['out_resource_id'] = self.create_resource(
            self.descr,
            'frontend.tgz',
            resource_types.TEST_ENVIRONMENT_UI,
            arch='any'
        ).id

    def on_execute(self):
        frontend_res = channel.sandbox.get_resource(self.ctx['out_resource_id'])
        frontend_path = self.abs_path("frontend")

        svn_url = self.ctx[UIurlParameter.name]
        revision = self.ctx[RevisionParameter.name]

        Arcadia.checkout(svn_url, frontend_path, revision=revision)

        code_info = build_ui.CodeInfoSvn(frontend_path, None, revision, svn_url)

        inf = build_ui.build(code_info)

        with tarfile.open(frontend_res.path, "w:gz") as archive:
            archive.add(inf.path, arcname="frontend")


__Task__ = BuildTestEnvironmentUI
