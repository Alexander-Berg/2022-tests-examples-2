import hashlib
import json
import base64
import logging
import time

from sandbox import sdk2
import sandbox.common.types.task as ctt
import sandbox.common.types.misc as ctm
import sandbox.common.types.notification as ctn
import sandbox.common.errors as errors

from .. import common as eviction


bad_events = [
    ctt.Status.NOT_RELEASED,
    ctt.Status.FAILURE,
    ctt.Status.DELETED,
    ctt.Status.Group.BREAK
]


VM_STOP_BEFORE_VMAGENT_UPDATE_TIMEOUT = 600
VM_AGENT_UPDATE_TIMEOUT = 1800

VM_START_CHECK_REMOVED_AFTER = 60  # check if vm was removed (HTTP404) after 60 seconds
VM_START_WAIT_RUNNING_STATE = 3600  # how much time to wait VM to reach "RUNNING" state


class QypEvacuateTest(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 86400 * 14
        pod_id = sdk2.parameters.String('Pod id', required=True)
        vmproxy_dc = sdk2.parameters.String(
            'VMProxy DC', required=True,
            choices=[
                ('sas', 'sas'),
                ('vla', 'vla'),
                ('man', 'man'),
                ('myt', 'myt'),
                ('iva', 'iva'),
                ('test', 'test'),
            ]
        )
        do_not_check_vmagent = sdk2.parameters.Bool(
            'Do not check vmagent version', required=True, default=False
        )

        notifications = [
            # Bad events
            sdk2.Notification(
                [
                    ctt.Status.ENQUEUED,
                    ctt.Status.Group.FINISH
                ] + bad_events,
                ['mocksoul', 'golomolzin', 'frolstas'],
                ctn.Transport.EMAIL
            ),

            # Only very bad events
            sdk2.Notification(
                bad_events,
                ['mocksoul', 'golomolzin', 'frolstas'],
                ctn.Transport.TELEGRAM
            )
        ]

    class Requirements(sdk2.Task.Requirements):
        semaphores = ctt.Semaphores(
            acquires=[
                ctt.Semaphores.Acquire(
                    name='QYP_EVACUATE_TEST_PARALLEL',
                    weight=1
                ),
            ],
            release=(ctt.Status.Group.BREAK, ctt.Status.Group.FINISH)
        )

    def on_execute(self):
        yp_oauth = sdk2.Vault.data('yp_oauth_token')
        vmproxy_oauth = sdk2.Vault.data('vmproxy_oauth_token')
        tvm_secret = sdk2.Vault.data('tvm_secret')

        qnotifier_tvm_src = 2010204
        qnotifier_tvm_dst = 2002376

        pod_id = self.Parameters.pod_id
        dc = self.Parameters.vmproxy_dc
        do_not_check_vmagent = self.Parameters.do_not_check_vmagent

        qnotifier_tags = ['qyp', 'evacuate', 'yp:id:%s' % (pod_id, )]

        notify_steps = [
            ['Turn off machine', None],
            ['Update VM agent', None],
            ['Make backup', None],
            ['Prepare new OS image from backup', None],
            ['Send acknowledge eviction request', None],
            ['Wait VM eviction', None],
            ['New machine is ready to use', None]
        ]

        def _set_backup_step(num, state=True):
            for step_info in notify_steps:
                step_info[1] = None
            notify_steps[num - 1][1] = state

            self.set_info('Step: %s [state %s]' % (notify_steps[num - 1][0], 'ok' if state else 'FAIL'))

        # Create /labels/qyp/eviction if not exists
        eviction.init_qyp_eviction_label(dc, yp_oauth, pod_id)

        pods = eviction.select_pods(dc, yp_oauth, '[/meta/id] = "%s"' % (pod_id, ), filter_node_status=False)
        assert len(pods) == 1
        podinfo = pods[0]

        def _notify_user(extra=None):
            return eviction.eviction_notify(
                (tvm_secret, qnotifier_tvm_src, qnotifier_tvm_dst), qnotifier_tags,
                self.id, notify_steps, podinfo, extra
            )

        try:
            vmagent_version = podinfo['labels']['vmagent_version']
            if vmagent_version:
                vmagent_version_list = [int(x) for x in vmagent_version.split('.', 2)]
                if len(vmagent_version_list) == 2:
                    vmagent_version_list.append(0)
            else:
                vmagent_version_list = [0, 0, 0]
        except Exception as ex:
            logging.warning('Unable to get current vmagent version: %s', ex)
            vmagent_version = None
            vmagent_version_list = []

        logging.info('Updating backups count for eviction by increasing last count')
        evacuation_backups_count = eviction.get_pod_eviction_label(dc, yp_oauth, pod_id, '/backup_count') or 0
        evacuation_evictions_count = eviction.get_pod_eviction_label(dc, yp_oauth, pod_id, '/eviction_count') or 0

        if self.Context.backup_sandbox_task is ctm.NotExists:
            if not do_not_check_vmagent:
                if not vmagent_version_list or vmagent_version_list < [0, 10, 0]:
                    logging.info(
                        'VM agent is too old! Got v%s',
                        vmagent_version
                    )
                    raise errors.TaskFailure('VM agent is too old (%s)' % (vmagent_version or 'unknown', ))

            if not vmagent_version_list or vmagent_version_list < [0, 26, 0]:
                if vmagent_version_list:
                    _set_backup_step(2)  # update vmagent
                    _notify_user([
                        'Updating VM agent from v%s to latest version' % (vmagent_version, )
                    ])

                logging.info(
                    'We need to update vmagent first (current is %r %r)',
                    vmagent_version, vmagent_version_list
                )
                vm_state = eviction.vmproxy_get_status(dc, pod_id, vmproxy_oauth)
                vm_spec = eviction.vmproxy_get_vmspec(dc, pod_id, vmproxy_oauth)
                vm_spec['updateVmagent'] = True

                if vm_state['state']['type'] != 'STOPPED':
                    logging.info(
                        'VM state is "%s", we need to stop it before vmagent update',
                        vm_state['state']['type']
                    )
                    eviction.vmproxy_stop_vm(dc, pod_id, vmproxy_oauth)

                    deadline = time.time() + VM_STOP_BEFORE_VMAGENT_UPDATE_TIMEOUT
                    while time.time() < deadline:
                        vm_state = eviction.vmproxy_get_status(dc, pod_id, vmproxy_oauth)
                        if vm_state and vm_state['state']['type'] == 'STOPPED':
                            logging.info('VM stopped, continuing')
                            break
                        else:
                            if vm_state:
                                logging.debug('VM state still "%s"...', vm_state['state']['type'])
                            else:
                                logging.debug('Unable to get vmstate')
                            time.sleep(5)
                    else:
                        raise errors.TaskFailure('Unable to stop VM before updating vmagent')

                logging.info('Issuing updateVmagent request...')
                result = eviction.vmproxy_update_vm(dc, vm_spec, vmproxy_oauth)

                if result is False:
                    raise errors.TaskFailure('Unable to update vmagent')

                deadline = time.time() + VM_AGENT_UPDATE_TIMEOUT

                while time.time() < deadline:
                    if not eviction.vmproxy_get_status(dc, pod_id, vmproxy_oauth):
                        logging.debug('VMagent is not alive yet, waiting...')
                        time.sleep(5)
                    else:
                        logging.info('VMagent update success!')
                        break
                else:
                    _set_backup_step(2, False)  # update vmagent
                    _notify_user([
                        'We were unable to update vmagent, evacuation process halted.',
                        'Evacuation will be retried later.'
                    ])
                    raise errors.TaskFailure('Failed to update vmagent')

                # We need again to create eviction labels, because VmUpdate somehow removes them
                eviction.init_qyp_eviction_label(dc, yp_oauth, pod_id)

            logging.info('Backup task was not scheduled yet -- do it now')
            eviction.update_pod_eviction_label(dc, yp_oauth, pod_id, evacuation_backups_count + 1, '/backup_count')
            backup_sandbox_task = eviction.make_vbox_backup_sandbox_task(dc, pod_id, vmproxy_oauth)
            self.Context.backup_sandbox_task = backup_sandbox_task

            _set_backup_step(3)  # schedule backup
            _notify_user([
                'We already scheduled backup (https://sandbox.yandex-team.ru/task/%d/view '
                'and waiting for it to finish.' % (backup_sandbox_task, )
            ])

            self.set_info(
                'Scheduled backup task: <a href="https://sandbox.yandex-team.ru/task/%d/view">%d</a>' % (
                    backup_sandbox_task, backup_sandbox_task
                ),
                do_escape=False
            )
        else:
            logging.info('Backup task was already scheduled (id=%r)', self.Context.backup_sandbox_task)
            backup_sandbox_task = self.Context.backup_sandbox_task

            self.set_info(
                'Waiting old backup task: <a href="https://sandbox.yandex-team.ru/task/%d/view">%d</a>' % (
                    backup_sandbox_task, backup_sandbox_task
                ),
                do_escape=False
            )

        # backup_sandbox_task = 378825545  # MERGE_QEMU_IMAGE
        # backup_sandbox_task = 636  # MERGE_QEMU_IMAGE

        logging.debug('WAITING...')

        task = sdk2.Task.find(id=backup_sandbox_task).limit(1).first()
        if task is None:
            raise errors.TaskFailure('Unable to find backup task %d' % (backup_sandbox_task, ))

        while task.status not in ctt.Status.Group.FINISH:
            raise sdk2.WaitTask([task.id], ctt.Status.Group.FINISH, wait_all=True)

        if task.status != ctt.Status.SUCCESS:
            _set_backup_step(3, False)
            _notify_user([
                'Backup sandbox task (https://sandbox.yandex-team.ru/task/%d/view) was failed.' % (
                    backup_sandbox_task,
                ),
                'Evacuation halted, but will be retried later.'
            ])
            raise errors.TaskFailure('Backup task #%d failed with status %s' % (task.id, task.status))

        if task.type.name == 'BACKUP_QEMU_VM' and task.Parameters.storage == 'QDM':
            resid = task.Parameters.result_url
        else:
            if task.type.name == 'BACKUP_QEMU_VM':
                resource = None

                for subtask in task.find():
                    if subtask.type.name == 'COPY_VM_IMAGE':
                        resource = sdk2.Resource.find(task_id=subtask.id, type='OTHER_RESOURCE').first()
                        break
                    elif subtask.type.name == 'MERGE_QEMU_IMAGE':
                        resource = sdk2.Resource.find(task_id=subtask.id, type='QEMU_MERGED_IMAGE').first()
                        break
                    else:
                        raise errors.TaskFailure('Unknown backup subtask type %s' % (subtask.type.name, ))

                if not resource:
                    raise errors.TaskFailure('Unable to load backup task resource')
            else:
                raise errors.TaskFailure('Unknown backup task type %s' % (task.type.name, ))

            resid = resource.skynet_id

            if not resid:
                raise errors.TaskFailure('Unable to find skynet skybone resource id (rbtorrent)')

        self.set_info('Backup resource ready: %s' % (resid, ))

        yp_client = eviction.YpClient(dc, yp_oauth)
        resources_pod = yp_client.get_object('pod', pod_id, ['/spec/iss/instances/0/entity/instance/resources'])
        resources_pod = resources_pod.json()['results'][0]['values'][0]
        idx_config = [idx for idx, item in enumerate(resources_pod) if item['key'] == 'vm.config'][0]
        old_url = resources_pod[idx_config]['value']['resource']['urls'][0]
        old_url = old_url.split('data:text/plain;charset=utf-8;base64,')[1]
        decoded_dict = json.loads(base64.b64decode(old_url))
        decoded_dict['disk']['deltaSize'] = 0
        decoded_dict['disk']['resource']['rbTorrent'] = resid
        decoded_dict['disk']['type'] = 'RAW'
        decoded_dict['disk']['path'] = '/'
        new_url = 'data:text/plain;charset=utf-8;base64,{}'.format(base64.b64encode(json.dumps(decoded_dict)))
        resources_pod[idx_config]['value']['resource']['urls'][0] = new_url
        resources_pod[idx_config]['value']['resource']['uuid'] = hashlib.sha1(new_url).hexdigest()

        self.set_info('Send request acknowledge eviction')
        _set_backup_step(5)
        try:
            yp_client.acknowledge_eviction('pod', pod_id, resources_pod)
        except Exception:
            _set_backup_step(5, False)
            raise errors.TaskFailure('Unable acknowledge eviction for pod %s' % (pod_id, ))
        self.set_info('Request acknowledge eviction successful: OK')

        _set_backup_step(6)
        while True:
            request = yp_client.get_object('pod', pod_id, ['/status/eviction/state'])
            state_eviction = request.json()['results'][0]['values'][0]
            if state_eviction == 'none':
                break
            time.sleep(10)
        self.set_info('VM eviction successful')

        check_404_at = time.time() + VM_START_CHECK_REMOVED_AFTER
        wait_running_state_deadline = None

        state_ok, http_code, vm_state = eviction.vmproxy_get_status(dc, pod_id, vmproxy_oauth, extended=True)
        target_state = 'RUNNING' if vm_state.get('config', {}).get('autorun', True) else 'CONFIGURED'

        self.set_info('Target state: %s, waiting' % (target_state, ))

        while True:
            state_ok, http_code, vm_state = eviction.vmproxy_get_status(dc, pod_id, vmproxy_oauth, extended=True)

            if state_ok:
                if wait_running_state_deadline is None:
                    wait_running_state_deadline = time.time() + VM_START_WAIT_RUNNING_STATE

                if vm_state['state']['type'] == target_state:
                    pods = eviction.select_pods(
                        dc, yp_oauth, '[/meta/id] = "%s"' % (pod_id, ), filter_node_status=False
                    )
                    assert len(pods) == 1
                    podinfo_new = pods[0]

                    _set_backup_step(7)  # machine running

                    if target_state == 'RUNNING':
                        _notify_user([
                            'Your machine is evacuated, up and running. Everything went fine!',
                            'Persistent hostname will be the same (%s)' % (podinfo['fqdn'][1], ),
                            'Transient hostname changed:',
                            '  old: %s' % (podinfo['fqdn'][0], ),
                            '  new: %s' % (podinfo_new['fqdn'][0], )
                        ])
                    else:
                        _notify_user([
                            'Your machine is evacuated, but didnt started, because you set autorun=False.',
                            'You need to start it manually.',
                            'Persistent hostname will be the same (%s)' % (podinfo['fqdn'][1], ),
                            'Transient hostname changed:',
                            '  old: %s' % (podinfo['fqdn'][0], ),
                            '  new: %s' % (podinfo_new['fqdn'][0], )
                        ])

                    # Create /labels/qyp/eviction if not exists
                    eviction.init_qyp_eviction_label(dc, yp_oauth, pod_id)

                    logging.info('Updating eviction count by increasing last count')
                    eviction.update_pod_eviction_label(
                        dc, yp_oauth, pod_id, evacuation_evictions_count + 1, '/eviction_count'
                    )

                    self.set_info('All done!')
                    return
                elif time.time() < wait_running_state_deadline:
                    # Got HTTP200 OK, but state is not running yet
                    logging.debug('VM is not ready yet, state: %r', vm_state)
                else:
                    # Give up waiting
                    extra_info = vm_state['state'].get('info', None)
                    if extra_info:
                        info_str = ' (%s)' % (extra_info, )
                    else:
                        info_str = ''
                    raise errors.TaskFailure(
                        'Bad vm state: %s%s (we wait %d seconds)' % (
                            vm_state['state']['type'], info_str,
                            VM_START_WAIT_RUNNING_STATE
                        )
                    )
            else:
                if time.time() > check_404_at and http_code == 404:
                    logging.info('VM was removed (got 404)')
                    raise errors.TaskFailure('VM was removed during evacuation (didnt started completely)')

                logging.debug('VM is not ready yet, state: %r', vm_state)

                message = vm_state.get('message', 'unknown') if isinstance(vm_state, dict) else 'unknown'

                if 'Could not compute pod allocation' in message:
                    raise errors.TaskFailure('Unable to allocate new VM (code %r): "%s"' % (http_code, message))

            time.sleep(10)
