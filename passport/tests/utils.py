# -*- coding: utf-8 -*-
from passport.backend.core.tracks.model import AuthTrack


DEFAULT_QUERY_PARAMS = {
    'login': 'l',
    'firstname': u'fnфн',
    'lastname': u'lnлн',
    'email': 'em',
    'service': 'from',
    'password': None,
    'quality': 0,
    'old_password_quality': 80,
    'hint_question_id': 1,
    'hint_question': 'aaaBB',
    'hint_answer': '',
    'phone_number': '+7(999)123 4567',
    'social_provider': 'sp',
    'language': 'l',
    'country': 'c',
    'action': 'a',
    'consumer': 'dev',
    'account_country': 'ru',
    'account_language': 'ru',
    'account_timezone': 'Europe/Paris',
}


def mock_track(track_data, track_class=AuthTrack):
    track = track_class('track_id', data=track_data, lists={'suggested_logins': []})
    return track
