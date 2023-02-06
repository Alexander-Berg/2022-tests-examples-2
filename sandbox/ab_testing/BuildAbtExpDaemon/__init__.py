# -*- coding: utf-8 -*-

from sandbox.projects.ab_testing import EXP_DAEMON_EXECUTABLE
from sandbox.projects.common.build.CommonBuildTask import CommonBuildTask
import sandbox.projects.common.constants as consts
from sandbox.projects.common.nanny import nanny
from sandbox.projects.common import utils


class BuildAbtExpDaemon(nanny.ReleaseToNannyTask, CommonBuildTask):
    '''
        Build expdaemon binary
    '''
    type = 'BUILD_ABT_EXP_DAEMON'

    def arcadia_info(self):
        rev = utils.svn_revision(self.ctx.get(consts.ARCADIA_URL_KEY, '')) or 'UNKNOWN REVISION'
        return rev, 'ExpDaemon r' + rev, 'trunk'

    def on_execute(self):
        CommonBuildTask.on_execute(self)

    TARGET_RESOURCES = (
        (EXP_DAEMON_EXECUTABLE, 'quality/ab_testing/exp_daemon/exp_daemon'),
    )


__Task__ = BuildAbtExpDaemon
