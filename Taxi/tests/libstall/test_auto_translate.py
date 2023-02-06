from scripts.translations.auto_translate import translate_tjson, encode_json,\
    decode_json, encode_form, decode_form


# pylint: disable=unused-argument
def mock_translate_tjson(joke_text):
    return [{'text': 'Hello!'}, {'text': 'World! 1'}, {'text': 'World! 2'},
            {'text': 'World! 5'}, {'text': 'World! 0'}]


def test_encode_json():
    string = "{{user1}},{{user2}}!"
    assert encode_json(string) == "<.user1>,<.user2>!"


def test_decode_json():
    string = "{{user1}},{{user2}}!"
    assert decode_json(encode_json(string)) == string


def test_encode_form():
    string1 = "{{count}} штука!"
    string2 = "{{count }} штуки!"
    string3 = "{{ count }} штук!"
    assert encode_form(string1, '1') == "1 штука!"
    assert encode_form(string2, '2') == "2 штуки!"
    assert encode_form(string3, '3') == "5 штук!"


def test_decode_form():
    string = "{{count}} штука!"
    assert decode_form(encode_form(string, '1')) == string


def test_translate_json():
    tjson_to_translate = {
        "keysets": {
            "ui_wms": {
                "keys": {
                    "привет": {
                        "info": {"is_plural": False},
                        "translations": {
                            "ru": {
                                "status": "approved",
                                "author": "test",
                                "form": "Привет!",
                            }
                        }
                    },
                    "мир": {
                        "info": {"is_plural": True},
                        "translations": {
                            "ru": {
                                "status": "approved",
                                "author": "test",
                                "form1": "Мир! {{count}}",
                                "form2": "Мир! {{count}}",
                                "form3": "Мир! {{count}}",
                                "form4": "Мир! {{count}}",
                            },
                        }
                    }
                }
            }
        }
    }
    right_json = {
        "keysets": {
            "ui_wms": {
                "keys": {
                    "привет": {
                        "info": {"is_plural": False},
                        "translations": {
                            "ru": {
                                "status": "approved",
                                "author": "test",
                                "form": "Привет!",
                            },
                            "en": {
                                "status": "requires_translation",
                                "author": "script-auto_translate",
                                "form": "Hello!",
                            },
                        }
                    },
                    "мир": {
                        "info": {"is_plural": True},
                        "translations": {
                            "ru": {
                                "status": "approved",
                                "author": "test",
                                "form1": "Мир! {{count}}",
                                "form2": "Мир! {{count}}",
                                "form3": "Мир! {{count}}",
                                "form4": "Мир! {{count}}",
                            },
                            "en": {
                                "status": "requires_translation",
                                "author": "script-auto_translate",
                                "form1": "World! {{count}}",
                                "form2": "World! {{count}}",
                                "form3": "World! {{count}}",
                                "form4": "World! {{count}}",
                            },
                        }
                    }
                }
            }
        }
    }
    json_to_translate = translate_tjson(tjson_to_translate, 'en',
                                        mock_translate_tjson, 'ui_wms')

    for key in json_to_translate:
        assert json_to_translate[key] == right_json[key]
