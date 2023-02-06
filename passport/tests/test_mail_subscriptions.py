# -*- coding: utf-8 -*-

from passport.backend.api.settings.mail_subscriptions import subscription_services


def test_unique_ids():
    actual_ids = [s['id'] for s in subscription_services.SENDER_MAIL_SUBSCRIPTION_SERVICES]
    assert sorted(actual_ids) == sorted(set(actual_ids))


def test_unique_slugs():
    actual_slugs = [s['slug'] for s in subscription_services.SENDER_MAIL_SUBSCRIPTION_SERVICES]
    assert sorted(actual_slugs) == sorted(set(actual_slugs))


def test_all_slugs_in_lower_case():
    actual_slugs = [s['slug'] for s in subscription_services.SENDER_MAIL_SUBSCRIPTION_SERVICES]
    bad_slugs = []
    for slug in actual_slugs:
        if slug != slug.lower():
            bad_slugs.append(slug)
    assert bad_slugs == []
