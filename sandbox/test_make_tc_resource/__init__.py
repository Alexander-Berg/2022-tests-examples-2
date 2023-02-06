import logging
import shutil
import time

from sandbox import sdk2

from sandbox.projects.browser_mobile.abro.BrowserAndroidTaskBase import (BrowserAndroidApkResource)
from sandbox.projects.common.teamcity import TeamcityArtifacts


class TestMakeTcResource(sdk2.Task):
    """ TestMakeTcResource """

    class Parameters(sdk2.Parameters):
        target_task = sdk2.parameters.Task("Target task", required=True)
        _container = sdk2.parameters.Container("Container", default=None, required=True)

    def on_execute(self):
        time.sleep(100500)
        res = TeamcityArtifacts(self, 'Teamcity artifacts', 'teamcity_artifacts', ttl=3)
        data = sdk2.ResourceData(res)
        data.path.mkdir(0o755, parents=True)

        # Copy apks from child tasks.
        apks_path = data.path.joinpath('apks')
        apks_path.mkdir(0o755, parents=True)

        child_task = self.Parameters.target_task
        # Limit must be explicitly specified.
        for apk_res in BrowserAndroidApkResource.find(task=child_task).limit(100):  # type: BrowserAndroidApkResource
            logging.info('apk_res: %s', str(apk_res))
            logging.info('apk_res.path: %s', str(apk_res.path))
            logging.info('apk_res.description: %s', str(apk_res.description))

            # Synchronize resource data to local disk.
            apk_data = sdk2.ResourceData(apk_res)
            shutil.copy2(str(apk_data.path), str(apks_path.joinpath(apk_data.path.name)))

        data.ready()
