# coding=utf-8

IRRELEVANT_PARAMS = [
    'access_token', 'callback', 'uid', 'uid_real', 'oauth_token', 'limit', 'offset', 'accuracy', 'proposedAccuracy', 'lang', 'pretty', 'include_meta', 'request_source',
    'date1', 'date2', 'date1_a', 'date1_b', 'date2_a', 'date2_b', 'request_id',
    'end-date', 'start-date', 'max-result', 'prettyPrint', 'role', 'samplingLevel', 'start-index', 'uid_real',
    'debug', 'internal_token', 'request_domain'
]

REQUESTS_CONF = {
    'faced': {
        'table': 'metrika-balancer-faced-api-http-log',
        'handles': [
            # публичные
            {
                'handle': '/stat/v1/data',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/comparison',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/drilldown',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/comparison/drilldown',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/bytime',
                'release_acceptance': True
            },
            # Глобальный отчет
            {
                'handle': '/stat/v1/global',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/global/drilldown',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/global/bytime',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/global/comparison',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/global/comparison/drilldown',
                'release_acceptance': False
            },
            # Отчет товары и заказы
            {
                'handle': '/stat/v1/custom/ecommerce_orders',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/custom/ecommerce_orders/drilldown',
                'release_acceptance': True
            },
            # In-page аналитика
            {
                'handle': '/maps/v1/data/link',
                'release_acceptance': False
            },
            {
                'handle': '/maps/v1/data/form',
                'release_acceptance': False
            },
            {
                'handle': '/maps/v1/data/scroll',
                'release_acceptance': False
            },
            {
                'handle': '/maps/v1/data/click',
                'release_acceptance': False
            },
            {
                'handle': '/maps/v1/data/link/map',
                'release_acceptance': False
            },
            # Отчеты ЦЗ
            {
                'handle': '/calltracking/stat/v1/data',
                'release_acceptance': False
            },
            {
                'handle': '/calltracking/stat/v1/data/drilldown',
                'release_acceptance': False
            },
            {
                'handle': '/calltracking/stat/v1/data/bytime',
                'release_acceptance': False
            },
            # webvisor
            {
                'handle': '/webvisor/v2/data/visits',
                'release_acceptance': False
            },
            {
                'handle': '/webvisor/v2/data/hits',
                'release_acceptance': False
            },
            # грид посетителей
            {
                'handle': '/stat/v1/user/list',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/user/info',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/user/visits',
                'release_acceptance': False
            },
            # Конверсии
            {
                'handle': '/stat/v1/data/conversion_rate',
                'release_acceptance': False
            },
            # GA
            {
                'handle': '/analytics/v3/data/ga',
                'release_acceptance': True
            },
            # custom
            {
                'handle': '/stat/v1/custom/offline_calls/log',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/custom/cross_device',
                'release_acceptance': False
            }
        ]
    },
    'mobmetd': {
        'table': 'metrika-balancer-mobmetd-http-log',
        'handles': [
            {
                'handle': '/stat/v1/data',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/drilldown',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/data/bytime',
                'release_acceptance': True
            },
            {
                'handle': '/stat/v1/profiles/attributes',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/data/labelled',
                'release_acceptance': False
            },
            {
                'handle': '/v2/user/acquisition',
                'release_acceptance': False
            },
            {
                'handle': '/v1/traffic/sources',
                'release_acceptance': False
            },
            {
                'handle': '/v1/cohort/analysis',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/list',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/data/activity_raw',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles',
                'release_acceptance': False
            },
            {
                'handle': '/v1/traffic/sources/events',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events/names',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events/attributes',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events/unwrap',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events/crashes',
                'release_acceptance': False
            },
            {
                'handle': '/stat/v1/profiles/sessions/events/errors',
                'release_acceptance': False
            }
        ]
    }
}
