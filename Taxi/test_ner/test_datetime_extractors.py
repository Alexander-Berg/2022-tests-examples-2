# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import state as state_module


PARAMETERS = [
    #  31.08.2021: "Body": "{\"Month\":8,\"Day\":31,\"Year\":2021}", "Year": "2021"}  # noqa
    # 2 дня назад"Body": "{\"Duration\":{\"Type\":\"BACK\",\"Day\":2}}"}
    # через 1 день "Body": "{\"Duration\":{\"Type\":\"FORWARD\",\"Day\":1}}"}  # noqa
    # В понедельник "Body": "{\"DayOfWeek\":1,\"Prep\":\"в\"}"}
    # вчера: "Body":"{\"Day\":\"-1D\"}"}
    # завтра: "Body":"{\"Day\":\"-1D\"}"}
    # через неделю в 12:08 "Body":["{\"Duration\":{\"Week\":1,\"Type\":\"FORWARD\"}}","{\"TimePrep\":\"в\",\"Hour\":12,\"Min\":8}"]}  # noqa
    (
        'Добрый день! Отмените урок 31.08.2021',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Day":31, "Month":8, "Year":2021}',
                },
            },
        },
        ['2021-08-31T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок 2 дня назад',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Duration":{"Type": "BACK", "Day": 2}}',
                },
            },
        },
        ['2021-06-21T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок через 8 часов',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Duration":{"Type": "FORWARD", "Hour": 8}}',
                },
            },
        },
        ['2021-06-24T00:46:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок в понедельник',
        {
            'rules': {
                'Date': {'Pos': '4', 'Length': '2', 'Body': '{"DayOfWeek":1}'},
            },
        },
        ['2021-06-21T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок через день в 12:08',
        {
            'rules': {
                'Date': {
                    'Pos': ['4', '6'],
                    'Length': ['2', '3'],
                    'Body': [
                        '{"Duration":{"Type":"FORWARD","Day":1}}',
                        '{"TimePrep":"в","Hour":12,"Min":8}',
                    ],
                },
            },
        },
        ['2021-06-24T12:08:00'],
        True,
    ),
    (
        'Добрый день! На завтра отмените урок',
        {
            'rules': {
                'Date': {'Pos': '2', 'Length': '2', 'Body': '{"Day":"1D"}'},
            },
        },
        ['2021-06-24T12:00:00'],
        True,
    ),
    ('Добрый день! На 14 число отмените урок', {'rules': {}}, [], True),
    (
        'Добрый день! Отмените сегодня урок',
        {
            'rules': {
                'Date': {'Pos': '3', 'Length': '1', 'Body': '{"Day":"0D"}'},
            },
        },
        ['2021-06-23T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок 27.06',
        {'rules': {'Text': {'Request': 'добрый день! отмените урок 27.06'}}},
        ['2021-06-27T12:00:00'],
        True,
    ),
    ('', 'wizerror=Some+error', [], False),
    ('??', 'wizerror=Some+error', [], False),
    ('13', 'wizerror=Some+error', [], False),
    (
        'перенесите урок с сегодня на завтра в 12:00',
        {
            'rules': {
                'Date': {
                    'Pos': ['3', '4'],
                    'Length': ['1', '5'],
                    'Body': [
                        '{"Day":"0D"}',
                        '{"Prep": "на", "TimePrep": "в", "Day": "1D", "Hour": 12, "Min": 0}',  # noqa
                    ],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-24T12:00:00'],
        True,
    ),
    (
        'перенесите урок 31 августа на сентябрь',
        {
            'rules': {
                'Date': {
                    'Pos': ['3', '4'],
                    'Length': ['1', '5'],
                    'Body': [
                        '{"Day": 31, "Month": 8}',
                        '{"Day": 31, "Prep": "на", "Month": 9}',
                    ],
                },
            },
        },
        ['2021-08-31T12:00:00', '2021-09-30T12:00:00'],
        True,
    ),
    (
        'перенесите урок на завтра с сегодня',
        {
            'rules': {
                'Date': {
                    'Pos': ['2', '5'],
                    'Length': ['2', '1'],
                    'Body': ['{"Prep": "на", "Day":"1D"}', '{"Day":"0D"}'],
                },
            },
        },
        ['2021-06-24T12:00:00', '2021-06-23T12:00:00'],
        True,
    ),
    (
        'перенесите урок завтра на 12:00 с 13:00',
        {
            'rules': {
                'Date': {
                    'Pos': ['2', '7'],
                    'Length': ['4', '2'],
                    'Body': [
                        '{"TimePrep": "на", "Hour": 13, "Min": 0, "Day":"1D"}',  # noqa
                        '{"Hour": 12, "Min": 0}',
                    ],
                },
            },
        },
        ['2021-06-24T13:00:00', '2021-06-24T12:00:00'],
        True,
    ),
    (
        'меня интересуют экскурсии с 3.07 по 8.07 в Калининграде',
        {
            'rules': {
                'Text': {
                    'Request': (
                        'меня интересуют экскурсии '
                        'с 3.07 по 8.07 в калининграде'
                    ),
                },
                'Date': {
                    'Pos': '3',
                    'Length': '6',
                    'Body': (
                        '{"Interval":'
                        '{"From":{"Month":7,"Prep":"с","Day":3},'
                        '"To":{"Month":7,"Prep":"по","Day":8}}}'
                    ),
                },
            },
        },
        ['2021-07-03T12:00:00', '2021-07-08T12:00:00'],
        True,
    ),
    (
        (
            'Добрый вечер.<br /> Не успеваем на урок сегодня. '
            'Отмените, пожалуйста. Будем во вторник по расписанию.'
        ),
        {
            'rules': {
                'Text': {
                    'Request': (
                        'добрый вечер.<br /> не успеваем'
                        ' на урок сегодня. отмените, пожалуйста. '
                        'будем во вторник по расписанию.'
                    ),
                },
                'Date': {
                    'Pos': ['7', '12'],
                    'Length': ['1', '1'],
                    'Body': ['{"Day":"0D"}', '{"DayOfWeek":2}'],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-22T12:00:00'],
        True,
    ),
    (
        (
            'Добрый день! Просьба на 15.01 отменить разово урок.'
            '<br /> Это всё. Благодарю'
        ),
        {
            'rules': {
                'Text': {
                    'Request': (
                        'добрый день! просьба на 15.01 '
                        'отменить разово урок.<br /> это всё. благодарю'
                    ),
                },
            },
        },
        ['2021-01-15T12:00:00'],
        True,
    ),
    (
        (
            'Доброе утро, прошу отменить сегодняшнее занятие, '
            'так как мы будем в пути, возвращаемся с каникул.'
            ' В четверг уже будет как планировалось'
        ),
        {
            'rules': {
                'Text': {
                    'Request': (
                        'доброе утро, прошу отменить'
                        ' сегодняшнее занятие, так как мы будем '
                        'в пути, возвращаемся с каникул. '
                        'в четверг уже будет как планировалось'
                    ),
                },
                'Date': {
                    'Pos': ['4', '15'],
                    'Length': ['1', '2'],
                    'Body': ['{"Day":"0D"}', '{"DayOfWeek":4,"Prep":"в"}'],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-24T12:00:00'],
        True,
    ),
    (
        (
            'Здравствуйте. Отмените пожалуйста сегодня занятие.'
            ' С субботы продолжим в обычном порядке'
        ),
        {
            'rules': {
                'Text': {
                    'Request': (
                        'здравствуйте. отмените пожалуйста '
                        'сегодня занятие. '
                        'с субботы продолжим в обычном порядке'
                    ),
                },
                'Date': {
                    'Pos': ['3', '6'],
                    'Length': ['1', '1'],
                    'Body': ['{"Day":"0D"}', '{"DayOfWeek":6}'],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-26T12:00:00'],
        True,
    ),
    (
        'Доброго ранку! <br /> Можна відмінити заняття 04.01 будь ласка?',
        {
            'rules': {
                'Text': {
                    'Request': (
                        'доброго ранку! <br /> можна '
                        'відмінити заняття 04.01 будь ласка?'
                    ),
                },
            },
        },
        ['2021-01-04T12:00:00'],
        True,
    ),
    (
        (
            'Курс География Подготовка к ОГЭ 8-9 классы здраствуйте'
            ' я бы хотела отменить урок в понедельник(24 января) и '
            'продолжить заниматься по расписанию.'
        ),
        {
            'rules': {
                'Text': {
                    'Request': (
                        'курс география подготовка к огэ '
                        '8-9 классы здраствуйте я бы хотела отменить '
                        'урок в понедельник(24 января) и продолжить '
                        'заниматься по расписанию.'
                    ),
                },
                'Date': {
                    'Pos': ['14', '16'],
                    'Length': ['2', '2'],
                    'Body': [
                        '{"DayOfWeek":1,"Prep":"в"}',
                        '{"Month":1,"Day":24}',
                    ],
                },
            },
        },
        ['2021-06-21T12:00:00', '2021-01-24T12:00:00'],
        True,
    ),
    (
        'какие у вас есть экскурсии на 13.07  2021?',
        {
            'rules': {
                'Text': {
                    'Request': 'какие у вас есть экскурсии на 13.07 2021?',
                },
                'Date': {
                    'Pos': '6',
                    'Length': '3',
                    'Body': '{"Month":7,"Day":13,"Year":2021}',
                    'Year': '2021',
                },
            },
        },
        ['2021-07-13T12:00:00'],
        True,
    ),
    (
        'какие у вас есть экскурсии на 13.07.21?',
        {
            'rules': {
                'Text': {'Request': 'какие у вас есть экскурсии на 13.07.21?'},
                'Date': {
                    'Pos': '6',
                    'Length': '3',
                    'root': 'root20',
                    'RuleResult': '3',
                    'Body': '{"Month":7,"Day":13,"Year":21}',
                    'Year': '2021',
                },
            },
        },
        ['2021-07-13T12:00:00'],
        True,
    ),
    (
        'дата рождения 13.07.30',
        {
            'rules': {
                'Text': {'Request': 'дата рождения 13.07.30'},
                'Date': {
                    'Pos': '2',
                    'Length': '3',
                    'root': 'root20',
                    'RuleResult': '3',
                    'Body': '{"Month":7,"Day":13,"Year":30}',
                    'Year': '1930',
                },
            },
        },
        ['1930-07-13T12:00:00'],
        True,
    ),
    (
        'я ищу экскурсию на 13.07.24',
        {
            'rules': {
                'Text': {'Request': 'я ищу экскурсию на 13.07.24'},
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'root': 'root20',
                    'RuleResult': '3',
                    'Body': '{"Month":7,"Day":13,"Year":24}',
                    'Year': '2024',
                },
            },
        },
        ['2024-07-13T12:00:00'],
        True,
    ),
]


@pytest.mark.now('2021-06-23T16:46')
async def test_datetime_entity_extractor(create_nlu, web_context, core_flags):
    for text, wiz_response, result, _ in PARAMETERS:
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

        assert nlu_response.entities['datetime'].values == result


PARAMETERS2 = [
    (
        'Я буду в Праге с 14 января по 18 января',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '6',
                    'Body': (
                        '{"Interval":'
                        '{"From":{"Month":1,"Prep":"с","Day":14},'
                        '"To":{"Month":1,"Prep":"по","Day":18}}}'
                    ),
                },
            },
        },
        ['2022-01-14T12:00:00', '2022-01-18T12:00:00'],
        True,
    ),
    (
        'Я буду в Лондоне с 2 февраля на 10 февраля',
        {
            'rules': {
                'Date': {
                    'Pos': ['5', '8'],
                    'Length': ['2', '2'],
                    'Body': ['{"Month":2,"Day":2}', '{"Month":2,"Day":10}'],
                },
            },
        },
        ['2022-02-02T12:00:00', '2022-02-10T12:00:00'],
        True,
    ),
    (
        'Я был в отпуске c 4 декабря по 11 декабря',
        {
            'rules': {
                'Date': {
                    'Pos': ['5', '8'],
                    'Length': ['2', '2'],
                    'Body': ['{"Month":12,"Day":4}', '{"Month":12,"Day":11}'],
                },
            },
        },
        ['2021-12-04T12:00:00', '2021-12-11T12:00:00'],
        True,
    ),
    (
        'Я буду в питере с 7 до 17 марта',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '5',
                    'Body': [
                        (
                            '{"Interval":'
                            '{"From":{"Month":3,"Prep":"с","Day":7},'
                            '"To":{"Month":3,"Prep":"до","Day":17}}}'
                        ),
                    ],
                },
            },
        },
        ['2022-03-07T12:00:00', '2022-03-17T12:00:00'],
        True,
    ),
    (
        'С 12 до 19 апреля я буду Сеуле',
        {
            'rules': {
                'Date': {
                    'Pos': '0',
                    'Length': '5',
                    'Body': [
                        (
                            '{"Interval":'
                            '{"From":{"Month":4,"Prep":"с","Day":12},'
                            '"To":{"Month":4,"Prep":"до","Day":19}}}'
                        ),
                    ],
                },
            },
        },
        ['2022-04-12T12:00:00', '2022-04-19T12:00:00'],
        True,
    ),
]


@pytest.mark.now('2021-12-14T16:46')
async def test_datetime_entity_extractor_2(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result, _ in PARAMETERS2:

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

        assert nlu_response.entities['datetime'].values == result


PARAMETERS3 = [
    (
        'Я был в Праге с 14 декабря по 18 декабря',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '6',
                    'Body': (
                        '{"Interval":'
                        '{"From":{"Month":12,"Prep":"с","Day":14},'
                        '"To":{"Month":12,"Prep":"по","Day":18}}}'
                    ),
                },
            },
        },
        ['2021-12-14T12:00:00', '2021-12-18T12:00:00'],
        True,
    ),
    (
        'Я буду в Лондоне с 2 февраля на 10 февраля',
        {
            'rules': {
                'Date': {
                    'Pos': ['5', '8'],
                    'Length': ['2', '2'],
                    'Body': ['{"Month":2,"Day":2}', '{"Month":2,"Day":10}'],
                },
            },
        },
        ['2022-02-02T12:00:00', '2022-02-10T12:00:00'],
        True,
    ),
    (
        'Я был в отпуске c 4 декабря на 11 декабря',
        {
            'rules': {
                'Date': {
                    'Pos': ['5', '8'],
                    'Length': ['2', '2'],
                    'Body': ['{"Month":12,"Day":4}', '{"Month":12,"Day":11}'],
                },
            },
        },
        ['2021-12-04T12:00:00', '2021-12-11T12:00:00'],
        True,
    ),
    (
        'Я буду в питере с 7 до 17 марта',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '5',
                    'Body': [
                        (
                            '{"Interval":'
                            '{"From":{"Month":3,"Prep":"с","Day":7},'
                            '"To":{"Month":3,"Prep":"до","Day":17}}}'
                        ),
                    ],
                },
            },
        },
        ['2022-03-07T12:00:00', '2022-03-17T12:00:00'],
        True,
    ),
    (
        'С 1 по 3 января я был в Кипре',
        {
            'rules': {
                'Date': {
                    'Pos': '0',
                    'Length': '5',
                    'Body': [
                        (
                            '{"Interval":'
                            '{"From":{"Month":1,"Prep":"с","Day":1},'
                            '"To":{"Month":1,"Prep":"по","Day":3}}}'
                        ),
                    ],
                },
            },
        },
        ['2022-01-01T12:00:00', '2022-01-03T12:00:00'],
        True,
    ),
    (
        'Хочу какую-нибудь интересную экскурсию в эти выходные',
        {
            'rules': {
                'Text': {
                    'Request': (
                        'хочу какую-нибудь интересную '
                        'экскурсию в эти выходные'
                    ),
                },
            },
        },
        ['2022-01-08T12:00:00', '2022-01-09T12:00:00'],
        True,
    ),
]


@pytest.mark.now('2022-01-05T16:46')
async def test_datetime_entity_extractor_3(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result, _ in PARAMETERS3:
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

        assert nlu_response.entities['datetime'].values == result


PARAMETERS4 = [
    #  31.08.2021: "Body": "{\"Month\":8,\"Day\":31,\"Year\":2021}", "Year": "2021"}  # noqa
    # 2 дня назад"Body": "{\"Duration\":{\"Type\":\"BACK\",\"Day\":2}}"}
    # через 1 день "Body": "{\"Duration\":{\"Type\":\"FORWARD\",\"Day\":1}}"}  # noqa
    # В понедельник "Body": "{\"DayOfWeek\":1,\"Prep\":\"в\"}"}
    # вчера: "Body":"{\"Day\":\"-1D\"}"}
    # завтра: "Body":"{\"Day\":\"-1D\"}"}
    # через неделю в 12:08 "Body":["{\"Duration\":{\"Week\":1,\"Type\":\"FORWARD\"}}","{\"TimePrep\":\"в\",\"Hour\":12,\"Min\":8}"]}  # noqa
    (
        'Добрый день! Отмените урок 31.08.2021',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Day":31, "Month":8, "Year":2021}',
                },
            },
        },
        ['2021-08-31T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок 2 дня назад',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Duration":{"Type": "BACK", "Day": 2}}',
                },
            },
        },
        ['2021-06-21T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок через 8 часов',
        {
            'rules': {
                'Date': {
                    'Pos': '4',
                    'Length': '3',
                    'Body': '{"Duration":{"Type": "FORWARD", "Hour": 8}}',
                },
            },
        },
        ['2021-06-24T00:46:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок в понедельник',
        {
            'rules': {
                'Date': {'Pos': '4', 'Length': '2', 'Body': '{"DayOfWeek":1}'},
            },
        },
        ['2021-06-28T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок в воскресенье',
        {
            'rules': {
                'Date': {'Pos': '4', 'Length': '2', 'Body': '{"DayOfWeek":0}'},
            },
        },
        ['2021-06-27T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок в cубботу',
        {
            'rules': {
                'Date': {'Pos': '4', 'Length': '2', 'Body': '{"DayOfWeek":6}'},
            },
        },
        ['2021-06-26T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок во вторник',
        {
            'rules': {
                'Date': {'Pos': '5', 'Length': '1', 'Body': '{"DayOfWeek":2}'},
            },
        },
        ['2021-06-29T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок в пятницу',
        {
            'rules': {
                'Date': {'Pos': '4', 'Length': '2', 'Body': '{"DayOfWeek":5}'},
            },
        },
        ['2021-06-25T12:00:00'],
        True,
    ),
    (
        'Добрый день! Отмените урок через день в 12:08',
        {
            'rules': {
                'Date': {
                    'Pos': ['4', '6'],
                    'Length': ['2', '3'],
                    'Body': [
                        '{"Duration":{"Type": "FORWARD", "Day": 1}}',
                        '{"Hour": 12, "Min": 8}',
                    ],
                },
            },
        },
        ['2021-06-24T12:08:00'],
        True,
    ),
    (
        'Добрый день! На завтра отмените урок',
        {
            'rules': {
                'Date': {'Pos': '2', 'Length': '2', 'Body': '{"Day":"1D"}'},
            },
        },
        ['2021-06-24T12:00:00'],
        True,
    ),
    ('Добрый день! На 14 число отмените урок', {'rules': {}}, [], True),
    (
        'Добрый день! Отмените сегодня урок',
        {
            'rules': {
                'Date': {'Pos': '3', 'Length': '1', 'Body': '{"Day":"0D"}'},
            },
        },
        ['2021-06-23T12:00:00'],
        True,
    ),
    ('', 'wizerror=Some+error', [], False),
    ('??', 'wizerror=Some+error', [], False),
    ('13', 'wizerror=Some+error', [], False),
    (
        'перенесите урок с сегодня на завтра в 12:00',
        {
            'rules': {
                'Date': {
                    'Pos': ['3', '4'],
                    'Length': ['1', '5'],
                    'Body': [
                        '{"Day":"0D"}',
                        '{"Prep": "на", "TimePrep": "в", "Day": "1D", "Hour": 12, "Min": 0}',  # noqa
                    ],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-24T12:00:00'],
        True,
    ),
    (
        'перенесите урок на завтра с сегодня',
        {
            'rules': {
                'Date': {
                    'Pos': ['2', '5'],
                    'Length': ['2', '1'],
                    'Body': ['{"Prep":"на","Day":"1D"}', '{"Day":"0D"}'],
                },
            },
        },
        ['2021-06-24T12:00:00', '2021-06-23T12:00:00'],
        True,
    ),
    (
        'перенесите урок завтра на 12:00 с 13:00',
        {
            'rules': {
                'Date': {
                    'Pos': ['2', '7'],
                    'Length': ['4', '2'],
                    'Body': [
                        '{"TimePrep": "на", "Hour": 13, "Min": 0, "Day":"1D"}',  # noqa
                        '{"Hour": 12, "Min": 0}',
                    ],
                },
            },
        },
        ['2021-06-24T13:00:00', '2021-06-24T12:00:00'],
        True,
    ),
]


@pytest.mark.now('2021-06-23T16:46')
async def test_weekday_from_future_datetime_entity_extractor(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result, _ in PARAMETERS4:
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

        assert (
            nlu_response.entities[
                'weekday_from_future_datetime_extractor'
            ].values
            == result
        )


PARAMETERS5 = [
    (
        'перенесите урок на завтра с сегодня',
        {
            'rules': {
                'Date': {
                    'Pos': ['2', '5'],
                    'Length': ['2', '1'],
                    'Body': ['{"Prep": "на", "Day":"1D"}', '{"Day":"0D"}'],
                },
            },
        },
        ['2021-06-23T12:00:00', '2021-06-24T12:00:00'],
    ),
    (
        'отмени урок сегодня',
        {
            'rules': {
                'Date': {'Pos': '2', 'Length': '1', 'Body': ['{"Day":"0D"}']},
            },
        },
        [],
    ),
    (
        'отмени урок на завтра',
        {
            'rules': {
                'Date': {
                    'Pos': '2',
                    'Length': '2',
                    'Body': ['{"Prep": "на", "Day":"1D"}'],
                },
            },
        },
        ['2021-06-23T16:46:00', '2021-06-24T12:00:00'],
    ),
]


@pytest.mark.now('2021-06-23T16:46')
async def test_source_target_datetime_entity_extractor(
        create_nlu, web_context, core_flags,
):
    for text, wiz_response, result in PARAMETERS5:
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

        assert nlu_response.entities['source_target_datetime'].values == result
