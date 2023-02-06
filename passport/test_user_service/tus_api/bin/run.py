# -*- coding: utf-8 -*-
from passport.backend.library.configurator import Configurator
from passport.backend.library.wsgi_runner import Runner
from passport.backend.qa.test_user_service.tus_api.app import execute_app


def run_app():
    app = execute_app()

    config = Configurator(
        'passport-test-user-service',
        configs=[
            'base_config.yaml',
        ],
    )
    runner = Runner(
        app,
        config=config,
    )
    runner.run()
