# pylint: disable=C0302

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import state as state_module


PARAMETERS = [
    (
        'Федорук Ирина Анатольевна, номер ранее указан 89035534022, г.Воскресенск,новый номер 89912230585',  # noqa
        {
            'rules': {
                'Text': {
                    'Request': 'федорук ирина анатольевна, номер ранее указан 89035534022, г.воскресенск,новый номер 89912230585',  # noqa
                    'UserRequest': 'Федорук Ирина Анатольевна, номер ранее указан 89035534022, г.Воскресенск,новый номер 89912230585',  # noqa
                    'RequestLenTruncated': '0',
                },
                'NormalizeRequest': {
                    'QueryTruncated': '0',
                    'RuleResult': '3',
                    'BannerRequest': 'федорук ирина анатольевна номер ранее указан 89035534022 г воскресенск новый номер 89912230585',  # noqa
                },
                'LangRecognizer': {'RuleResult': '3'},
                'RelevLocale': {
                    'SearchCountryID': '225',
                    'SearchRegion': '225',
                },
                'Fio': {'RuleResult': '3', 'Fio': 'федорук ирина анатольевна'},
            },
        },
        ['федорук ирина анатольевна'],
    ),
]


async def test_fio_entity_extractor(create_nlu, web_context, core_flags):
    for text, wiz_response, result in PARAMETERS:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }
        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['fio_extractor'].values == result


PARAMETERS2 = [
    (
        'Ирина Анатольевна федорук',  # noqa
        {
            'rules': {
                'Text': {
                    'Request': 'ирина анатольевна федорук',
                    'UserRequest': 'Ирина Анатольевна федорук',
                    'RequestLenTruncated': '0',
                },
                'NormalizeRequest': {
                    'QueryTruncated': '0',
                    'RuleResult': '3',
                    'BannerRequest': 'ирина анатольевна федорук',
                },
                'LangRecognizer': {'RuleResult': '3'},
                'RelevLocale': {
                    'SearchCountryID': '225',
                    'SearchRegion': '225',
                },
                'Fio': {
                    'RuleResult': '3',
                    'Fio': ['федорук ирина анатольевна'],
                },
            },
        },
        ['ирина'],
    ),
    (
        'федорук',  # noqa
        {
            'rules': {
                'Text': {
                    'Request': 'федорук',
                    'UserRequest': 'федорук',
                    'RequestLenTruncated': '0',
                },
                'NormalizeRequest': {
                    'QueryTruncated': '0',
                    'RuleResult': '3',
                    'BannerRequest': 'федорук',
                },
                'LangRecognizer': {'RuleResult': '3'},
                'RelevLocale': {
                    'SearchCountryID': '225',
                    'SearchRegion': '225',
                },
                'Fio': {'RuleResult': '3', 'Fio': ['федорук']},
            },
        },
        [],
    ),
]


async def test_first_name_entity_extractor(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result in PARAMETERS2:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }
        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['first_name_extractor'].values == result


PARAMETERS3 = [
    (
        'Ирина Анатольевна федорук Ирина Анатольевна федорук',  # noqa
        {
            'rules': {
                'Text': {
                    'Request': (
                        'ирина анатольевна федорук ирина анатольевна федорук'
                    ),  # noqa
                    'UserRequest': (
                        'Ирина Анатольевна федорук Ирина Анатольевна федорук'
                    ),  # noqa
                    'RequestLenTruncated': '0',
                },
                'NormalizeRequest': {
                    'QueryTruncated': '0',
                    'RuleResult': '3',
                    'BannerRequest': 'ирина анатольевна федорук ирина анатольевна федорук',  # noqa
                },
                'LangRecognizer': {'RuleResult': '3'},
                'RelevLocale': {
                    'SearchCountryID': '225',
                    'SearchRegion': '225',
                },
                'Fio': {
                    'RuleResult': '3',
                    'Fio': [
                        'федорук ирина анатольевна',
                        'федорук ирина анатольевна',
                    ],
                },
            },
        },
        ['федорук', 'федорук'],
    ),
]


