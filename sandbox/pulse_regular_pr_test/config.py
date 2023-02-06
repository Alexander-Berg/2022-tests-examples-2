# coding=utf-8
import logging

import yaml
from sandbox.projects.sandbox_ci.pulse import config


class Config(object):
    def __init__(self, yaml_config):
        raw_config = yaml.load(yaml_config)
        self._config = config.process_config(raw_config).get('limits', {})

        logging.debug('Config: %s', self._config)

    def shooting_limit_for(self, platform, stage, metric_name, percentile):
        return (
            self._config
                .get('shooting')
                .get(platform, {})
                .get(stage, {})
                .get(metric_name, {})
                .get(percentile)
        )

    def static_limit_for(self, platform, bundle):
        return (
            self._config
                .get('static_delta')
                .get(platform, {})
                .get(bundle)
        )
