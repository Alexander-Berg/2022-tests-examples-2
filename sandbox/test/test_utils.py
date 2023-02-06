import logging
import yatest


logger = logging.getLogger("test_logger")

from sandbox.projects.mobile_apps.teamcity_sandbox_runner.utils.vcs import get_config, read_config


def test_read_config():
    '''
    Test purpose:  Read and validate config
    '''
    logger.info("Reading config and resolve composite variable")
    loaded_data_path = yatest.common.source_path(
        'sandbox/projects/mobile_apps/teamcity_sandbox_runner/utils/vcs/test/test_util.yaml')
    loaded_data = get_config(loaded_data_path)
    config, sha1_hash = read_config(config_from_repository=False, config_path='', config_for_launcher=False,
                                    config_str=loaded_data, dependent_templates='')
    logger.info("GRADLE_ROOT is {}".format(config['stages']['assemble']['env']['GRADLE_ROOT']))
    assert config['stages']['assemble']['env']['GRADLE_ROOT'] == '%env.BUILDSCRIPTS_ROOT%/BBBB'