async def test_last_name_entity_extractor(create_nlu, web_context, core_flags):
    for text, wiz_response, result in PARAMETERS3:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }
        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['last_name_extractor'].values == result


PARAMETERS4 = [
    (
        'Ирина Анатольевна федорук Ирина федорук',  # noqa
        {
            'rules': {
                'Text': {
                    'Request': 'ирина анатольевна федорук ирина федорук',
                    'UserRequest': 'Ирина Анатольевна федорук Ирина федорук',
                    'RequestLenTruncated': '0',
                },
                'NormalizeRequest': {
                    'QueryTruncated': '0',
                    'RuleResult': '3',
                    'BannerRequest': 'ирина анатольевна федорук ирина федорук',
                },
                'LangRecognizer': {'RuleResult': '3'},
                'RelevLocale': {
                    'SearchCountryID': '225',
                    'SearchRegion': '225',
                },
                'Fio': {
                    'RuleResult': '3',
                    'Fio': ['федорук ирина анатольевна', 'федорук ирина'],
                },
            },
        },
        ['анатольевна'],
    ),
]


async def test_middle_name_entity_extractor(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result in PARAMETERS4:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }
        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['middle_name_extractor'].values == result


PARAMETERS5 = [
    ('мой номер телефона 7900123456', []),
    ('мой номер телефона 890012345673', []),
    ('мой номер телефона 8(900)1234567123', []),
    ('мой номер телефона 8 900 123 47', []),
    ('мой номер телефона 8-900-12', []),
    ('мой номер телефона 900.123.45.67', []),
    ('мой номер телефона 8:900:123:45:671234', []),
    ('мой номер телефона 79001234567', ['79001234567']),
    ('мой номер телефона 89001234567', ['79001234567']),
    ('мой номер телефона 8(900)1234567', ['79001234567']),
    ('мой номер телефона 8 900 123 45 67', ['79001234567']),
    ('мой номер телефона 8-900-123-45-67', ['79001234567']),
    ('мой номер телефона 8.900.123.45.67', ['79001234567']),
    ('мой номер телефона 8:900:123:45:67', ['79001234567']),
    ('мой номер телефона 79001234567', ['79001234567']),
    ('мой номер телефона 7(900)1234567', ['79001234567']),
    ('мой номер телефона 7 900 123 45 67', ['79001234567']),
    ('мой номер телефона 7-900-123-45-67', ['79001234567']),
    ('мой номер телефона 7.900.123.45.67', ['79001234567']),
    ('мой номер телефона 7:900:123:45:67', ['79001234567']),
    ('мой номер телефона +7 (900) 123 45 67', ['79001234567']),
    ('мой номер телефона +7 9001234567', ['79001234567']),
    ('мой номер телефона +7 700 123 1234', ['77001231234']),  # Kazakhstan
    ('my phone number is +90 312 213 2965', ['903122132965']),  # Turkey
    ('my phone number is +44 7911 123456', ['447911123456']),  # UK
    ('my phone number is +971 12-345-6789', ['971123456789']),  # UAE
    ('my phone number is +49 69 1234 5678', ['496912345678']),  # Germany
    ('my phone number is +380 50 123-45-67', ['380501234567']),  # Ukrain
    ('my phone number is +1-212-456-7890', ['12124567890']),  # USA
    ('my phone number is +375 123-4567-890', ['3751234567890']),  # Belarus
    ('my phone number is +56 123-4567-890', ['561234567890']),  # Chile
    ('my phone number is +90 312 213 293', []),
    ('my phone number is +44 7911 12345', []),
    ('my phone number is +90 312 213 29312', []),
    ('my phone number is +44 7911 12345321', []),
    ('my phone number is +1-212-456-789', []),
    ('my phone number is +1-212-456-78912', []),
]


async def test_phone_number_entity_extractor(
        create_nlu, web_context, core_flags,
):
    for text, result in PARAMETERS5:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }

        wiz_response = {'rules': {}}

        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['phone_number_extractor'].values == result


