# -*- coding: utf-8 -*-

import logging

import sandbox.projects.release_machine.security as rm_sec
from sandbox.projects.common.search import instance_resolver
from sandbox.projects.common.search import cluster_names as cn
from sandbox.projects.common.search import bugbanner
from sandbox.projects.common import error_handlers as eh


class TestInstanceResolver(bugbanner.BugBannerTask):
    """
        Production-class monitoring test for important cluster group names.
        See https://st.yandex-team.ru/SEARCH-4023 for details.
    """
    type = "TEST_INSTANCE_RESOLVER"

    execution_space = 256  # 256 Mb

    def on_execute(self):
        self.add_bugbanner(bugbanner.Banners.ReleaseMachine)

        self.set_info("Test resolving by itag...")
        test_group_name = "MSK_WIZARD_LINGVOBOOST_WIZARD"
        instances_by_itag = instance_resolver.get_instances_by_itag(test_group_name)
        logging.info("Instances by itag for %s", test_group_name)
        for instance in instances_by_itag:
            logging.info("    %s", instance)

        configuration_names = cn.get_all_configurations()
        vault_nanny_token = rm_sec.get_rm_token(self)
        for configuration_name in configuration_names:
            logging.info('Test configuration %s', configuration_name)
            self.set_info("Test configuration {} ...".format(configuration_name))
            try:
                nanny_token = vault_nanny_token if configuration_name in cn.get_nanny_configurations() else None
                instances = instance_resolver.get_instances_by_config(configuration_name, nanny_oauth_token=nanny_token)
                if not instances:
                    raise Exception("No instances. ")
            except Exception as err:
                eh.log_exception("Problem resolving {}".format(configuration_name), err)
                eh.check_failed("No instances resolved for configuration {}".format(configuration_name))

        self.set_info("Test GenCFG groups...")
        tdi_instances = instance_resolver.get_instances_by_active_config(terms=['G@SAS_WEB_TDI_MERGER_RKUB'])
        logging.info("TDI instances %s", tdi_instances)

        self.set_info("Test resolve UP...")
        web_base_instances = instance_resolver.get_instances_by_config(cn.C.jupiter_base)
        for web_base_inst in web_base_instances[:3]:
            up_instances = instance_resolver.get_upper_instances(web_base_inst[0], web_base_inst[1])
            logging.info('Web Base instance: {}, upper instances: {}'.format(web_base_inst, up_instances))

        # test up and down
        self.set_info("Test resolve DOWN and UP...")
        web_int_instances = instance_resolver.get_instances_by_config(cn.C.jupiter_int)
        for web_int_inst in web_int_instances[:3]:
            up_instances = instance_resolver.get_upper_instances(web_int_inst[0], web_int_inst[1])
            down_instances = instance_resolver.get_lower_instances(web_int_inst[0], web_int_inst[1])
            logging.info(
                'Web Int instance: upper instances: %s\n, down instances: %s\n',
                up_instances, down_instances
            )


__Task__ = TestInstanceResolver
