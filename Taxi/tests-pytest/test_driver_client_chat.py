# -*- coding: utf-8 -*-
import copy
import urllib

import pytest

from taxi.core import async
from taxi.external import chat
from taxi.internal import dbh
from taxi.internal.order_kit import driver_client_chat
from taxi.internal.order_kit.plg import order_fsm
from taxi.util import evlog

EVLOGGER = evlog.new_event('test', {})


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_creation(patch):
    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create(*args, **kwrags):
        query_string = urllib.urlencode({'user_id': 'userid',
                                         'order_id': 'order_x'})
        assert args[0] == {
            'participants': [
                {
                    'action': 'add',
                    'metadata': {
                        'translation_settings': {
                            'to': 'en',
                            'do_not_translate': [],
                        }
                    },
                    'role': 'client',
                    'id': 'userid',
                    'subscription': {
                        'fields': ['chat_id', 'newest_message_id', 'text', 'sender'],
                        'callback_url': (
                            'http://taxi-protocol.taxi.tst.yandex.net'
                            '/internal/orderchat-callback?' + query_string
                        )
                    }
                }
            ],
            'metadata': {
                'order_id': 'order_x',
                'comment': {},
                'user_id': 'userid',
                'order_locale': 'en'
            }
        }
        yield async.return_value('created_chat_id')

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_x')
    state = order_fsm.OrderFsm(proc=proc)

    yield driver_client_chat.handle_creation(state, EVLOGGER)

    assert proc.chat_id == 'created_chat_id'
    assert not proc.chat_visible
    yield proc.save_chat_info()
    assert proc.chat_id == 'created_chat_id'
    assert not proc.chat_visible
    db_proc = yield dbh.order_proc.Doc.find_one_by_id('order_x')
    assert db_proc.chat_id == 'created_chat_id'
    assert not db_proc.chat_visible

    # test no recreation
    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create2(*args, **kwrags):
        assert False

    state = order_fsm.OrderFsm(proc=proc)
    yield driver_client_chat.handle_creation(state, EVLOGGER)
    assert proc.chat_id == 'created_chat_id'


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_creation_non_allowed_class(patch):
    proc = yield dbh.order_proc.Doc.find_one_by_id('order_pool')
    state = order_fsm.OrderFsm(proc=proc)
    yield driver_client_chat.handle_creation(state, EVLOGGER)
    assert not state.proc.chat_id


@pytest.mark.now('2018-05-25T13:59:34+0300')
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_assigning(patch):
    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info(*args, **kwrags):
        if not hasattr(get_info, 'send_with_driver'):
            get_info.send_with_driver = False
        else:
            get_info.send_with_driver = True
        data = {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {},
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        }
        if get_info.send_with_driver:
            data['newest_message_id'] = '2'
            data['metadata'].update({
                'taximeter_order': {
                    'db_id': 'park_id',
                    'alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97'},
            })
            data['participants'].append({
                'id': 'park_id_uuid',
                'role': 'driver',
                'active': True,
                'metadata': {
                    'translation_settings': {
                        'to': 'en',
                        'do_not_translate': []
                    }
                }
            })
        yield async.return_value(data)

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post(url, payload, log_extra):
        if not hasattr(_perform_post, 'set_can_translate'):
            _perform_post.set_can_translate = False
        else:
            _perform_post.set_can_translate = True
        if not _perform_post.set_can_translate:
            assert payload == {
                'update_metadata': {
                    'taximeter_order': {
                        'db_id': 'park_id',
                        'alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97'}
                },
                'newest_message_id': '1',
                'update_participants': {
                    'role': 'driver',
                    'action': 'add',
                    'subscription': {
                        'callback_url': (
                            'https://taximeter-chat.tst.mobile.yandex.net/api/'
                            'subscription_callback/?'
                            'alias_id=22c6f49e8a944fb48fe91bda0fb9ce97'
                        )
                    },
                    'nickname': 'driver',
                    'id': 'park_id_uuid',
                    'metadata': {
                        'translation_settings': {
                            'to': 'en',
                            'do_not_translate': [],
                        }
                    }
                }, 'created_date': '2018-05-25T13:59:34+0300'
            }
            yield async.return_value({
                'message_id': '2'
            })
        else:
            assert payload == {
                'update_metadata': {
                    'taximeter_order': {
                        'db_id': 'park_id',
                        'alias_id': '22c6f49e8a944fb48fe91bda0fb9ce97'},
                    'can_translate': True
                },
                'newest_message_id': '2',
                'created_date': '2018-05-25T13:59:34+0300'
            }
            yield async.return_value({
                'message_id': '3'
            })

    @patch('taxi.internal.driver_manager.get_driver_by_park_driver_id')
    @async.inline_callbacks
    def get_driver_by_park_driver_id(db_id, uuid, fields, consumer_name):
        assert db_id == 'park_id' and uuid == 'uuid'
        yield async.return_value(dbh.drivers.Doc({
            '_id': 'clid_uuid',
            'locale': 'en'
        }))

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_assigning')
    state = order_fsm.OrderFsm(proc=proc)
    state._handle_assigned({'i': 0})

    yield driver_client_chat.handle_assigning(state, EVLOGGER)

    assert state.proc.chat_visible

    # test no multiple updates
    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info2(*args, **kwrags):
        yield async.return_value({
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'can_translate': False
            },
            'participants': [
                {
                    'id': 'park_id_uuid',
                    'role': 'driver',
                    'active': True,
                },
            ]
        })

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post2(url, payload, log_extra):
        assert False

    yield driver_client_chat.handle_assigning(state, EVLOGGER)


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_assigning_client_errors(patch):
    @patch('taxi.external.chat.post_update_with_retry')
    @async.inline_callbacks
    def post_update(*args, **kwrags):
        raise chat.ClientError

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_assigning')
    assert proc.chat_id == 'chat_id'
    state = order_fsm.OrderFsm(proc=proc)
    state._handle_assigned({'i': 0})

    yield driver_client_chat.handle_assigning(state, EVLOGGER)

    assert state.proc.chat_visible is None
    assert state.proc.chat_id == 'chat_id'

    yield proc.save_chat_info()
    assert proc.chat_id == 'chat_id'
    assert proc.chat_visible is None

    db_proc = yield dbh.order_proc.Doc.find_one_by_id('order_assigning')
    assert db_proc.chat_id == 'chat_id'
    assert db_proc.chat_visible is None


