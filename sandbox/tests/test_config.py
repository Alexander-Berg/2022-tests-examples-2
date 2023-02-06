# coding=utf-8

import logging
import os
import unittest
from copy import deepcopy

import pytest

from sandbox.projects.browser.booking import config


class TestConfigLoader(unittest.TestCase):
    def test_merge_config(self):
        basic = {
            'simple-key-1': 1,
            'simple-key-2': 2,
            'dict-key-1': {'aaa': 111},
            'dict-key-2': {'bbb': 222},
            'other-key-1': 123,
            'other-key-2': {'qwe': 123},
            'params': {'volumeDescription': {'customVolume': {'environmentDistribution': {'abc': 123}}}},
        }
        update = {
            'simple-key-1': 666,
            'simple-key-2': {'aaa': 555, 'asd': 123},
            'dict-key-1': 999,
            'dict-key-2': {'aaa': 555},
            'params': {'volumeDescription': {'customVolume': {'environmentDistribution': {'qwe': 123}}}},
        }
        merged = {
            'simple-key-1': 666,
            'simple-key-2': {'aaa': 555, 'asd': 123},
            'dict-key-1': 999,
            'dict-key-2': {'aaa': 555, 'bbb': 222},
            'other-key-1': 123,
            'other-key-2': {'qwe': 123},
            'params': {'volumeDescription': {'customVolume': {'environmentDistribution': {'qwe': 123}}}},
        }
        assert config.ConfigLoader._merge_config(basic, update) == merged

    CORRECT_CONFIG = {
        'desktop': {
            'booking-kinds': {
                'beta:release': {
                    'create-days': 14,
                    'veto-days': 7,
                    'notification-hours-threshold': 10,
                    'time-msk': '12:00',
                    'params': {
                        'quotaSource': 'qs_testpalm_combined_brocase_ru',
                        'speedMode': 'NORMAL',
                        'volumeDescription': {
                            "volumeSources": [],
                            'customVolume': {
                                'amount': '100',
                                'environmentDistribution': {
                                    '123': 0.5,
                                    '321': 0.5,
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    def test_validate_correct_config(self):
        config.ConfigLoader._validate_merged_config(self.CORRECT_CONFIG)

    def test_validate_wrong_sum(self):
        with pytest.raises(ValueError) as e:
            config_json = deepcopy(self.CORRECT_CONFIG)
            params = config_json['desktop']['booking-kinds']['beta:release']['params']
            custom_volume = params['volumeDescription']['customVolume']
            custom_volume['environmentDistribution'] = {
                '123': 0.1,
                '321': 0.1,
            }
            config.ConfigLoader._validate_merged_config(config_json)
        assert 'desktop' in e.value.message
        assert 'beta:release' in e.value.message

    def test_all_configs(self):
        import yatest.common
        config_dir = os.path.join(
            yatest.common.test_source_path(),
            os.pardir, 'config')

        configs = config.ConfigLoader.available_configs(config_dir)
        assert configs
        for choice_name, config_path in configs.iteritems():
            logging.warning('%s: %s', choice_name, config_path)
            config_json = config.ConfigLoader._load_config_json(config_path)
            logging.warning('config:\n%s', config_json)
            # Check config can be loaded using standard method.
            config.ConfigLoader.load_config(config_path)

    def create_config_with_environment(self, project_key, booking_kind, environment_distribution):
        return {
            project_key: {
                'booking-kinds': {
                    booking_kind: {
                        'create-days': 14,
                        'veto-days': 7,
                        'notification-hours-threshold': 10,
                        'time-msk': '12:00',
                        'params': {
                            'quotaSource': 'qs_testpalm_combined_brocase_ru',
                            'speedMode': 'NORMAL',
                            'volumeDescription': {
                                "volumeSources": [],
                                'customVolume': {
                                    'amount': '100',
                                    'environmentDistribution': environment_distribution
                                }
                            }
                        }
                    }
                }
            }
        }

    def test_validate_environment_correct_and_or(self):
        config_json = deepcopy(self.CORRECT_CONFIG)
        params = config_json['desktop']['booking-kinds']['beta:release']['params']
        custom_volume = params['volumeDescription']['customVolume']
        custom_volume['environmentDistribution'] = {
            '11': 0.6,
            '22 || 33': 0.1,
            '44 || 55 || 66': 0.1,
            '22 && 33': 0.1,
            '44 && 55 && 66': 0.1,
        }
        config.ConfigLoader._validate_merged_config(config_json)

    def test_validate_environment_wrong_and_or(self):
        config_json = deepcopy(self.CORRECT_CONFIG)
        params = config_json['desktop']['booking-kinds']['beta:release']['params']
        custom_volume = params['volumeDescription']['customVolume']
        custom_volume['environmentDistribution'] = {
            '11 && 22 || 33': 1.0,
        }
        with pytest.raises(BaseException) as e:
            config.ConfigLoader._validate_merged_config(config_json)
        print(e.value.message)
        logging.warn(e.value.message)
        assert '11 && 22 || 33' in e.value.message
        assert 'does not match any of the regexes' in e.value.message
