import json
import os

from taxi_pyml.supportai.common import actions_determinant
from taxi_pyml.supportai.common import model_topics
from taxi_pyml.supportai.common import postprocess
from taxi_pyml.supportai.common import types
from taxi_pyml.supportai.common import standard_tags

from taxi_pyml.supportai import objects


def test_actions_determinant_config(get_file_path):
    config = actions_determinant.Config.from_config_filepath(
        get_file_path('resources_actions/actions_config.json'),
    )
    meta_info = {'a': 1}
    model_topics_response = model_topics.Response(
        most_probable_topic='hello',
        sure_topic='hello',
        tags=[],
        probabilities=[
            objects.TopicProbability(topic_name='hello', probability=0.8),
            objects.TopicProbability(topic_name='goodbye', probability=0.2),
        ],
    )
    response = config(meta_info, model_topics_response)
    assert response.actions == [
        {'action': 'close', 'arguments': {'macro_id': 1}},
    ]
    assert response.tags == []

    meta_info = {'a': 2}
    model_topics_response = model_topics.Response(
        most_probable_topic='goodbye',
        sure_topic='goodbye',
        tags=[],
        probabilities=[
            objects.TopicProbability(topic_name='hello', probability=0.2),
            objects.TopicProbability(topic_name='goodbye', probability=0.8),
        ],
    )
    response = config(meta_info, model_topics_response)
    assert response.actions == [
        {'action': 'comment', 'arguments': {'macro_id': 2}},
    ]
    assert response.tags == []

    meta_info = {'a': 2}
    model_topics_response = model_topics.Response(
        most_probable_topic='hello',
        sure_topic='hello',
        tags=[],
        probabilities=[
            objects.TopicProbability(topic_name='hello', probability=0.8),
            objects.TopicProbability(topic_name='goodbye', probability=0.2),
        ],
    )
    response = config(meta_info, model_topics_response)
    assert response.actions == []
    assert response.tags == ['ml_fail_rules', 'ml_fail_rules_hello']

    meta_info = {'a': 2}
    model_topics_response = model_topics.Response(
        most_probable_topic='thank_u',
        sure_topic='thank_u',
        tags=[],
        probabilities=[
            objects.TopicProbability(topic_name='hello', probability=0.8),
            objects.TopicProbability(topic_name='goodbye', probability=0.2),
        ],
    )
    response = config(meta_info, model_topics_response)
    assert response.actions == []
    assert response.tags == [
        'ml_fail_absent_topic',
        'ml_fail_absent_topic_thank_u',
    ]


def test_model_topics_config(get_file_path):
    config = model_topics.Config.from_config_filepath(
        get_file_path('resources_actions/model_topics_config.json'),
    )

    data_request_1 = types.Request(
        dialog=objects.Dialog(messages=[objects.Message(text='привет')]),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': ''},
        ],
    )

    data_request_2 = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(author='user', text='привет'),
                objects.Message(author='support', text='привет'),
                objects.Message(author='user', text='как дела?'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'привет\nкак дела?'},
        ],
    )

    data_request_3 = types.Request(
        dialog=objects.Dialog(
            messages=[
                objects.Message(author='user', text='hello'),
                objects.Message(author='support', text='привет'),
                objects.Message(author='user', text='как дела?'),
            ],
        ),
        control_tag='experiment',
        features=[
            {'key': 'a', 'value': 1},
            {'key': 'united_user_messages', 'value': 'hello\nкак дела?'},
        ],
    )

    response = config([0.8, 0.2], data_request=data_request_1)
    assert response.most_probable_topic == 'hello'
    assert response.probabilities == [
        objects.TopicProbability('hello', 0.8),
        objects.TopicProbability('goodbye', 0.2),
    ]
    assert response.sure_topic == 'hello'
    assert response.tags == ['ml_topic_hello', 'ml_topic_net_hello']

    response = config([0.49, 0.51], data_request=data_request_1)
    assert response.most_probable_topic == 'goodbye'
    assert response.probabilities == [
        objects.TopicProbability('hello', 0.49),
        objects.TopicProbability('goodbye', 0.51),
    ]
    assert response.sure_topic == 'hello'
    assert response.tags == ['ml_topic_hello', 'ml_topic_net_hello']

    response = config([0.8, 0.2], data_request=data_request_2)
    assert response.most_probable_topic == 'hello'
    assert response.probabilities == [
        objects.TopicProbability('hello', 0.8),
        objects.TopicProbability('goodbye', 0.2),
    ]
    assert response.sure_topic is None
    assert response.tags == [
        'ml_fail_not_sure_in_topic',
        'ml_fail_not_sure_in_topic_hello',
    ]

    response = config([0.8, 0.2], data_request=data_request_3)
    assert response.most_probable_topic == 'hello'
    assert response.probabilities == [
        objects.TopicProbability('hello', 0.8),
        objects.TopicProbability('goodbye', 0.2),
    ]
    assert response.sure_topic == 'hello'
    assert response.tags == ['ml_topic_hello', 'ml_topic_rules_hello']
    # TODO nickpon: test probabilities counter in a tree