@pytest.mark.now('2018-05-30T20:55:39+0300')
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_reorder(patch):
    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info(*args, **kwrags):
        yield async.return_value({
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {},
            'participants': [
                {
                    'id': 'park_id_uuid',
                    'role': 'driver',
                    'active': True,
                },
            ]
        })

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post(url, payload, log_extra):
        assert payload == {
            'update_metadata': {'can_translate': False},
            'newest_message_id': '1',
            'update_participants': {
                'action': 'remove',
                'role': 'driver',
                'id': 'park_id_uuid'
            },
            'created_date': '2018-05-30T20:55:39+0300'
        }
        yield async.return_value({
            'message_id': '2'
        })

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_autoreordering')
    state = order_fsm.OrderFsm(proc)

    yield driver_client_chat.handle_autoreorder(state, EVLOGGER)

    assert not state.proc.chat_visible

    # test no multiple updates
    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info2(*args, **kwrags):
        yield async.return_value({
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {},
            'participants': [
                {
                    'id': 'park_id_uuid',
                    'role': 'driver',
                    'active': False,
                },
            ]
        })

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post2(url, payload, log_extra):
        assert False

    yield driver_client_chat.handle_autoreorder(state, EVLOGGER)


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_handle_close(patch):
    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info(*args, **kwrags):
        if not hasattr(get_info, 'send_active'):
            get_info.send_active = True
        else:
            get_info.send_active = False
        yield async.return_value({
            'id': 'chat_id',
            'newest_message_id': '3',
            'metadata': {},
            'participants': [
                {
                    'id': 'x',
                    'role': 'driver',
                    'active': False
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': get_info.send_active
                }
            ]
        })

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post(url, payload, log_extra):
        assert payload['newest_message_id'] == '3'
        assert payload['update_participants']['action'] == 'remove'
        assert payload['update_participants']['id'] == 'driver_id'
        yield async.return_value({
            'message_id': '6'
        })

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_assigning')
    state = order_fsm.OrderFsm(proc)

    yield driver_client_chat.close(state, EVLOGGER)

    assert not state.proc.chat_visible


