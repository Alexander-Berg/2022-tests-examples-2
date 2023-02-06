# -*- coding: utf-8 -*-

from passport.backend.core.compare.compare import UA_COMPONENT_WEIGHTS


def compared_user_agent(os='windows 7', browser='mozilla', yandexuid='123'):
    return {
        'os.name': os,
        'browser.name': browser,
        'yandexuid': yandexuid,
    }


def compare_uas_factor(*matches):
    return sum(UA_COMPONENT_WEIGHTS[matched_field] for matched_field in matches)