PARAMETERS6 = [
    ('My email address is simple@example.com', ['simple@example.com']),
    (
        'My email address is very.common@example.com ',
        ['very.common@example.com'],
    ),
    (
        (
            'My email address is '
            'disposable.style.email.with+symbol@example.com'
        ),
        ['disposable.style.email.with+symbol@example.com'],
    ),
    (
        'My email address is other.email-with-hyphen@example.com ',
        ['other.email-with-hyphen@example.com'],
    ),
    (
        'My email address is fully-qualified-domain@example.com',
        ['fully-qualified-domain@example.com'],
    ),
    (
        'My email address is user.name+tag+sorting@example.com',
        ['user.name+tag+sorting@example.com'],
    ),
    ('My email address is x@example.com', ['x@example.com']),
    ('My email address is user.name@example.com', ['user.name@example.com']),
    (
        'My email address is example-indeed@strange-example.com',
        ['example-indeed@strange-example.com'],
    ),
    ('My email address is test/test@test.com', ['test/test@test.com']),
    ('My email address is example@s.example', ['example@s.example']),
    (
        'My email address is mailhost!username@example.org',
        ['mailhost!username@example.org'],
    ),
    (
        r'My email address is user%example.com@example.org',
        [r'user%example.com@example.org'],
    ),
    ('My email address is user@example.com', ['user@example.com']),
    ('My email address is user-@example.org', ['user-@example.org']),
    (
        'My email address is postmaster@[123.123.123.123]',
        ['postmaster@[123.123.123.123]'],
    ),
    ('My email address is Abc.example.com', []),
    (
        r"""My email address is "john..doe"@example.org""",
        [""""john..doe"@example.org"""],
    ),
    ('My email address is A@b@c@example.com', []),
    (r"""My email address is a"b(c)d,e:f;g<h>i[j\k]l@example.com""", []),
    ("""My email address is just"not"right@example.com""", []),
    (r"""My email address is this is"not\allowed@example.com""", []),
    (r"""My email address is this\ still\"not\\allowed@example.com""", []),
    (
        (
            'My email address is '
            'i_like_underscore@but_its_not_'
            'allowed_in_this_part.example.com'
        ),
        [],
    ),
    ('My email address is QA[icon]CHOCOLATE[icon]@test.com', []),
    (
        (
            'My email addresses are simple@example.com,'
            ' not_so_simple@example.com'
        ),
        ['simple@example.com', 'not_so_simple@example.com'],
    ),
    (
        'My email address is #!$%&\'*+-/=?^_`{}|~@example.org',
        ['#!$%&\'*+-/=?^_`{}|~@example.org'],
    ),
    (
        (
            """My email address is example@s.solutions, """
            r""""very.unusual.@.unusual.com"@example.com"""
        ),
        [
            'example@s.solutions',
            """"very.unusual.@.unusual.com"@example.com""",
        ],
    ),
    ('My email address is A@b@c@example.com', []),
]


async def test_email_entity_extractor(create_nlu, web_context, core_flags):
    for text, result in PARAMETERS6:
        supportai_models_response = {
            'most_probable_topic': 'Cancel_lesson',
            'probabilities': [
                {'topic_name': 'Cancel_lesson', 'probability': 0.8},
                {'topic_name': 'Move_lesson', 'probability': 0.2},
            ],
        }

        wiz_response = {'rules': {}}

        request = supportai_lib_module.SupportRequest.deserialize(
            {
                'dialog': {'messages': [{'author': 'user', 'text': text}]},
                'features': [],
            },
        )
        state = state_module.State(feature_layers=[{}])
        nlu = await create_nlu(
            config_path='configuration.json',
            namespace='justschool_dialog',
            supportai_models_response=supportai_models_response,
            wiz_response=wiz_response,
        )

        nlu_response = await nlu(request, state, web_context, core_flags)
        assert nlu_response.entities['email_extractor'].values == result


async def test_number_entity_extractor(create_nlu, web_context, core_flags):

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    wiz_response = {'rules': {}}

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Извлеки мне число 1234'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[{}])

    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.entities['number_entity'].values == [1234]
