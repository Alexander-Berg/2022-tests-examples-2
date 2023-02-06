# -*- coding: utf-8 -*-
import json
import logging
import os


TUS_ENV = os.environ.get('TEST_USER_SERVICE_ENV', 'LOCAL_DEBUG')
IS_FLASK_DEBUG_ENABLED = TUS_ENV == 'LOCAL_DEBUG'

TVMTOOL_LOCAL_AUTHTOKEN = os.environ.get('TVMTOOL_LOCAL_AUTHTOKEN', '')

SSL_CA_CERT = os.environ.get('SSL_CA_CERT', '/etc/ssl/certs/ca-certificates.crt')

PASSPORT_CONSUMER = os.environ.get('TEST_USER_SERVICE_PASSPORT_CONSUMER', 'tus')

IP_WITHOUT_REGISTRATION_LIMITS = '37.9.101.77'

OAUTH_TUS_CLIENT_ID = '9052de6e4cf142039a7ee44ac03e4614'
REQUIRED_OAUTH_SCOPE = 'tus:manage_accounts'

DEFAULT_TUS_CONSUMER = 'tus_common'

kolmogor_config = {
    'PROD': {
        'url': 'http://badauthdb.passport.yandex.net:9080',
        'tvmtool_dst': 'kolmogor-prod',
    },
    'TEST': {
        'url': 'http://badauthdb-test.passport.yandex.net:9080',
        'tvmtool_dst': 'kolmogor-test',
    },
    'DEV': {
        'url': 'http://badauthdb-test.passport.yandex.net:9080',
        'tvmtool_dst': 'kolmogor-test',
    },
    'LOCAL_DEBUG': {
        'url': 'http://badauthdb-test.passport.yandex.net:9080',
        'tvmtool_dst': 'kolmogor-test',
    },
}

KOLMOGOR_URL = kolmogor_config[TUS_ENV]['url']
KOLMOGOR_TIMEOUT = 0.05
KOLMOGOR_RETRIES = 2

create_account_limits = {
    'tus_8s': {  # для лимита по rps (для получения разрешённого rps надо поделить значение лимита на 8)
        '#total': 500,  # суммарно от TUS
        '#default': 100,  # если передан tus_consumer, но для него нет отдельной квоты
        'tus_common': 100,  # если значение tus_consumer не передано
    },
    'tus_24h': {  # для лимита по rpd
        '#total': 70000,  # #total = #default * 3 + sum(other_custom_limits)
        '#default': 5000,
        'tus_common': 5000,
        'ya-travel-frontend': 10000,
        'musfront': 30000,
        'thirium': 10000,
    },
}

# чтобы быстро поднять лимиты при необходимости
CREATE_ACCOUNT_LIMITS = json.loads(os.environ.get('CREATE_ACCOUNT_LIMITS', '{"tus_8s": {}, "tus_24h": {}}'))
for counter_type, limits in CREATE_ACCOUNT_LIMITS.items():
    create_account_limits[counter_type].update(limits)

save_account_limits = {
    'tus_24h': {  # для лимита по rpd
        '#default': 3,  # ограничиваем количество попыток сохранить аккаунт
    },
}

KOLMOGOR_COUNTERS_CONFIG = {
    'create_account': create_account_limits,
    'save_account': save_account_limits,
}

ALL_AVAILABLE_PASSPORT_ENVS = ['TEST', 'PROD', 'TEAM', 'TEAM_TEST', 'EXTERNAL']

passport_config = {
    'PROD': {
        'blackbox': {
            'host': 'blackbox-mimino.yandex.net',
            'tvmtool_dst': 'blackbox-mimino',
        },
        'passport_api': {
            'host': 'passport-internal.yandex.ru',
            'tvmtool_dst': 'passport-api-production',
        }
    },
    'TEST': {
        'blackbox': {
            'host': 'pass-test.yandex.ru',
            'tvmtool_dst': 'blackbox-testing',
        },
        'passport_api': {
            'host': 'passport-test-internal.yandex.ru',
            'tvmtool_dst': 'passport-api-testing',
        }
    },
    'TEAM': {
        'blackbox': {
            'host': 'blackbox.yandex-team.ru',
            'tvmtool_dst': 'blackbox-team-prod',
        },
        'passport_api': {
            'host': 'passport-internal.yandex-team.ru',
            'tvmtool_dst': 'passport-api-team',
        }
    },
    'TEAM_TEST': {
        'blackbox': {
            'host': 'blackbox-test.yandex-team.ru',
            'tvmtool_dst': 'blackbox-team-test',
        },
        'passport_api': {
            'host': 'passport-test-internal.yandex-team.ru',
            'tvmtool_dst': 'passport-api-team-test',
        }
    },
    'LOCAL_DEBUG': {
        'blackbox': {
            'host': 'pass-test.yandex.ru',
            'tvmtool_dst': 'blackbox-testing',
        },
        'passport_api': {
            'host': 'passport-test-internal.yandex.ru',
            'tvmtool_dst': 'passport-api-testing',
        }
    },
}

IDM_ENV = {
    'TEST': {
        'host': 'idm-api.test.yandex-team.ru:443',
        'client_id': 2001602
    },
    'PROD': {
        'host': 'idm-api.yandex-team.ru:443',
        'client_id': 2001600
    },
    'DEV': {
        'host': 'idm-api.test.yandex-team.ru:443',
        'client_id': 2001602
    }
}

IDM_ROLES = {
    "slug": "role",
    "name": {
        "ru": "роль",
        "en": "role"
    },
    "values": {
        "user": {
            "name": {
                "ru": "пользователь",
                "en": "user"
            }
        },
        "admin": {
            "name": {
                "ru": "администратор",
                "en": "admin"
            }
        },
    }
}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        result = {
            'level': record.levelname,
            'message': super(JsonFormatter, self).format(record),
        }
        fields = result['@fields'] = {}
        if hasattr(record, 'request_id') and record.request_id != '':  # TODO
            fields['request_id'] = record.request_id
        return json.dumps(result)


SENSITIVE_FIELDS_TO_MASK = (
    'password',
    'account.password',
    'client_secret',
    'oauth_token',
    'token',
    'Ya-Client-Cookie',
    'Cookie',
    'Ya-Consumer-Authorization',
    'Authorization',
    'X-Ya-Service-Ticket',  # сервисный TVM-тикет
    'X-Ya-User-Ticket',  # пользовательский TVM-тикет
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'passport.backend.qa.test_user_service.tus_api.utils.RequestIdFilter',
        },
        'tskv_filter': {
            '()': 'passport.backend.qa.test_user_service.tus_api.utils.TskvFilter',
        }
    },
    'formatters': {
        'local': {
            'format': '%(asctime)s %(request_id)s %(levelname)s %(name)s:%(lineno)d %(message)s',
        },
        'yt': {
            '()': 'passport.backend.qa.test_user_service.tus_api.settings.JsonFormatter',
            'format': '%(name)s:%(lineno)d\t%(message)s',
        },
        'tskv': {
            'format': '%(message)s',
        }
    },
    'root': {
        'handlers': [
            'console',
            'local_file',
            'stat_file'
        ],
        'level': 'DEBUG',
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'local',
            'stream': 'ext://sys.stdout',
            'filters': ['request_id'],
        },
        'stat_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'tskv',
            'filename': '/logs/tus-stat.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 2,
            'filters': ['tskv_filter'],
        },
        # Этот лог - чтобы в случае необходимости подцепиться по ssh и читать в реальном времени.
        'local_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'local',
            'filename': '/logs/tus-api.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 2,
            'filters': ['request_id'],
        },
    },
}
