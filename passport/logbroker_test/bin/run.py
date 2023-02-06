# -*- coding: utf-8 -*-
from passport.backend.logbroker_client.core.run import run_app
import yenv


def main():
    run_app(configs=[
        'base.yaml',
        'logbroker-test/base.yaml',
        'logbroker-test/%s.yaml' % yenv.type,
        'logging_native.yaml',
        'logbroker-test/logging.yaml',
        'export.yaml',
        'logbroker-test/export.yaml',
    ], with_passport_settings=True)
