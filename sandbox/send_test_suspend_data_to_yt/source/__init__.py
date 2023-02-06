from sandbox import sdk2
from sandbox.projects.cloud.billing.common.task import SmallTask
from sandbox.sandboxsdk import environments


class SendTestSuspendDataToYt(SmallTask):
    """ Task to send test data from data-vault to yt table """

    class Parameters(SmallTask.Parameters):
        yt_cluster = sdk2.parameters.String(
            'Destination YT cluster',
            default='hahn',
            required=True
        )
        yt_token_name = sdk2.parameters.String(
            'YT Token secret name',
            required=True
        )
        dst_table_path = sdk2.parameters.String(
            'YT Path for destination Table',
            required=True
        )
        data_vault_name = sdk2.parameters.String(
            'Name of secret with data',
            required=True
        )

    class Requirements(SmallTask.Requirements):
        environments = (
            environments.PipEnvironment('yandex-yt'),
            environments.PipEnvironment('yandex-yt-yson-bindings-skynet')
        )

    def on_execute(self):
        from cloud.billing.utils.scripts.upload_test_data_to_yt import upload_test_data_to_yt
        upload_test_data_to_yt(
            yt_cluster=self.Parameters.yt_cluster,
            yt_token=sdk2.Vault.data(self.owner, self.Parameters.yt_token_name),
            dst_table_path=self.Parameters.dst_table_path,
            data=sdk2.Vault.data(self.owner, self.Parameters.data_vault_name)
        )
