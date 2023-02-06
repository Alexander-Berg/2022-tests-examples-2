import datetime
from sandbox.sdk2 import parameters
from sandbox.projects.yabs.base_bin_task import BaseBinTask


DAY = 86400


class PrebillingRemoveOldRunDirs(BaseBinTask):
    class Parameters(BaseBinTask.Parameters):
        description = 'remove useless dirs'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'PrebillingB2B'})

        secret_name = parameters.YavSecret(
            'yav secret id',
            default='sec-01eqfz6a8j1rqs267tfn54hbg5'
        )
        yt_cluster = parameters.String(
            'YT dst cluster',
            default='freud',
        )
        dirs_to_clear = parameters.String(
            'Backup directory path',
            default='//home/yabs/stat/tmp/bykovdmitrii/b2b',
        )

        min_num_days_to_delete = parameters.Integer(
            'min days from creation to delete',
            default=2,
        )

    def on_execute(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.secret_name.data()['yt_token']
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)
        now_dt = datetime.datetime.now()
        for table in ytc.list(self.Parameters.dirs_to_clear):
            creation_time = ytc.get("{}/{}/@creation_time".format(self.Parameters.dirs_to_clear, table))
            if (now_dt - datetime.datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds() > DAY * self.Parameters.min_num_days_to_delete:
                ytc.remove("{}/{}".format(self.Parameters.dirs_to_clear, table), recursive=True, force=True)
