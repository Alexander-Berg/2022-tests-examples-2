import os
import time
import logging
from os.path import join as pj

import robot.jupiter.test.common as jupiter_integration
from robot.jupiter.library.python.delivery import LocalDelivery, get_delivery_config, get_delivery_final_targets
from robot.jupiter.library.python.delivery.target_info import get_delivery_target_infos
from robot.library.yuppie.modules.environment import Environment

import yatest.common


IGNORED_TARGETS = frozenset([])


class DeliveryTestParams(object):
    KNOWN_TEST_PARAMS = set([
        'delivery_cluster',
        'delivery_mr_prefix',
        'delivery_timeout',
        'delivery_target',
        'hang_on_error',
        'ram_drive_path',
    ])

    REQUIRED_TEST_PARAMS = set()

    def __init__(self, test_params):
        self.check_params(test_params)

        self.test_dir = os.getcwd()
        self.cluster = test_params.get('delivery_cluster', 'localhost')
        self.mr_prefix = test_params.get('delivery_mr_prefix', None)
        self.timeout = int(test_params.get('delivery_timeout', '600'))
        self.target = test_params.get('delivery_target', None)

        self.is_local_yt = (self.cluster == 'localhost')
        if self.is_local_yt:  # can safely upload data to local YT
            self.tables_data = pj(self.test_dir, 'delivery_tables.tar')
            self.files_data = pj(self.test_dir, 'delivery_files.tar')
        else:
            self.tables_data = None
            self.files_data = None

    def check_params(self, test_params):
        for key in test_params:
            assert key in self.KNOWN_TEST_PARAMS, ("unknown test parameter", key)

        for key in self.REQUIRED_TEST_PARAMS:
            assert key in test_params, ("missing test parameter", key)

    def make_env(self):
        return Environment(
            cluster=self.cluster,
            mr_prefix=self.mr_prefix)


class DeliveryTargetTestParams(DeliveryTestParams):
    REQUIRED_TEST_PARAMS = set([
        'delivery_target',
        'delivery_cluster',
        'delivery_mr_prefix'])


def check_depends(infos, targets):
    for target in targets:
        assert target in infos, "Can't find delivery of target {} in delivery_config".format(target)
        for dep_target in infos[target].depends:
            assert dep_target in targets, "Dependency {} of {} is not in targets".format(dep_target, target)


def call_targets(local_delivery, targets, infos, timeout):
    sorted_infos = sorted(infos.items(), key=lambda x: x[1])  # priority/weight-ordeder run sequence
    targets_in_progress = set()

    def run_targets():
        def check_target_depends(index):
            for dep in sorted_infos[index][1].depends:
                if dep in targets_in_progress:  # deps must be done already
                    return False
            return True

        def get_next_target():
            for i in xrange(len(sorted_infos)):
                if check_target_depends(i):
                    return sorted_infos.pop(i)
            return None

        def run_one_target(target):
            local_delivery.get_cm().call_target_async(target[0], timer=timeout)
            targets_in_progress.add(target[0])

        target_to_run = get_next_target()
        while target_to_run:
            run_one_target(target_to_run)
            target_to_run = get_next_target()

    def clear_finished_targets():
        active_targets = set(local_delivery.get_cm().get_active_targets())
        for target in targets_in_progress:
            if target not in active_targets:
                logging.info("Target {} finished".format(target))

        targets_in_progress.intersection_update(active_targets)

    run_targets()
    while targets_in_progress:
        time.sleep(5)
        clear_finished_targets()
        run_targets()

    local_delivery.get_cm().check_targets(targets, timeout=timeout)


def process(local_delivery, params):
    delivery_config = get_delivery_config(local_delivery.delivery_binaries_dir)
    delivery_config = {k: v for k, v in delivery_config.items() if v.get("delivery_test", True)}
    if params.target:
        targets = set([params.target])
    else:
        targets = set(get_delivery_final_targets(delivery_config, local_delivery.get_cm()))

    targets.difference_update(IGNORED_TARGETS)
    infos = get_delivery_target_infos(delivery_config)
    check_depends(infos, targets)
    infos = {name: value for name, value in infos.iteritems() if name in targets}

    local_delivery.get_cm().disable_restart()
    call_targets(local_delivery, targets, infos, params.timeout)
    while local_delivery.get_cm().get_active_targets():
        time.sleep(10)


def do_run_delivery(params, links):
    env = params.make_env()
    local_delivery = jupiter_integration.run_safe(
        env.hang_test, LocalDelivery,
        bin_dir=env.binary_path,
        cm_bin_dir=env.get_cm_bin_dir(),
        delivery_binaries_dir=yatest.common.binary_path('robot/jupiter/packages/delivery'),
        cluster=env.cluster,
        configuration='yamake',
        prefix=env.mr_prefix,
        tables_data=params.tables_data,
        files_data=params.files_data,
        ram_drive_path=env.ram_drive_path,
        solver_resources={"mem": 16 << 10}  # 16GB
    )
    jupiter_integration.call_jupiter(env.hang_test, process, local_delivery, params)
