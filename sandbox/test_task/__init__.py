# coding: utf-8

import os
import time
import copy
from six.moves import queue as Queue
import random
import inspect
import logging
import getpass
import textwrap
import threading

from sandbox import common
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr

from sandbox import sdk2
from sandbox.sdk2 import ssh
from sandbox.sdk2.vcs import svn

from sandbox.sandboxsdk import task
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk import errors
from sandbox.sandboxsdk import channel
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk import environments

import sandbox.projects.sandbox.resources as sb_resources
import sandbox.projects.common.utils as utils


def _cqueue_pinger(hosts_list, timeout):
    import api.cqueue
    result = []
    with api.cqueue.Client(implementation='cqudp') as client:
        for host, res, err in client.ping(hosts_list).wait(timeout=timeout):
            result.append("{host}: {res}".format(host=host, res="Okay" if not err else err))
    return result


class TestTask(task.SandboxTask):
    """
    A test task is widely used by Sandbox build-time tests and also by Sandbox developers to check new releases at
    `Sandbox Development Installation`_ before releasing a new build.

    .. _Sandbox Development Installation: https://sandbox-dev.yandex-team.ru/

    Following commonly used behaviours can be checked by the task:

    - Resources management
    - Children tasks creation and monitoring
    - Multi-threading
    - ... and much more!
    """

    max_restarts = 10

    @property
    def environment(self):
        envs = []
        pip_modules = self.ctx.get(self.PipEnvironments.name, False)
        if pip_modules:
            for module in pip_modules.split(','):
                envs.append(environments.PipEnvironment(module))

        return tuple(envs)

    class LifeBlock(parameters.SandboxInfoParameter):
        description = 'Lifetime parameters'

    class PreparingLiveTime(parameters.SandboxIntegerParameter):
        name = 'prep_live_time'
        description = 'Time to live in preparing'
        default_value = 0
        required = True

    class LiveTime(parameters.SandboxIntegerParameter):
        name = 'live_time'
        description = 'Time to live'
        default_value = 10
        required = True

    class FinishingLiveTime(parameters.SandboxIntegerParameter):
        name = 'fin_live_time'
        description = 'Time to live in finishing'
        default_value = 0
        required = True

    class ReleasingLiveTime(parameters.SandboxIntegerParameter):
        name = 'releasing_live_time'
        description = 'Time to live in releasing'
        default_value = 0
        required = True

    class BreakTime(parameters.SandboxIntegerParameter):
        name = 'break_time'
        description = 'Time to break'

    class TerminationTime(parameters.SandboxIntegerParameter):
        name = "termination_time"
        description = "Time to terminate (on signal handling)"
        default_value = 0

    class RaiseExceptionOnStart(parameters.SandboxBoolParameter):
        name = 'raise_exception_on_start'
        description = 'Raise excepton on start'

    class RaiseExceptionOnEnqueue(parameters.SandboxBoolParameter):
        name = 'raise_exception_on_enqueue'
        description = 'Raise excepton on enqueue'

    class InvalidContextOnExecute(parameters.SandboxBoolParameter):
        name = 'invalid_context_on_execute'
        description = 'Save unserializable value to context during execution'

    class GoToState(parameters.SandboxStringParameter):
        name = 'go_to_state'
        description = 'Go to state'
        multiline = False
        choices = tuple(
            (s, s)
            for s in (
                ctt.Status.SUCCESS,
                ctt.Status.TEMPORARY,
                ctt.Status.EXCEPTION,
                ctt.Status.FAILURE
            )
        )
        default_value = ctt.Status.SUCCESS

    class NoTimeout(parameters.SandboxBoolParameter):
        name = 'use_no_timeout'
        description = 'If the task times out during "Time to live", switch to TEMPORARY'

    class UseCGroup(parameters.SandboxBoolParameter):
        name = 'use_cgroup'
        description = 'Create cgroup and run subprocess'

    class Suspend(parameters.SandboxBoolParameter):
        name = 'suspend'
        description = 'Suspend before finish'

    class WaitTime(parameters.SandboxIntegerParameter):
        name = 'wait_time'
        description = 'Wait for timeout'
        required = True

    class WaitOnEnqueue(parameters.SandboxIntegerParameter):
        name = 'wait_on_enqueue'
        description = 'Wait on enqueue'

    class WaitTaskOnEnqueue(parameters.ListRepeater, parameters.SandboxStringParameter):
        name = 'wait_task_on_enqueue'
        description = 'Wait for tasks on enqueue'

    class StopOnEnqueue(parameters.SandboxBoolParameter):
        name = 'stop_on_enqueue'
        description = 'Stop on enqueue'

    class SubtasksBlock(parameters.SandboxInfoParameter):
        description = 'Subtasks Parameters'

    class NumberOfSubtasks(parameters.SandboxIntegerParameter):
        name = 'number_of_subtasks'
        description = 'Number of subtasks'
        default_value = 1

    class InheritNotifications(parameters.SandboxBoolParameter):
        name = 'inherit_notifications'
        description = 'Inherit notifications in subtasks'
        default_value = True

    class CreateSubtask(parameters.SandboxBoolParameter):
        name = 'create_sub_task'
        description = 'Create subtask'
        required = False
    CreateSubtask.sub_fields = {
        'true': [SubtasksBlock.name, NumberOfSubtasks.name, InheritNotifications.name]
    }

    class ResourcesBlock(parameters.SandboxInfoParameter):
        description = 'Resources Parameters'

    class DependentResource(parameters.LastReleasedResource):
        name = 'dependent_resource_id'
        description = 'Dependent resource'
        resource_type = sb_resources.TestTaskResource2
        state = (ctr.State.READY, ctr.State.NOT_READY)
        required = False

    class DependentResources(parameters.LastReleasedResource):
        name = 'dependent_resources'
        description = 'Dependent resources'
        resource_type = sb_resources.TestTaskResource2
        state = (ctr.State.READY, ctr.State.NOT_READY)
        required = False
        multiple = True

    class SyncInSubprocess(parameters.SandboxBoolParameter):
        name = 'sync_resource_in_subprocess'
        description = 'Sync resource with Synchrophazotron'
        default_value = False

    class CreateResources(parameters.SandboxBoolParameter):
        name = 'create_resources'
        description = 'Create resources'
        default_value = True

    class CreateEmptyResource(parameters.SandboxBoolParameter):
        name = 'create_empty_resource'
        description = 'Create empty resource'
        default_value = False

    class CreateResourceOnEnqueue(parameters.SandboxBoolParameter):
        name = 'create_resource_on_enqueue'
        description = 'Create resource in on_enqueue()'
        default_value = False

    class ModifyResource(parameters.SandboxBoolParameter):
        name = 'modify_resource'
        description = 'Modify resource'

    class CreateParentResources(parameters.SandboxBoolParameter):
        name = 'create_parent_resources'
        description = 'Create parent resources'

    class ParentResourceId(parameters.SandboxIntegerParameter):
        name = 'parent_resource_id'
        description = 'Parent resource ID'
        required = False

    class SaveParentResourceBasename(parameters.SandboxBoolParameter):
        name = 'save_parent_resource_basename'
        description = 'Save parent resource basename'

    class CheckCoredump(parameters.SandboxBoolParameter):
        name = 'check_coredump'
        description = 'Check coredump'

    class CheckPbcopy(parameters.SandboxBoolParameter):
        name = 'check_pbcopy'
        description = 'Check pbcopy'

    class VaultItemOwner(parameters.SandboxStringParameter):
        name = 'vault_item_owner'
        description = 'Vault item owner (task author by default)'
        group = 'Vault Parameters'
        default_value = 'SANDBOX'

    class VaultItemName(parameters.SandboxStringParameter):
        name = 'vault_item_name'
        description = 'Vault item name'
        group = 'Vault Parameters'
        default_value = 'test_data'

    class VaultItemExpected(parameters.SandboxStringParameter):
        name = 'vault_item_expected'
        description = 'Expected contents of vault record'
        group = 'Vault Parameters'
        default_value = 'test vault data for test task'

    class CheckVault(parameters.SandboxBoolParameter):
        name = 'check_vault'
        description = 'Check vault data'
        group = 'Vault Parameters'
    CheckVault.sub_fields = {'true': [VaultItemName.name, VaultItemOwner.name, VaultItemExpected.name]}

    class CheckSsh(parameters.SandboxBoolParameter):
        name = "check_ssh"
        description = "Check ssh"
    CheckSsh.sub_fields = {"true": [VaultItemName.name, VaultItemOwner.name]}

    class SubversionBlock(parameters.SandboxInfoParameter):
        description = 'Subversion Parameters'

    class TestArcadiaURL(parameters.SandboxArcadiaUrlParameter):
        name = 'test_get_arcadia_url'
        description = 'Path to Arcadia svn'
        default_value = ''
        required = False

    class NotificationBlock(parameters.SandboxInfoParameter):
        description = 'Notification Parameters'

    class EmailRecipient(parameters.SandboxStringParameter):
        name = 'email_recipient'
        description = 'Email recipient'

    class MarkAsUrgent(parameters.SandboxBoolParameter):
        name = "mark_as_urgent"
        description = "Mark as urgent (send from sandbox-urgent@)"
        default_value = False

    class SendEmail(parameters.SandboxBoolParameter):
        name = 'send_email_to_recipient'
        description = 'Send test email'
    SendEmail.sub_fields = {'true': [EmailRecipient.name, MarkAsUrgent.name]}

    class MiscBlock(parameters.SandboxInfoParameter):
        description = 'Miscellaneous Parameters'

    class RamdriveSize(parameters.SandboxIntegerParameter):
        name = 'ramdrive'
        description = 'Create a RAM drive of specified size in GiB'

    class Privileged(parameters.SandboxBoolParameter):
        name = 'privileged'
        description = 'Run under root privileges'

    class Container(parameters.Container):
        required = False
        default_value = None
        description = "Container"

    class PingHostsViaCqueue(parameters.SandboxStringParameter):
        name = 'ping_host_via_skynet'
        description = 'Pass hostnames separated with comma in old style syntax (e.g. sandbox0{1..4}h)'
        default_value = ''

    class CreateIndependentTask(parameters.SandboxBoolParameter):
        name = 'create_independent_task'
        description = 'Create independent task'

    class PipEnvironments(parameters.SandboxStringParameter):
        name = 'pip_environments'
        description = 'Install pip modules (comma-separated)'

    class Multiselect(parameters.SandboxBoolGroupParameter):
        name = 'multiselect'
        description = 'Just a muliselect field'
        choices = (
            ('Option One', 'option1'),
            ('Option Two', 'option2'),
            ('Option Three', 'option3'),
        )
        default_value = 'option2'

    class ListOfStrings(parameters.ListRepeater, parameters.SandboxStringParameter):
        name = 'list_of_strings'
        description = 'Dynamic parameter of type "List"'

    class DictOfStrings(parameters.DictRepeater, parameters.SandboxStringParameter):
        name = 'dict_of_strings'
        description = 'Dynamic parameter of type "Dict"'
        default_value = ''

    class DictOfStringsWithChoices(parameters.DictRepeater, parameters.SandboxStringParameter):
        name = 'dict_of_strings_choices'
        description = 'Dynamic parameter of type "Dict" with choices'
        choices = (
            ('', ''),
            ('SUCCESS', 'success'),
            ('TEMPORARY', 'temporary'),
            ('EXCEPTION', 'exception'),
            ('FAILURE', 'failure'),
        )
        default_value = ''

    class ShowDictOfStringsWithChoices(parameters.SandboxBoolParameter):
        name = 'show_dict_of_strings_choices'
        description = 'Show Dict with choices'
        default_value = False
    ShowDictOfStringsWithChoices.sub_fields = {'true': [DictOfStringsWithChoices.name]}

    class LongListWithChoices(parameters.SandboxStringParameter):
        name = 'long_list_with_choices'
        description = 'More than 7 choices'
        choices = (
            ('Choice One', 'choice1'),
            ('Choice Two', 'choice2'),
            ('Choice Three', 'choice3'),
            ('Choice Four', 'choice4'),
            ('Choice Five', 'choice5'),
            ('Choice Again', 'choice_again'),
            ('One more choice', 'choice_one_more'),
            ('... and again!', 'choice_and_again'),
            ('Final choice!', 'choice_final'),
        )
        default_value = 'choice3'

    SERVICE = True

    @property
    def privileged(self):
        return self.ctx.get(self.Privileged.name, False)

    type = 'TEST_TASK'

    # noinspection PyUnresolvedReferences
    client_tags = ctc.Tag.GENERIC | ctc.Tag.MULTISLOT | ctc.Tag.SERVER | ctc.Tag.Group.OSX

    input_parameters = [
        LifeBlock,
        PreparingLiveTime,
        LiveTime,
        FinishingLiveTime,
        ReleasingLiveTime,
        BreakTime,
        TerminationTime,
        RaiseExceptionOnStart,
        RaiseExceptionOnEnqueue,
        InvalidContextOnExecute,
        GoToState,
        NoTimeout,
        UseCGroup,
        Suspend,
        WaitTime,
        WaitOnEnqueue,
        WaitTaskOnEnqueue,
        StopOnEnqueue,
        CreateSubtask,
        SubtasksBlock,
        NumberOfSubtasks,
        InheritNotifications,
        ResourcesBlock,
        DependentResource,
        DependentResources,
        SyncInSubprocess,
        CreateResources,
        CreateEmptyResource,
        CreateResourceOnEnqueue,
        ModifyResource,
        CreateParentResources,
        ParentResourceId,
        SaveParentResourceBasename,
        CheckCoredump,
        CheckPbcopy,
        CheckVault,
        VaultItemOwner,
        VaultItemName,
        VaultItemExpected,
        CheckSsh,
        SubversionBlock,
        TestArcadiaURL,
        NotificationBlock,
        SendEmail,
        EmailRecipient,
        MarkAsUrgent,
        MiscBlock,
        RamdriveSize,
        Privileged,
        Container,
        PingHostsViaCqueue,
        CreateIndependentTask,
        PipEnvironments,
        Multiselect,
        ListOfStrings,
        DictOfStrings,
        ShowDictOfStringsWithChoices,
        DictOfStringsWithChoices,
        LongListWithChoices
    ]

    execution_space = 3521

    CTX_REDEFINES = {'kill_timeout': 3600, 'do_not_restart': True}
    CTX_CUSTOM = {'test_task_test_context_key': 0xBEAF}

    def initCtx(self):
        self.ctx.update(self.CTX_REDEFINES)
        self.ctx.update(self.CTX_CUSTOM)
        if self.descr and 'test init UNKNOWN' in self.descr:
            self.ctx[self.LiveTime.name] = 21
            self.descr = self.descr.replace('test init UNKNOWN', 'testt init UNKNOWN')
            raise Exception('FFFfffiuuuu')

    @property
    def release_template(self):
        subject = u'Test task "{}" has been released!'.format(self.descr)
        return self.ReleaseTemplate(
            ["sandbox-noreply", "devnull"],
            subject,
            textwrap.dedent(u"""
                Good news, everyone!

                {}

                --
                Sincerely,
                    your Sandbox ({}) installation.
            """.format(subject, self.host))
        )

    @property
    def footer(self):
        return [
            {'helperName': 'replacePlaceholders',
             'content': textwrap.dedent("""
            <div style="border: 2px solid yellow;">
                <h2 align="center">
                    footer: <h1>{}</h1>
                </h2>
                <br/>
                Placeholder replacement should also works fine: <b>%TEST%</b>
            </div>
            """.format(self.descr))},

            {'helperName': '',
             'content': textwrap.dedent("""
            <a href="https://sandbox.yandex-team.ru/sandbox/tasks/view?task_id=23150465">23150465</a>
            <div style="font-size: 12pt; font-weight: bold; color: #9f0000; padding: 3px;">
            RPS measure on FreeBSD+e5-2660 is inaccurate. Details:
            <a href="https://jira.yandex-team.ru/SANDBOX-1779">SANDBOX-1179</a>
            </div><br/>
            <div><strong>Comment: no helper.</strong></div>
            """)},

            {'helperName': 'replacePlaceholders',
             'content': textwrap.dedent("""
            <a href="https://sandbox.yandex-team.ru/sandbox/tasks/view?task_id=23150465">23150465</a>
            <div style="font-size: 12pt; font-weight: bold; color: #9f0000; padding: 3px;">
            RPS measure on FreeBSD+e5-2660 is inaccurate. Details:
            <a href="https://jira.yandex-team.ru/SANDBOX-1779">SANDBOX-1179</a>
            </div><br/>
            <div><strong>Comment: %TEST% (sync helper)</strong></div>
            """)},

            {'helperName': '',
             'content': textwrap.dedent("""
            <a href="https://sandbox.yandex-team.ru/sandbox/tasks/view?task_id=23150465">23150465</a>
            <div style="font-size: 12pt; font-weight: bold; color: #9f0000; padding: 3px;">
            RPS measure on FreeBSD+e5-2660 is inaccurate. Details:
            <a href="https://jira.yandex-team.ru/SANDBOX-1779">SANDBOX-1179</a>
            </div><br/>
            <div><strong>Comment: %TEST% (async helper)</strong></div>
            """)},

            {'helperName': '',
             'content': {
                 'Task': 'Status',
                 'Task #21160643. Subtask 24 of task #21160270': 'FINISHED',
                 'Task #21160640. Subtask 23 of task #21160270': 'FINISHED',
                 'Task #21160638. Subtask 22 of task #21160270': 'FINISHED',
                 'Task #21160635. Subtask 21 of task #21160270': 'FINISHED',
                 'Task #21160633. Subtask 20 of task #21160270': 'FINISHED',
                 'Task #21160631. Subtask 19 of task #21160270': 'FINISHED',
                 'Task #21160628. Subtask 18 of task #21160270': 'FINISHED',
                 'Task #21160622. Subtask 17 of task #21160270': 'FINISHED',
                 'Task #21160618. Subtask 16 of task #21160270': 'FINISHED',
                 'Task #21160537. Subtask 15 of task #21160270': 'FINISHED',
                 'Task #21160532. Subtask 14 of task #21160270': 'FINISHED',
                 'Task #21160521. Subtask 13 of task #21160270': 'FINISHED',
                 'Task #21160511. Subtask 12 of task #21160270': 'FINISHED',
                 'Task #21160506. Subtask 11 of task #21160270': 'FINISHED',
                 'Task #21160501. Subtask 10 of task #21160270': 'FINISHED'
             }},

            {'helperName': '',
             'content': [
                 {'tasks': 'Task #21160643. Subtask 24 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160640. Subtask 23 of task #21160270', 'status': 'FINISHED', 'child': '6547 4591'},
                 {'tasks': 'Task #21160638. Subtask 22 of task #21160270', 'status': 'FINISHED', 'child': '2378 4591'},
                 {'tasks': 'Task #21160635. Subtask 21 of task #21160270', 'status': 'FINISHED', 'child': '2378 4591'},
                 {'tasks': 'Task #21160633. Subtask 20 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160631. Subtask 19 of task #21160270', 'status': 'FINISHED', 'child': '1234 4591'},
                 {'tasks': 'Task #21160628. Subtask 18 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160622. Subtask 17 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160618. Subtask 16 of task #21160270', 'status': 'FINISHED', 'child': '6547 4591'},
                 {'tasks': 'Task #21160537. Subtask 15 of task #21160270', 'status': 'FINISHED', 'child': '9875 4591'},
                 {'tasks': 'Task #21160532. Subtask 14 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160521. Subtask 13 of task #21160270', 'status': 'FINISHED', 'child': '2378 4591'},
                 {'tasks': 'Task #21160511. Subtask 12 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160506. Subtask 11 of task #21160270', 'status': 'FINISHED', 'child': '3458 4591'},
                 {'tasks': 'Task #21160501. Subtask 10 of task #21160270', 'status': 'FINISHED', 'child': '2378 4591'}
             ]},

            {'helperName': '',
             'content': {
                 'Subtasks results': {
                     'Task #21160643. Subtask 24 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160640. Subtask 23 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160638. Subtask 22 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160635. Subtask 21 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160633. Subtask 20 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160631. Subtask 19 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160628. Subtask 18 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160622. Subtask 17 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160618. Subtask 16 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160537. Subtask 15 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160532. Subtask 14 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160521. Subtask 13 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160511. Subtask 12 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160506. Subtask 11 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'},
                     'Task #21160501. Subtask 10 of task #21160270': {'status': 'FINISHED', 'comment': 'some comment'}
                 }
             }},

            {'helperName': '',
             'content': {
                 'Test order for rows': {
                     "header": [
                         {"key": "key1", "title": "key12"},
                         {"key": "key2", "title": "key22"},
                     ],
                     "body": {
                         "key1": [1, 2, 3, 4, 5],
                         "key2": [6, 7, 8, 9, 10]
                     }
                 }
             }},
        ]

    def on_enqueue(self):
        task.SandboxTask.on_enqueue(self)

        if self.ctx.get(self.CreateResourceOnEnqueue.name):
            path = self.abs_path('on_enqueue_resource')
            self.ctx['created_resource_on_enqueue'] = self.create_resource(
                self.descr,
                path,
                sb_resources.TestTaskResource,
                arch='any'
            ).id

        if self.ctx.get('test_on_enqueue'):
            self.ctx['test_on_enqueue'] += 1
        else:
            self.ctx['test_on_enqueue'] = 1

        if self.ctx.get(self.RamdriveSize.name):
            self.ramdrive = self.RamDrive(
                ctm.RamDriveType.TMPFS,
                self.ctx[self.RamdriveSize.name] << 10,
                None
            )
        if self.ctx[self.RaiseExceptionOnEnqueue.name]:
            raise Exception("Exception on enqueue.")
        if self.ctx[self.WaitOnEnqueue.name]:
            self.wait_time(self.ctx[self.WaitOnEnqueue.name])
        elif self.ctx[self.WaitTaskOnEnqueue.name]:
            self.wait_tasks(
                tasks=self.ctx[self.WaitTaskOnEnqueue.name],
                statuses=list(self.Status.Group.FINISH),
                wait_all=True
            )

        if self.ctx[self.StopOnEnqueue.name]:
            raise common.errors.TaskStop

    def on_release(self, params):
        self.ctx["has_channel_task"] = bool(channel.channel.task)
        self.try_access_vault()
        if params["release_subject"] == "die":
            raise Exception
        self.ctx["test_on_release"] = params
        if params.get("_release_subscriber") and params.get("release_subject"):
            channel.channel.sandbox.send_email(
                params["_release_subscriber"],
                None,
                params["release_subject"],
                "[testing] Release body"
            )
        if self.ctx.get(self.ReleasingLiveTime.name):
            sleep = self.ctx[self.ReleasingLiveTime.name]
            logging.info("Sleeping for %.2fs", sleep)
            time.sleep(sleep)
        task.SandboxTask.on_release(self, params)

    def on_prepare(self):
        task.SandboxTask.on_prepare(self)
        if self.ctx.get(self.PreparingLiveTime.name):
            sleep = self.ctx[self.PreparingLiveTime.name]
            logging.info("Sleeping for %.2fs", sleep)
            time.sleep(sleep)

    def on_break(self):
        logging.debug("on_break")
        self.ctx["test_on_break"] = bool(channel.channel.task)
        self.ctx["has_channel_task"] = bool(channel.channel.task)
        self.try_access_vault()
        task.SandboxTask.on_break(self)
        time.sleep(self.ctx[self.BreakTime.name])

    def on_finish(self):
        task.SandboxTask.on_finish(self)
        if self.ctx.get(self.CheckCoredump.name):
            if not self.list_resources("CORE_DUMP"):
                raise errors.SandboxTaskFailureError("Coredump check failed: no resource found")

        if self.ctx.get(self.FinishingLiveTime.name):
            sleep = self.ctx[self.FinishingLiveTime.name]
            logging.info("Sleeping for %.2fs", sleep)
            time.sleep(sleep)

    def on_terminate(self):
        logging.debug("Terminating")
        self.ctx["test_on_terminate"] = True
        time.sleep(self.ctx[self.TerminationTime.name])
        logging.debug("Terminated")

    def arcadia_info(self):
        return None, "Default release subject", None

    def try_access_vault(self):
        caller = inspect.getframeinfo(inspect.currentframe().f_back)[2]
        logging.info('Test vault access from %s()', caller)
        if self.ctx[self.CheckVault.name]:
            vault_data = self.get_vault_data(
                self.ctx.get(self.VaultItemOwner.name),
                self.ctx.get(self.VaultItemName.name)
            )
            expected = self.ctx.get(self.VaultItemExpected.name, self.VaultItemExpected.default_value)
            if vault_data != expected:
                raise errors.SandboxTaskUnknownError(
                    'Vault error: test_data {} invalid (expected {})'.format(vault_data, expected)
                )
            logging.info('Vault data: %s', vault_data)
            self.ctx['has_vault_key'] = True
        else:
            logging.info('"Test vault" parameter is not set, skipping the test')

    def on_execute(self):
        logging.info("Current environments: %r", os.environ)
        with self.memoize_stage.first_run:
            logging.info('This is my FIRST RUN!')
        logging.info("Current user is %r (UID %d, GID %d)", getpass.getuser(), os.getuid(), os.getgid())

        if self.ctx[self.InvalidContextOnExecute.name]:
            self.ctx["unpicklable"] = lambda: None
            return  # don't do anything else, just check task ends up in EXCEPTION status

        if self.ctx[self.RaiseExceptionOnStart.name]:
            raise errors.SandboxTaskUnknownError('UNKNOWN ERROR')

        if self.ramdrive:
            logging.info(
                "RAM drive of size %s path: %r",
                common.utils.size2str(self.ramdrive.size << 20),
                self.ramdrive.path
            )
            process.run_process(['mount'], log_prefix='mount')
            process.run_process(['df', '-h'], log_prefix='df_h')

        logging.info('Test run_process')
        process.run_process(['du', '-h'], log_prefix='du_h')
        logging.info('Test logging message.')

        if self.ctx[self.CheckCoredump.name]:
            p = process.run_process(["sleep", "1000"], wait=False)
            os.kill(p.pid, 3)

        if self.ctx[self.CheckPbcopy.name]:
            p = process.run_process("echo 12345 | pbcopy; pbpaste", shell=True, outs_to_pipe=True, wait=False)
            out, err = p.communicate()
            assert p.returncode == 0 and out.strip() == "12345", (p.returncode, out, err)

        logging.info('Test environment')
        process.run_process(['env | sort'], log_prefix='env', shell=True)

        self.try_access_vault()

        if self.ctx[self.PingHostsViaCqueue.name]:
            import library.sky.hosts
            hosts = library.sky.hosts.braceExpansion(self.ctx[self.PingHostsViaCqueue.name].split(","))
            timeout = len(hosts) * 3
            logging.info(
                "Staring ping via cqueue %d host(s): %s with timeout %d",
                len(hosts),
                ", ".join(hosts),
                timeout
            )
            utils.receive_skynet_key(self.owner)
            logging.info("Here is results:\n%s", "\n".join(_cqueue_pinger(hosts, timeout=timeout)))
            logging.info("Ping is over")

        if self.ctx.get('multi_threading'):
            logging.info('Test multi-threading')

            def ping_server(queue):
                try:
                    server = channel.channel.sandbox.server
                    for _ in xrange(3):
                        data = random.randint(0, 0x7FFFFFFF)
                        assert server.ping(data) == data
                    queue.put(True)
                except Exception:
                    logging.exception("Error occurred during pinging server")
                    queue.put(False)

            q = Queue.Queue()
            threads = []
            for x in xrange(10):
                th = threading.Thread(target=ping_server, args=(q, ))
                th.start()
                threads.append(th)

            res = True
            for x in xrange(q.qsize()):
                res &= q.get(timeout=3)
            map(threading.Thread.join, threads)
            if not res:
                raise errors.SandboxTaskFailureError("Threading error. See logs for more info")

        if self.ctx[self.CreateResources.name]:
            file_resource = self.create_resource(self.descr, 'lifetime.log', 'TEST_TASK_RESOURCE')
            with open(file_resource.path, 'w') as resource_file:
                resource_file.write('Some test data')

            folder_resource = self.create_resource(self.descr, 'directory_with_non_ascii', 'TEST_TASK_RESOURCE')
            paths.make_folder(folder_resource.path)
            logging.info('write file1привет.txt')
            with open(os.path.join(folder_resource.path, 'file1привет.txt'), 'w') as resource_file:
                resource_file.write('Some test data in file1привет.txt')

            folder_resource = self.create_resource(self.descr, 'directory_resource', 'TEST_TASK_RESOURCE_2')
            paths.make_folder(folder_resource.path)
            logging.info('write file1')
            with open(os.path.join(folder_resource.path, 'file1'), 'w') as resource_file:
                resource_file.write('Some test data in file1')
            logging.info('write file2')
            with open(os.path.join(folder_resource.path, 'file2'), 'w') as resource_file:
                resource_file.write('Some test data in file2')

        with self.memoize_stage.mark_ready:
            if self.ctx.get(self.CreateResourceOnEnqueue.name):
                on_enq_path = self.abs_path('on_enqueue_resource')
                with open(on_enq_path, "w") as f:
                    f.write("blah")
                self.mark_resource_ready(self.ctx['created_resource_on_enqueue'])

        if self.ctx[self.ParentResourceId.name] and self.parent_id:
            parent_resource_id = self.ctx[self.ParentResourceId.name]
            parent_resource_path = channel.channel.sandbox.get_resource(parent_resource_id).file_name
            kwargs = {}
            if self.ctx[self.SaveParentResourceBasename.name]:
                parent_resource_path += '_basename'
                kwargs = {'save_basename': True}
            with open(parent_resource_path, 'w') as resource_file:
                resource_file.write('Some test data for parent resource')
            self.save_parent_task_resource(parent_resource_path, self.ctx[self.ParentResourceId.name], **kwargs)

        if self.ctx[self.CreateEmptyResource.name]:
            self.create_resource(self.descr, 'empty_resource', 'TEST_TASK_RESOURCE')

        wait_time = int(self.ctx.get(self.WaitTime.name, 0))
        if wait_time and not self.ctx.get('waited_time'):
            self.ctx['waited_time'] = True
            self.wait_time(wait_time)

        if self.ctx[self.CreateSubtask.name]:
            if not self.ctx.get('subtask_ids'):
                logging.info('Create a subtasks')
                self.ctx['subtask_ids'] = []
                sub_task_context = copy.deepcopy(self.ctx)
                sub_task_context[self.CreateSubtask.name] = False
                for key in sub_task_context.keys():
                    if key.startswith("_"):
                        del sub_task_context[key]
                for i in range(self.NumberOfSubtasks.cast(self.ctx[self.NumberOfSubtasks.name])):
                    if self.ctx[self.CreateParentResources.name]:
                        pres = self.create_resource(
                            "Parent resource {}".format(i),
                            "res-{}.txt".format(i),
                            "TEST_TASK_RESOURCE"
                        )
                        sub_task_context[self.ParentResourceId.name] = pres.id

                    subtask = self.create_subtask(
                        task_type=self.type, input_parameters=sub_task_context,
                        description='Child of test task %s' % self.id,
                        inherit_notifications=self.ctx[self.InheritNotifications.name]
                    )
                    self.ctx['subtask_ids'].append(subtask.id)

                self.ctx['wait_all_tasks'] = True
                if len(self.ctx['subtask_ids']) > 1:
                    self.wait_any_task_completed(self.ctx['subtask_ids'])
                else:
                    self.wait_task_completed(self.ctx['subtask_ids'][0])
            else:
                if self.ctx.get('wait_all_tasks'):
                    self.ctx['wait_all_tasks'] = False
                    self.wait_all_tasks_completed(self.ctx['subtask_ids'])
                else:
                    for task_id in self.ctx['subtask_ids']:
                        task = channel.channel.sandbox.get_task(task_id)
                        logging.info('Subtask #{0} status: {1}'.format(task.id, task.status))
            return

        test_get_arcadia_url = self.ctx.get(self.TestArcadiaURL.name)
        if test_get_arcadia_url:
            logging.info('Test getting arcadia repo from cache, url {0}'.format(test_get_arcadia_url))
            test_get_arcadia_path = svn.Arcadia.get_arcadia_src_dir(test_get_arcadia_url)
            logging.info('Arcadia repo path {0}:\n{1}'.format(test_get_arcadia_path,
                                                              os.listdir(test_get_arcadia_path)))

        logging.info('make temp folder')
        if not os.path.exists(self.abs_path('temp')):
            os.mkdir(self.abs_path('temp'))
            with open(self.abs_path('temp', 'temp.txt'), 'w') as temp_file:
                temp_file.write('abracadabra')
        logging.info('create some files in task directory')
        some_file = open(self.abs_path('some_test_file'), 'w')
        some_file.write('sdfsdfsfsf')
        some_file.close()
        logging.info('create another file in task directory')
        another_file = open(self.abs_path('another_test_file'), 'w')
        another_file.write('another_file content \n \t\n \t sfsdf ')
        another_file.close()

        vault_item_owner = self.ctx.get(self.VaultItemOwner.name) or self.owner
        if self.ctx[self.CheckSsh.name]:
            with ssh.Key(self, vault_item_owner, self.ctx[self.VaultItemName.name]):
                pass

        resource_id = self.ctx[self.DependentResource.name]
        if resource_id:
            logging.info('dependent resource: %r', resource_id)
            if self.ctx[self.SyncInSubprocess.name]:
                pr = self._subprocess(
                    [str(self.synchrophazotron), str(resource_id)],
                    wait_timeout=3600,
                    keep_filehandlers=True,
                    log_prefix="synchrophazotron",
                )
                with open(pr.stdout.name, 'r') as fh:
                    dependent_resource_path = fh.read().strip()
                pr.stdout.close()
                pr.stderr.close()
            else:
                dependent_resource_path = self.sync_resource(self.ctx[self.DependentResource.name])

            logging.info("Dependent resource path: %r", dependent_resource_path)
            if os.path.isfile(dependent_resource_path):
                with open(dependent_resource_path, 'rb') as f:
                    logging.info(f.read())
            if self.ctx.get(self.ModifyResource.name):
                if os.path.isfile(dependent_resource_path):
                    with open(dependent_resource_path, 'a') as f:
                        f.write('test modification')
                else:
                    with open(os.path.join(dependent_resource_path, 'new_file.mdf'), 'w') as f:
                        f.write('test modification')

        if self.ctx[self.LiveTime.name]:
            sleep = self.ctx[self.LiveTime.name]
            msg = "Sleeping for %.2fs" % sleep
            logging.info(msg)
            with self.current_action(msg):
                if self.ctx[self.NoTimeout.name]:
                    with sdk2.helpers.NoTimeout():
                        time.sleep(sleep)
                else:
                    time.sleep(sleep)

        if self.ctx[self.UseCGroup.name]:
            cg = common.os.CGroup("test_task")
            cg.memory["low_limit_in_bytes"] = 16911433728
            cg.memory["limit_in_bytes"] = 21421150208
            cg.cpu["smart"] = 1
            cmd = ["/bin/sleep", str(self.ctx["kill_timeout"])]
            logging.info("Running %r in %r", cmd, cg)
            p = process.run_process(cmd, wait=False, preexec_fn=cg.set_current)
            logging.info("Process started in %r", list(common.os.CGroup(pid=p.pid)))

        if self.ctx.get(self.Suspend.name):
            self.suspend()

        go_to_state = self.ctx[self.GoToState.name]
        exception_classes = {
            ctt.Status.FAILURE: common.errors.TaskFailure,
            ctt.Status.EXCEPTION: common.errors.TaskError,
            ctt.Status.TEMPORARY: common.errors.TemporaryError,
        }
        if go_to_state in exception_classes:
            if go_to_state not in ctt.Status.Group.FINISH:
                self.ctx[self.GoToState.name] = ctt.Status.SUCCESS
            exception_class = exception_classes[go_to_state]
            raise exception_class(
                "{} was raised. The task state should be {}.".format(exception_class.__name__, go_to_state)
            )

        if self.ctx[self.CreateIndependentTask.name]:
            task_fields = {
                'type_name': 'TEST_TASK',
                'owner': self.author,
                'descr': 'Created from TEST_TASK <{}> for test user inherit'.format(self.id),
                'priority': ("SERVICE", "HIGH")
            }
            self.ctx['independent_task_id'] = channel.channel.sandbox.server.create_task(task_fields)

        if self.ctx[self.SendEmail.name]:
            self.ctx['email_notification_id'] = channel.channel.sandbox.send_email(
                self.ctx[self.EmailRecipient.name],
                None,
                "Test email from TestTask #{}".format(self.id),
                "Email body",
                urgent=self.ctx[self.MarkAsUrgent.name],
            )

        tasks = channel.channel.sandbox.list_tasks(parent_id=self.id)
        logging.info("Tasks: %s", tasks)
