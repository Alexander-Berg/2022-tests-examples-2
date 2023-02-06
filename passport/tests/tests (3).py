# -*- coding: utf-8 -*-
import yatest.common as yc


def test_ok():
    yc.execute(
        [
            yc.binary_path('passport/backend/oauth/configs/cli/oauth-configs-cli'),
            'validate',
            '--dir=%s' % yc.source_path('passport/backend/oauth/configs'),
            '--verbose',
            '--colorless',
        ],
        check_exit_code=True,
    )
