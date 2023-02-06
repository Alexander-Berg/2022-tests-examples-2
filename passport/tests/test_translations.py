# -*- coding: utf-8 -*-
from passport.backend.api.settings.translations import (
    NOTIFICATIONS,
    QUESTIONS,
    SMS,
    TEXTS,
)
import six


def test_translations():
    KEYSETS = {
        'sms': SMS,
        'questions': QUESTIONS,
        'texts': TEXTS,
        'notifications': NOTIFICATIONS,
    }
    for keyset_name, keyset in six.iteritems(KEYSETS):
        keys = keyset['ru'].keys()
        keys_wo_translation = {}
        for key in keys:
            langs_wo_translation = [
                lang
                for lang, translations in six.iteritems(keyset)
                if not translations.get(key, '').strip()
            ]
            if langs_wo_translation:
                keys_wo_translation[key] = langs_wo_translation

        assert not keys_wo_translation, 'Missing translations: %s' % keys_wo_translation
