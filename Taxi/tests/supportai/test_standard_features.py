from taxi_pyml.supportai import objects
from taxi_pyml.supportai.common import standard_features, types


def test_get_user_messages():
    assert (
        standard_features.get_united_user_messages(
            [
                objects.Message(author='user', text='привет'),
                objects.Message(author='user', text='хотел бы отменить заказ'),
            ],
        )[1]
        == 'привет\nхотел бы отменить заказ'
    )

    assert (
        standard_features.get_united_user_messages(
            [
                objects.Message(author='user', text='привет'),
                objects.Message(author='user', text='хотел бы отменить заказ'),
                objects.Message(author='ai', text='уточните номер заказа'),
                objects.Message(author='user', text='номер 123456'),
            ],
        )[1]
        == 'привет\nхотел бы отменить заказ\nномер 123456'
    )

    assert (
        standard_features.get_united_user_messages(
            [
                objects.Message(author='ai', text='привет'),
                objects.Message(author='ai', text='хотел бы отменить заказ'),
                objects.Message(author='ai', text='уточните номер заказа'),
                objects.Message(author='support', text='номер 123456'),
            ],
        )[1]
        == ''
    )


def test_get_iteration_number():
    assert (
        standard_features.get_iteration_number(
            [
                objects.Message(author='user', text='привет'),
                objects.Message(author='user', text='хотел бы отменить заказ'),
            ],
        )[1]
        == 1
    )
    assert standard_features.get_iteration_number([])[1] == 0
    assert (
        standard_features.get_iteration_number(
            [
                objects.Message(author='user', text='привет'),
                objects.Message(author='support', text='привет'),
            ],
        )[1]
        == 1
    )
    assert (
        standard_features.get_iteration_number(
            [
                objects.Message(author='user', text='привет'),
                objects.Message(author='support', text='привет'),
                objects.Message(author='user', text='где заказ?'),
            ],
        )[1]
        == 2
    )
    assert (
        standard_features.get_iteration_number(
            [objects.Message(author='support', text='привет')],
        )[1]
        == 1
    )


def test_add_standard_features():
    dialog = objects.Dialog(
        messages=[
            objects.Message(author='user', text='привет'),
            objects.Message(author='user', text='хотел бы отменить заказ'),
        ],
    )
    control_tag = 'experiment'

    request = types.Request.create_request_with_standard_features(
        dialog=dialog, control_tag=control_tag, features=[],
    )
    assert request.dialog == dialog
    assert request.control_tag == control_tag
    assert request.features == [
        {
            'key': standard_features.USER_MESSAGES_FEATURE_NAME,
            'value': 'привет\nхотел бы отменить заказ',
        },
        {
            'key': standard_features.USER_MESSAGES_LENGTH_FEATURE_NAME,
            'value': len('привет\nхотел бы отменить заказ'),
        },
        {
            'key': standard_features.LAST_USER_MESSAGE_FEATURE_NAME,
            'value': 'хотел бы отменить заказ',
        },
        {
            'key': standard_features.LAST_USER_MESSAGE_LENGTH_FEATURE_NAME,
            'value': len('хотел бы отменить заказ'),
        },
        {'key': standard_features.ITERATION_NUMBER_FEATURE_NAME, 'value': 1},
        {
            'key': standard_features.NORMALIZED_USER_MESSAGES_FEATURE_NAME,
            'value': 'привет хотеть бы отменить заказ',
        },
        {
            'key': standard_features.NORMALIZED_LAST_USER_MESSAGE_FEATURE_NAME,
            'value': 'хотеть бы отменить заказ',
        },
    ]

    request = types.Request.create_request_with_standard_features(
        dialog=dialog,
        control_tag=control_tag,
        features=[{'key': 'a', 'value': 123}, {'key': 'b', 'value': True}],
    )

    assert request.dialog == dialog
    assert request.control_tag == control_tag
    assert request.features == [
        {'key': 'a', 'value': 123},
        {'key': 'b', 'value': True},
        {
            'key': standard_features.USER_MESSAGES_FEATURE_NAME,
            'value': 'привет\nхотел бы отменить заказ',
        },
        {
            'key': standard_features.USER_MESSAGES_LENGTH_FEATURE_NAME,
            'value': len('привет\nхотел бы отменить заказ'),
        },
        {
            'key': standard_features.LAST_USER_MESSAGE_FEATURE_NAME,
            'value': 'хотел бы отменить заказ',
        },
        {
            'key': standard_features.LAST_USER_MESSAGE_LENGTH_FEATURE_NAME,
            'value': len('хотел бы отменить заказ'),
        },
        {'key': standard_features.ITERATION_NUMBER_FEATURE_NAME, 'value': 1},
        {
            'key': standard_features.NORMALIZED_USER_MESSAGES_FEATURE_NAME,
            'value': 'привет хотеть бы отменить заказ',
        },
        {
            'key': standard_features.NORMALIZED_LAST_USER_MESSAGE_FEATURE_NAME,
            'value': 'хотеть бы отменить заказ',
        },
    ]