def test_model_topics_config_pure_probabilites(get_file_path):
    config = model_topics.Config.from_config_filepath(
        get_file_path('resources_actions/model_topics_config.json'),
    )
    assert config.get_pure_probabilites(
        [
            objects.TopicProbability(topic_name='goodbye', probability=0.9),
            objects.TopicProbability(topic_name='hello', probability=0.1),
        ],
    ) == [0.1, 0.9]


def test_postprocessor_with_actions(get_directory_path):
    postprocessor = postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_actions'),
    )
    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='привет')]),
            control_tag='experiment',
            features=[{'key': 'a', 'value': 1}],
        ),
    )
    assert response.reply.text == 1
    assert response.close is not None
    assert response.tag.add == [
        'ml_topic_hello',
        'ml_topic_net_hello',
        'experiment',
        'ar_done',
    ]

    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(
                messages=[objects.Message(text='привет', author='user')],
            ),
            control_tag='experiment',
            features=[{'key': 'a', 'value': 2}],
        ),
    )
    assert response.reply is None
    assert response.close is None
    assert response.tag.add == [
        'ml_topic_hello',
        'ml_topic_net_hello',
        'ml_fail_rules',
        'ml_fail_rules_hello',
        'experiment',
    ]


def run_postprocessor_with_scenarios(postprocessor):
    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='привет')]),
            control_tag='experiment',
            features=[],
        ),
    )
    assert response.reply.text == 'Номер телефона?'
    assert response.tag.add == [
        'ml_topic_hello',
        'ml_topic_net_hello',
        'ml_clarify_phone',
        'experiment',
        'ar_done',
    ]

    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(
                messages=[
                    objects.Message(text='привет', author='user'),
                    objects.Message(text='Номер телефона?', author='support'),
                    objects.Message(text='123', author='user'),
                ],
            ),
            control_tag='experiment',
            features=[{'key': '_topic', 'value': 'hello'}],
        ),
    )
    assert (
        response.reply.text == 'Номер заказа?[NEW]Только не сообщайте никому'
    )
    assert response.tag.add == ['ml_clarify_order_id', 'experiment', 'ar_done']
    assert (
        objects.Feature(key='phone', value='123')
        in response.features.extracted_features
    )

    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(
                messages=[
                    objects.Message(text='привет', author='user'),
                    objects.Message(text='Номер телефона?', author='support'),
                    objects.Message(text='123', author='user'),
                    objects.Message(text='Номер заказа?', author='support'),
                    objects.Message(
                        text='Только не сообщайте никому', author='support',
                    ),
                    objects.Message(text='456', author='user'),
                ],
            ),
            control_tag='experiment',
            features=[{'key': '_topic', 'value': 'hello'}],
        ),
    )
    assert response.reply is None
    assert (
        objects.Feature(key='phone', value='123')
        in response.features.extracted_features
    )
    assert (
        objects.Feature(key='order_id', value='456')
        in response.features.extracted_features
    )
    assert response.tag.add == [
        'ml_clarify_backend_features',
        'test_tag',
        'experiment',
    ]

    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(
                messages=[
                    objects.Message(text='привет', author='user'),
                    objects.Message(text='Номер телефона?', author='support'),
                    objects.Message(text='123', author='user'),
                    objects.Message(text='Номер заказа?', author='support'),
                    objects.Message(
                        text='Только не сообщайте никому', author='support',
                    ),
                    objects.Message(text='456', author='user'),
                ],
            ),
            control_tag='experiment',
            features=[
                {'key': '_topic', 'value': 'hello'},
                {'key': 'amount', 'value': 150},
            ],
        ),
    )
    assert response.reply.text == 'Big amount'
    assert (
        objects.Feature(key='phone', value='123')
        in response.features.extracted_features
    )
    assert (
        objects.Feature(key='order_id', value='456')
        in response.features.extracted_features
    )
    assert response.tag.add == ['test_tag', 'experiment', 'ar_done']


def test_postprocessor_with_scenarios_from_file(get_directory_path):
    postprocessor = postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_scenarios'),
    )

    run_postprocessor_with_scenarios(postprocessor)


