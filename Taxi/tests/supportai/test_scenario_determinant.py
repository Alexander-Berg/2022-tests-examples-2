from taxi_pyml.supportai import objects
from taxi_pyml.supportai.common import (
    model_topics,
    scenario_determinant,
    types,
    text_features_extractor,
)


def test_scenario_check_rule(load_json):
    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_features_can_be_asked.json'),
    )

    features = {'a': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == {'b', 'c'}

    features = {'a': 1, 'b': 'abcd'}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == set()

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_no_need_to_ask.json'),
    )
    features = {'a': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert result.is_true
    assert result.literals == set()

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_undef_feature_cant_be_asked.json'),
    )
    features = {'a': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == set()

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_features_can_be_asked_with_backend_features.json'),
    )
    features = {'a': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == {'b', 'c', 'd', 'e'}

    features = {'a': 1, 'b': 'abcd'}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == set()

    features = {'a': 1, 'd': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == {'b', 'c', 'e'}

    features = {'a': 1, 'd': 2}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == set()

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_no_need_to_ask_with_backend_features.json'),
    )
    features = {'a': 1}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert result.is_true
    assert result.literals == set()

    features = {'a': 2}
    result = scenario._check_rule(scenario.rule_value.ast, features)
    assert not result.is_true
    assert result.literals == set()


def test_scenario_analyze(load_json):
    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_features_can_be_asked.json'),
    )

    result = scenario.analyze(features={'a': 1})
    assert not result.is_true
    assert result.feature_to_ask.slug == 'b'

    result = scenario.analyze(features={'a': 1, 'b': 'abc'})
    assert not result.is_true
    assert result.feature_to_ask.slug == 'c'

    result = scenario.analyze(features={'a': 1, 'b': 'abcd'})
    assert not result.is_true
    assert result.feature_to_ask is None

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_no_need_to_ask.json'),
    )

    result = scenario.analyze(features={'a': 1, 'b': 'abcd'})
    assert result.is_true
    assert result.feature_to_ask is None

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_undef_feature_cant_be_asked.json'),
    )

    result = scenario.analyze(features={'a': 1})
    assert not result.is_true
    assert result.feature_to_ask is None
    assert result.backend_features is None

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_features_can_be_asked_with_backend_features.json'),
    )
    result = scenario.analyze(features={'a': 1})
    assert not result.is_true
    assert result.feature_to_ask.slug == 'b'

    result = scenario.analyze(features={'a': 1, 'b': 'abc', 'c': False})
    assert not result.is_true
    assert result.backend_features == [
        text_features_extractor.BackendFeature('d'),
        text_features_extractor.BackendFeature('e'),
    ]

    result = scenario.analyze(
        features={'a': 1, 'b': 'abc', 'c': False, 'd': 1},
    )
    assert not result.is_true
    assert result.backend_features == [
        text_features_extractor.BackendFeature('e'),
    ]

    scenario = scenario_determinant.Scenario.deserialize(
        load_json('scenario_no_need_to_ask_with_backend_features.json'),
    )
    result = scenario.analyze(features={'a': 1, 'b': 'abcd'})
    assert result.is_true
    assert result.feature_to_ask is None
    assert result.backend_features is None


