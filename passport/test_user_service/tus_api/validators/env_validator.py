# coding=utf-8
from formencode.validators import (
    FancyValidator,
    Invalid,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import PassportEnvNotAllowed
from passport.backend.qa.test_user_service.tus_api.settings import ALL_AVAILABLE_PASSPORT_ENVS


class EnvValidator(FancyValidator):
    """Проверка, что переданное окружение существует"""

    allowed_environments = ALL_AVAILABLE_PASSPORT_ENVS

    def _to_python(self, value, state):
        env = value.upper()
        if env in ['PROD', 'PRODUCTION']:
            env = 'PROD'
        elif env in ['TEST', 'TESTING']:
            env = 'TEST'
        elif env in ['TEAM', 'INTRANET']:
            env = 'TEAM'
        elif env in ['TEAM-TEST', 'TEAM_TEST']:
            env = 'TEAM_TEST'
        elif env in ['EXTERNAL']:
            env = 'EXTERNAL'
        else:
            raise Invalid('Should be only TEST, PROD, TEAM, TEAM-TEST or EXTERNAL', value, state)
        if env not in self.allowed_environments:
            raise PassportEnvNotAllowed(
                'Allowed env values for this API method are {}'.format(', '.join(self.allowed_environments))
            )
        return env
