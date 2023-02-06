from __future__ import print_function

import datetime
import json
import time

from dateutil.tz import tzlocal

from sandbox.sdk2 import (
    ResourceData,
    parameters,
)
from sandbox.projects.yabs.cpm_multiplier.resources import YabsCpmMultiplierYtBackup
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class YabsCpmMultiplierPrepareBackup(BaseBinTask):
    '''Creates backup of YT tables used by CPMMultiplier'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Backup YT tables'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsCpmMultiplierB2B'})

        with parameters.Group('Backup') as backup_params:
            yt_token_secret_id = parameters.YavSecret(
                label="YT token secret id",
                required=True,
                description='secret should contain keys: YT_TOKEN',
                default="sec-01dbk7b8f40jq2nh6ym7y0hhgh",
            )
            yt_cluster = parameters.String(
                'YT cluster',
                default='hahn',
                required=True,
            )
            tablet_cell_bundle = parameters.String(
                'Tablet cell bundle for dictionaries backup',
                default='default',
                required=True,
            )
            backup_base = parameters.String(
                'Backup directory path',
                default='//home/yabs/stat/cpm_multiplier/backup',
                required=True,
            )
            result_ttl = parameters.Integer(
                'Output ttl (days)',
                default=19,
            )
            link_path = parameters.String(
                'Path to link to latest CPMMultiplier table',
                default='//home/yabs/stat/cpm_multiplier/CPMMultiplier',
                required=True,
            )
            dictionaries = parameters.List(
                'Dictionaries to backup',
                default=[
                    'PartnerPage',
                    'Page',
                    'FormulaParameters',
                    'PageGroupExperiment',
                ],
                required=True,
            )
            stat_path = parameters.String(
                'Path to RtpPageStat table',
                required=True,
                default='//home/yabs/stat/RtbPageStat',
            )
            dict_path = parameters.String(
                'Path to dictionaries backups',
                required=True,
                default='//home/yabs/backup/hahn',
            )
            result_attrs = parameters.Dict(
                'Result resource attributes',
                default={},
            )

    def find_prev_path(self, ytc):
        if not ytc.exists(self.Parameters.link_path):
            return None

        prev_path = ytc.get_attribute(self.Parameters.link_path + '&', 'target_path', None)
        prev_path = '/'.join(prev_path.split('/')[:-1])
        return prev_path

    def backup_to_dynamic(self, ytc, src, dst):
        ytc.copy(src, dst)
        ytc.alter_table(dst, dynamic=True)
        ytc.set_attribute(dst, 'tablet_cell_bundle', self.Parameters.tablet_cell_bundle)
        ytc.mount_table(dst)

    def find_dict_path(self, ytc):
        dict_backups = ytc.list(self.Parameters.dict_path, absolute=True)
        return sorted(dict_backups)[-2]

    def create_resource(self, backup_description):
        backup_resource = ResourceData(
            YabsCpmMultiplierYtBackup(
                self,
                description='CPMMultiplier YT backup description',
                path='backup_description.json',
                **self.Parameters.result_attrs
            ),
        )
        backup_resource.path.write_bytes(json.dumps(backup_description))
        backup_resource.ready()

    def on_execute(self):
        import yt.wrapper as yt
        yt_token = self.Parameters.yt_token_secret_id.data()["YT_TOKEN"]
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)

        current_time = int(time.time())
        backup_description = {
            'current_time': current_time,
            'stat_time': current_time - 7200,
        }

        dest_path = '{}/{}'.format(self.Parameters.backup_base, self.id)
        ytc.remove(dest_path, recursive=True, force=True)
        ytc.create('map_node', dest_path, recursive=True)

        ts = datetime.datetime.now(tzlocal())
        ts += datetime.timedelta(days=self.Parameters.result_ttl)
        ytc.set_attribute(dest_path, 'expiration_time', ts.isoformat())

        # Previous run data
        prev_path = self.find_prev_path(ytc)
        dest_prev_path = None
        if prev_path is not None:
            dest_prev_path = '{}/previous'.format(dest_path)
            ytc.copy(prev_path, dest_prev_path)
        backup_description['previous_path'] = dest_prev_path

        # Dictionaries
        dest_dict_path = '{}/dict'.format(dest_path)
        ytc.create('map_node', dest_dict_path)

        dict_path = self.find_dict_path(ytc)
        for dict_name in self.Parameters.dictionaries:
            self.backup_to_dynamic(ytc, '{}/--home-yabs-dict-{}'.format(dict_path, dict_name), '{}/{}'.format(dest_dict_path, dict_name))
        backup_description['dict_path'] = dest_dict_path

        # RtbPageStat
        dest_stat_path = '{}/RtbPageStat'.format(dest_path)
        ytc.run_merge(self.Parameters.stat_path, dest_stat_path)  # Used only for MapReduce
        backup_description['stat_path'] = dest_stat_path

        self.create_resource(backup_description)
