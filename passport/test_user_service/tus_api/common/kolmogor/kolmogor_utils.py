# -*- coding: utf-8 -*-
import logging

from passport.backend.core.builders.kolmogor import (
    Kolmogor,
    KolmogorPermanentError,
)
from passport.backend.qa.test_user_service.tus_api import settings
from passport.backend.qa.test_user_service.tus_api.common.xunistater import request_time
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    KolmogorCounterOverflow,
    TestUserServiceInternalException,
)
from passport.backend.qa.test_user_service.tus_api.tvm import TvmToolCredentialsManager


log = logging.getLogger(__name__)


class KolmogorUtils:

    def __init__(self):
        self.kolmogor: Kolmogor = Kolmogor(use_tvm=True, tvm_credentials_manager=TvmToolCredentialsManager())
        self.kolmogor_counters_config = settings.KOLMOGOR_COUNTERS_CONFIG

    @staticmethod
    def _get_time_domain(space):
        if space == 'tus_8s':
            return 'second'
        if space == 'tus_24h':
            return 'day'
        else:
            raise TestUserServiceInternalException('Kolmogor configuration is not valid')

    def get_limit(self, action_name, space, limit_name):
        return self.kolmogor_counters_config[action_name][space].get(
            limit_name,
            self.kolmogor_counters_config[action_name][space]['#default']
        )

    def call_inc_if_less_than(self, space, keys, limits):
        counters_with_values = self.kolmogor.get(space, keys)
        log.debug(f'Counters values for {space} are {counters_with_values}')
        for counter_key, counter_value in counters_with_values.items():
            if counter_value >= limits[space][counter_key]:
                raise KolmogorCounterOverflow(f'Exceeded requests for {counter_key} per {self._get_time_domain(space)}')
        self.kolmogor.inc(space, keys)

    @request_time(signal_name='kolmogor')
    def increment_requests_counter(self, action_name, limits_for):
        log.debug(f'Trying to increment counters for {action_name}')
        if action_name not in self.kolmogor_counters_config:
            raise KolmogorPermanentError('No group matches the passed counter group name')
        counters_config_for_action = self.kolmogor_counters_config[action_name]

        keys_to_increment = [f'{action_name}#{limit_name}' for limit_name in limits_for]
        limits = {
            space: {
                key: self.get_limit(action_name, space, limit_name)
                for key, limit_name in zip(keys_to_increment, limits_for)
            }
            for space in counters_config_for_action
        }
        for space in counters_config_for_action:
            self.call_inc_if_less_than(space, keys_to_increment, limits)
        log.debug(f'Succeeded incrementing counters for {action_name}')


def get_kolmogor():
    return KolmogorUtils()