def test_scenarios_determinant(get_file_path):
    config = scenario_determinant.ScenarioDeterminant.from_config_filepath(
        get_file_path('scenarios.json'),
    )

    request = types.Request(
        dialog=objects.Dialog(messages=[objects.Message(text='привет')]),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': ''},
        ],
    )
    assert config(request, None) == scenario_determinant.Response(tags=[])

    model_topics_response = model_topics.Response(
        most_probable_topic='cancel_subscription',
        sure_topic='cancel_subscription',
        tags=[],
        probabilities=[
            objects.TopicProbability(
                topic_name='cancel_subscription', probability=0.8,
            ),
            objects.TopicProbability(
                topic_name='refund_money', probability=0.2,
            ),
        ],
    )
    result = config(request, model_topics_response)
    assert (
        result.clarifying_question
        == 'Как вы оформляли подписку?[NEW]Только честно'
    )
    assert not result.extracted_features

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='Только честно', author='ai'),
                objects.Message(text='appstore', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nappstore'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.scenario.reply_macros_text.startswith(
        'Вы можете отменить подписку через меню устройства c iOS',
    )
    assert result.extracted_features == [
        {'key': 'way_of_making_subscription', 'value': 'App Store'},
        {'key': 'way_of_making_subscription_type', 'value': str},
    ]

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='Только честно', author='ai'),
                objects.Message(text='блабла', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nблабла'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.scenario is None
    assert result.clarifying_question is None
    assert result.tags == [
        'ml_fail_rules',
        'ml_fail_rules_cancel_subscription',
    ]
    assert result.extracted_features == [
        {'key': 'way_of_making_subscription', 'value': None},
        {'key': 'way_of_making_subscription_type', 'value': None},
    ]

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Привет! Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='Только честно', author='ai'),
                objects.Message(text='appstore', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'united_user_messages', 'value': 'привет\nappstore'},
        ],
    )
    result = config(request, model_topics_response)

    assert result.scenario.reply_macros_text.startswith(
        'Вы можете отменить подписку',
    )


def test_scenarios_determinant_button(get_file_path):
    config = scenario_determinant.ScenarioDeterminant.from_config_filepath(
        get_file_path('scenarios.json'),
    )

    request = types.Request(
        dialog=objects.Dialog(messages=[objects.Message(text='контакты')]),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': ''},
        ],
    )

    model_topics_response = model_topics.Response(
        most_probable_topic='button_topic',
        sure_topic='button_topic',
        tags=[],
        probabilities=[
            objects.TopicProbability(
                topic_name='button_topic', probability=0.8,
            ),
            objects.TopicProbability(
                topic_name='refund_money', probability=0.2,
            ),
        ],
    )
    result = config(request, model_topics_response)
    assert result.clarifying_question == 'Выберите тип подписки'
    assert result.extracted_features == [
        {'key': 'button_0', 'value': 'Кнопка 1'},
        {'key': 'button_1', 'value': 'Кнопка 2'},
        {'key': 'button_2', 'value': 'Кнопка 3'},
    ]

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(text='Выберите тип подписки', author='ai'),
                objects.Message(text='Кнопка 2', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nКнопка 2'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.scenario.reply_macros_text == 'Спасибо за ответ'


def test_scenarios_determinant_with_backend_features(get_file_path):
    config = scenario_determinant.ScenarioDeterminant.from_config_filepath(
        get_file_path('scenarios_with_backend_features.json'),
    )

    model_topics_response = model_topics.Response(
        most_probable_topic='cancel_subscription',
        sure_topic='cancel_subscription',
        tags=[],
        probabilities=[
            objects.TopicProbability(
                topic_name='cancel_subscription', probability=0.8,
            ),
            objects.TopicProbability(
                topic_name='refund_money', probability=0.2,
            ),
        ],
    )

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='appstore', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nappstore'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.backend_features == [
        text_features_extractor.BackendFeature('amount'),
    ]
    assert result.tags == ['ml_clarify_backend_features', 'backend_tag']

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='playmarket', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nplaymarket'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.backend_features == [
        text_features_extractor.BackendFeature('amount'),
        text_features_extractor.BackendFeature('subscription_days'),
    ]

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='playmarket', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nplaymarket'},
            {'key': 'amount', 'value': 200},
        ],
    )
    result = config(request, model_topics_response)
    assert result.backend_features == [
        text_features_extractor.BackendFeature('subscription_days'),
    ]

    request = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(text='привет', author='user'),
                objects.Message(
                    text='Как вы оформляли подписку?', author='ai',
                ),
                objects.Message(text='playmarket', author='user'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nplaymarket'},
            {'key': 'amount', 'value': 200},
            {'key': 'subscription_days', 'value': 100},
        ],
    )
    result = config(request, model_topics_response)
    assert result.backend_features is None

    request = types.Request(
        dialog=objects.Dialog(
            messages=[objects.Message(text='привет', author='user')],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет'},
        ],
    )
    result = config(request, model_topics_response)
    assert result.backend_features is None
    assert result.clarifying_question == 'Как вы оформляли подписку?'
    assert result.tags == ['ml_clarify_way_of_making_subscription']
