# -*- coding: utf-8 -*-

from sandbox.projects.ab_testing import SESSION_MANAGER_RPC_EXECUTABLE
from sandbox.projects.common.build.CommonBuildTask import CommonBuildTask
import sandbox.projects.common.constants as consts
from sandbox.projects.common.nanny import nanny
from sandbox.projects.common import utils


class BuildSessionManagerRpc(nanny.ReleaseToNannyTask, CommonBuildTask):
    '''
        Build expcookier binary
    '''
    type = 'BUILD_SESSION_MANAGER_RPC'

    def arcadia_info(self):
        rev = utils.svn_revision(self.ctx.get(consts.ARCADIA_URL_KEY, '')) or 'UNKNOWN REVISION'
        return rev, 'SessionManagerRpc r' + rev, 'trunk'

    def on_execute(self):
        CommonBuildTask.on_execute(self)

    TARGET_RESOURCES = (
        (SESSION_MANAGER_RPC_EXECUTABLE, 'quality/ab_testing/sessions_analysis/sessions_viewer/session_viewer_rpc/session_viewer_rpc'),
    )


__Task__ = BuildSessionManagerRpc