def test_postprocessor_with_scenarios_from_dict(get_directory_path):

    directory = get_directory_path('resources_scenarios')

    with open(os.path.join(directory, 'scenarios_config.json'), 'r') as file:
        scenarios_config = json.load(file)

    with open(
            os.path.join(directory, 'model_topics_config.json'), 'r',
    ) as file:
        model_topics_config = json.load(file)

    postprocessor = postprocess.Postprocessor.from_config_data(
        {
            'scenarios_config': scenarios_config,
            'model_topics_config': model_topics_config,
        },
    )

    run_postprocessor_with_scenarios(postprocessor)


def test_postprocessor_control(get_directory_path):
    postprocessor = postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_actions'),
    )
    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='привет')]),
            control_tag=standard_tags.ML_CONTROL_GROUP,
            features=[{'key': 'a', 'value': 1}],
        ),
    )

    assert response.reply is None
    assert response.close is None
    assert response.defer is None
    assert response.forward is None

    assert response.features.suggest is None
    assert response.tag.add == [
        'ml_topic_hello',
        'ml_topic_net_hello',
        'ml_fail_control',
    ]

    response = postprocessor(
        [0.8, 0.2],
        types.Request(
            dialog=objects.Dialog(
                messages=[objects.Message(text='привет', author='user')],
            ),
            control_tag='ml_fail_control',
            features=[{'key': 'a', 'value': 2}],
        ),
    )
    assert response.reply is None
    assert response.close is None
    assert response.defer is None
    assert response.forward is None

    assert response.features.suggest is None
    assert response.tag.add == [
        'ml_topic_hello',
        'ml_topic_net_hello',
        'ml_fail_rules',
        'ml_fail_rules_hello',
        'ml_fail_control',
    ]


# TODO: add test after adding logic to text features extractor
def test_text_features_extractor(get_file_path):
    pass


def test_dialog_iteration_counter():
    assert (
        model_topics.Config.get_dialog_iteration(
            types.Request(
                dialog=objects.Dialog(
                    messages=[objects.Message(text='привет')],
                ),
                control_tag='experiment',
                features=[{'key': 'a', 'value': 1}],
            ),
        )
        == 1
    )
    assert (
        model_topics.Config.get_dialog_iteration(
            types.Request(
                dialog=objects.Dialog(
                    messages=[objects.Message(text='привет', author='user')],
                ),
                control_tag='experiment',
                features=[{'key': 'a', 'value': 1}],
            ),
        )
        == 1
    )
    assert (
        model_topics.Config.get_dialog_iteration(
            types.Request(
                dialog=objects.Dialog(
                    messages=[
                        objects.Message(text='привет', author='user'),
                        objects.Message(text='привет2', author='ai'),
                        objects.Message(text='привет3', author='user'),
                        objects.Message(text='привет4', author='support'),
                    ],
                ),
                control_tag='experiment',
                features=[{'key': 'a', 'value': 1}],
            ),
        )
        == 3
    )


def test_f_string_bot_answer_formatter(get_directory_path):
    postprocessor = postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_scenarios'),
    )
    response = postprocessor(
        [0.1, 0.9],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='Привет')]),
            features=[
                {'key': 'tariff', 'value': 'vse_svoi'},
                {'key': 'phone_number', 'value': 55500},
            ],
            control_tag='experiment',
        ),
    )
    assert response.reply.text == 'Номер телефона 55500?'
    response = postprocessor(
        [0.1, 0.9],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='Привет')]),
            features=[
                {'key': 'tariff', 'value': 'vse_ne_svoi'},
                {'key': 'phone_number', 'value': 55500},
            ],
            control_tag='experiment',
        ),
    )
    assert response.reply.text == 'vse_ne_svoi 55500'

    response = postprocessor(
        [0.1, 0.9],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='Привет')]),
            features=[{'key': 'tariff', 'value': 'vse_ne_svoi'}],
            control_tag='experiment',
        ),
    )

    assert response.reply is None
    assert 'string_feature_not_found' in response.tag.add

    response = postprocessor(
        [0.1, 0.9],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text='Привет')]),
            features=[{'key': 'tariff', 'value': 'vse_svoi'}],
            control_tag='experiment',
        ),
    )
    assert response.reply is None

    response = postprocessor(
        [0.1, 0.9],
        types.Request(
            dialog=objects.Dialog(messages=[objects.Message(text=None)]),
            features=[{'key': 'tariff', 'value': 'check_none'}],
            control_tag='experiment',
        ),
    )
    assert response.reply is None
    assert response.defer.time_sec == 10
