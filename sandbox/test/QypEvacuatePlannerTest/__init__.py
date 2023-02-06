from __future__ import print_function

import logging
from sandbox import sdk2
import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn

from .. import common as eviction
from ..QypEvacuateTest import QypEvacuateTest


bad_events = [
    ctt.Status.NOT_RELEASED,
    ctt.Status.FAILURE,
    ctt.Status.DELETED,
    ctt.Status.Group.BREAK  # exception, timeout, stopped, expired, no_res
]
DC_LIST = ('test', 'vla', 'sas', 'man', 'myt', 'iva')


class QypEvacuatePlannerTest(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        dryrun = sdk2.parameters.Bool(
            'Dry run (dont run evacuate tasks)', required=True, default=False
        )

        notifications = [
            # Bad events
            sdk2.Notification(
                bad_events,
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

    def on_execute(self):
        yp_oauth = sdk2.Vault.data('yp_oauth_token')
        dryrun = self.Parameters.dryrun

        for dc in DC_LIST:
            pods_for_eviction = eviction.get_pods_for_eviction(dc, yp_oauth_token=yp_oauth, production=False)

            pod_ids_by_node = {}
            for pod_info in pods_for_eviction:
                pod_ids_by_node.setdefault(pod_info['node_id'], {})[pod_info['id']] = (
                    None, None, None  # task, enqueued, status
                )

            info_text = ['[%s] Need to evacuate:' % (dc, )]

            for pod_info in pods_for_eviction:
                logging.info('Need to evacuate pod "%s" (%s)', pod_info['id'], pod_info['node_id'])

                evacuate_task_id = eviction.get_pod_eviction_label(dc, yp_oauth, pod_info['id'], '/sb_task')

                if evacuate_task_id:
                    logging.debug('Found evacuation task id %r', evacuate_task_id)
                    evacuate_task = QypEvacuateTest.find(id=evacuate_task_id).limit(1).first()

                    if not evacuate_task:
                        logging.info('Unable to find old evacuate task (got %r)', evacuate_task)
                    else:
                        if evacuate_task.status not in ctt.Status.Group.FINISH:
                            logging.info('Current evacuate task not in finished state, wait it')
                            pod_ids_by_node[pod_info['node_id']][pod_info['id']] = (
                                evacuate_task_id, False, evacuate_task.status
                            )
                            continue
                        else:
                            logging.info(
                                'Current evacuate task in finished state, but we stil want '
                                'to schedule evacuation, do it now'
                            )

                if not dryrun:
                    eviction.init_qyp_eviction_label(dc, yp_oauth, pod_info['id'])
                    evacuate_task = QypEvacuateTest(
                        None,
                        description='QYP evacuation task of pod "%s" from node "%s"' % (
                            pod_info['id'], pod_info['node_id']
                        ),
                        owner=self.owner,
                        pod_id=pod_info['id'],
                        vmproxy_dc=dc
                    )

                    evacuate_task.save()
                    eviction.update_pod_eviction_label(dc, yp_oauth, pod_info['id'], evacuate_task.id, '/sb_task')
                    evacuate_task.enqueue()

                    pod_ids_by_node[pod_info['node_id']][pod_info['id']] = (evacuate_task.id, True, 'new')
                else:
                    pod_ids_by_node[pod_info['node_id']][pod_info['id']] = (None, None, None)

            if pod_ids_by_node:
                for node, pods in pod_ids_by_node.items():
                    info_text.append('  %s:' % (node, ))

                    for pod_id, (task_id, enqueued, task_status) in pods.items():
                        if task_id:
                            if enqueued:
                                info_text.append('    %s [<a href="/task/%d">%d</a> (%s)]' % (
                                    pod_id, task_id, task_id, task_status
                                ))
                            else:
                                info_text.append('    %s [<a href="/task/%d">%d</a> (%s, already exist)]' % (
                                    pod_id, task_id, task_id, task_status
                                ))
                        else:
                            info_text.append('    %s' % (pod_id, ))

                    info_text.append('')

                self.set_info('<br/>'.join(info_text),  do_escape=False)
            else:
                self.set_info('[%s] No pods needed evacuation found' % (dc, ))

        if dryrun:
            logging.info('DRYRUN MODE: NO TASKS WERE MADE')
