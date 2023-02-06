import datetime
import logging
import api.copier.errors as copier_errors
import sandbox.common.share as common_share
from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.projects.adfox.resource_types import AdfoxArchivedAtlasCacheFile


class AdfoxKeepAtlasCache(sdk2.Task):

    class Requirements(sdk2.Requirements):
        environments = [environments.PipEnvironment('yandex-yt')]

    class Parameters(sdk2.Task.Parameters):
        bstr_yt_path = sdk2.parameters.String("Path to bstr dir on yt", default="//home/adfox/bridge/deploy-production/bstr", required=True)
        yt_proxy = sdk2.parameters.String("YT proxy", default="locke", required=True)
        yt_token_yav = sdk2.parameters.YavSecret("YAC secret with yt_token", required=True)

    def on_execute(self):
        self.download_cache()

    def download_cache(self):
        import yt.wrapper

        yt_token = self.Parameters.yt_token_yav.data()["yt_token"]
        client = yt.wrapper.YtClient(proxy=self.Parameters.yt_proxy, token=yt_token)

        while True:
            amacs_cache_name = client.list(self.Parameters.bstr_yt_path)[0]
            amacs_cache_path = self.Parameters.bstr_yt_path + "/" + amacs_cache_name
            rbtorrent_attribute_path = amacs_cache_path + "/@_bstr_info/torrent"
            rbtorrent = client.get(rbtorrent_attribute_path)

            try:
                common_share.skynet_get(rbtorrent, ".")
            except copier_errors.CopierError as e:
                logging.exception("Cannot download resource with id %s. Exception %s", rbtorrent, e)
                continue

            AdfoxArchivedAtlasCacheFile(self, str(datetime.datetime.now()), amacs_cache_name + ".zstd")
            break