@pytest.mark.now('2018-05-25T13:59:34+0300')
@pytest.mark.config(CLIENTDRIVER_CHAT_ADD_TRANSLATE_STATUS_MESSAGES=True)
@pytest.mark.translations([
    ('notify', 'chat.translate_on', 'ru',
     u'Переводим клиенту на %(client_language)s, а водителю на %(driver_language)s'),
    ('notify', 'chat.translate_off_driver', 'ru', u'У водителя нет переводчика'),
    ('notify', 'chat.translate_off_same', 'ru', u'У водителя и пассажира в чате %(language)s язык'),
    ('locales', 'locale_name_ru', 'ru', u'русский'),
    ('locales', 'locale_name_en', 'ru', u'английский'),
    ('locales', 'locale_name_es', 'ru', u'испанский'),
])
@pytest.mark.parametrize('get_chat_response,expected_post_payload,', [
    (  # test no translate to can translate
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value'
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'en',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': True,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'en'
                }
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
            'message': {
                'sender': {'id': 'system', 'role': 'system'},
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': [],
                        'app_language': 'ru',
                        'system_languages': []
                    },
                    'message_key': 'chat.translate_on',
                    'tanker_locale': 'ru',
                    'message_params': [
                        {
                            'type': 'language',
                            'name': 'client_language',
                            'value': 'ru'
                        },
                        {
                            'type': 'language',
                            'name': 'driver_language',
                            'value': 'en'
                        }
                    ]
                },
                'text': u'Переводим клиенту на русский, а водителю на английский'
            }
        }
    ),
    (  # test translate to no translate (because driver not supports)
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value',
                'can_translate': True,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'en'
                }
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': False,
                'last_translate_message': {
                    'message_key': 'chat.translate_off_driver',
                }
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
            'message': {
                'sender': {'id': 'system', 'role': 'system'},
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': [],
                        'app_language': 'ru',
                        'system_languages': []
                    },
                    'message_key': 'chat.translate_off_driver',
                    'tanker_locale': 'ru',
                },
                'text': u'У водителя нет переводчика'
            }
        }
    ),
    (  # test translate to no translate (same language)
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value',
                'can_translate': True,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'en'
                }
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': False,
                'last_translate_message': {
                    'message_key': 'chat.translate_off_same',
                    'language': 'ru'
                }
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
            'message': {
                'sender': {'id': 'system', 'role': 'system'},
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': [],
                        'app_language': 'ru',
                        'system_languages': []
                    },
                    'message_key': 'chat.translate_off_same',
                    'tanker_locale': 'ru',
                    'message_params': [
                        {
                            'type': 'language',
                            'name': 'language',
                            'value': 'ru'
                        },
                    ]
                },
                'text': u'У водителя и пассажира в чате русский язык'
            }
        }
    ),
    (  # test translate to another translate (driver changed language)
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'order_locale': 'ru',
                'key': 'value',
                'can_translate': True,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'en'
                }
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'es',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': True,
                'order_locale': 'ru',
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'es'
                }
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
            'message': {
                'sender': {'id': 'system', 'role': 'system'},
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': [],
                        'app_language': 'ru',
                        'system_languages': []
                    },
                    'message_key': 'chat.translate_on',
                    'tanker_locale': 'ru',
                    'message_params': [
                        {
                            'type': 'language',
                            'name': 'client_language',
                            'value': 'ru'
                        },
                        {
                            'type': 'language',
                            'name': 'driver_language',
                            'value': 'es'
                        }
                    ]
                },
                'text': u'Переводим клиенту на русский, а водителю на испанский'
            }
        }
    ),
    (  # test no client translation
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value',
                'can_translate': False
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'es',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': False,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'es'
                }
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
        }
    ),
    (  # test nothing changed
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value',
                'can_translate': True,
                'last_translate_message': {
                    'message_key': 'chat.translate_on',
                    'client_language': 'ru',
                    'driver_language': 'en'
                }
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'ru',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'en',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        'Nothing posted'
    ),
    (  # test unknown language
        {
            'id': 'chat_id',
            'newest_message_id': '1',
            'metadata': {
                'key': 'value',
                'can_translate': False
            },
            'participants': [
                {
                    'id': 'client_id',
                    'role': 'client',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'unknown language',
                            'do_not_translate': []
                        }
                    }
                },
                {
                    'id': 'driver_id',
                    'role': 'driver',
                    'active': True,
                    'metadata': {
                        'translation_settings': {
                            'to': 'es',
                            'do_not_translate': []
                        }
                    }
                }
            ]
        },
        {
            'update_metadata': {
                'key': 'value',
                'can_translate': True,
            },
            'newest_message_id': '1',
            'created_date': '2018-05-25T13:59:34+0300',
        }
    ),
])
@pytest.inline_callbacks
def test_assign_translaton_message(get_chat_response, expected_post_payload, patch):
    chat_base_url = 'chat_base_url'

    @patch('taxi.external.chat.get_info')
    @async.inline_callbacks
    def get_info(*args, **kwrags):
        yield async.return_value(copy.deepcopy(get_chat_response))

    @patch('taxi.external.chat._perform_post')
    @async.inline_callbacks
    def _perform_post(url, payload, log_extra):
        assert payload == expected_post_payload
        yield async.return_value({'message_id': '2'})

    yield driver_client_chat.update_can_translate_flag(
        'chat_id', chat_base_url, proc=None, log_extra=None
    )
