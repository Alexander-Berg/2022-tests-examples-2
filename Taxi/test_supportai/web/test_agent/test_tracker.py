import pytest

from supportai.common import feature as feature_module
from supportai.common import nlu as nlu_module
from supportai.common import state as state_module
from supportai.common import tracker as tracker_module


def test_map_extracted_slots():
    tracker = tracker_module.DialogStateTracker(namespace='')

    entities = {
        'datetime': nlu_module.Entity(['2021-06-22']),
        'first_name': nlu_module.Entity(['Василий']),
        'language': nlu_module.Entity(['ru']),
    }

    state_features = {
        'some_dttm': feature_module.Feature(
            status=feature_module.Status.IN_PROGRESS,
            value=None,
            spec=feature_module.FeatureSpec(
                key='some_dttm',
                entity='datetime',
                entity_extract_order=0,
                type_='str',
                is_array=False,
            ),
        ),
        'text_language': feature_module.Feature(
            status=feature_module.Status.UNDEFINED,
            value=None,
            spec=feature_module.FeatureSpec(
                key='text_language',
                entity='language',
                entity_extract_order=0,
                type_='str',
                is_array=False,
                can_be_found_without_question=True,
            ),
        ),
        'another_feature': feature_module.Feature(
            status=feature_module.Status.DEFINED,
            value='kek',
            spec=feature_module.FeatureSpec(
                key='another_feature', type_='str', is_array=False,
            ),
        ),
    }
    state = state_module.State(feature_layers=[state_features])
    state_copy = state_module.State(feature_layers=[state_features])

    tracker.update_state_by_entities(state, entities)
    assert len(state.get_features()) == len(state_copy.get_features())
    assert state.get_features()['some_dttm'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value='2021-06-22',
        spec=feature_module.FeatureSpec(
            key='some_dttm',
            entity='datetime',
            entity_extract_order=0,
            type_='str',
            is_array=False,
            can_be_found_without_question=False,
        ),
    )

    assert state.get_features()['text_language'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value='ru',
        spec=feature_module.FeatureSpec(
            key='text_language',
            entity='language',
            entity_extract_order=0,
            type_='str',
            is_array=False,
            can_be_found_without_question=True,
        ),
    )

    assert (
        state.get_features()['another_feature']
        == state_features['another_feature']
    )

    state_features = {
        'some_dttm': feature_module.Feature(
            status=feature_module.Status.IN_PROGRESS,
            value=None,
            spec=feature_module.FeatureSpec(
                key='some_dttm',
                entity='datetime',
                entity_extract_order=0,
                type_='str',
                is_array=False,
            ),
        ),
        'another_dttm': feature_module.Feature(
            status=feature_module.Status.UNDEFINED,
            value=None,
            spec=feature_module.FeatureSpec(
                key='another_dttm',
                entity='datetime',
                entity_extract_order=0,
                type_='str',
                is_array=False,
            ),
        ),
    }
    state = state_module.State(feature_layers=[state_features])
    state_copy = state_module.State(feature_layers=[state_features])

    tracker.update_state_by_entities(state, entities)
    assert len(state.get_features()) == len(state_copy.get_features())
    assert state.get_features()['some_dttm'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value='2021-06-22',
        spec=feature_module.FeatureSpec(
            key='some_dttm',
            entity='datetime',
            entity_extract_order=0,
            type_='str',
            is_array=False,
            can_be_found_without_question=False,
        ),
    )

    assert (
        state.get_features()['another_dttm'] == state_features['another_dttm']
    )

    entities = {
        'number': nlu_module.Entity([123]),
        'first_name': nlu_module.Entity(['Василий']),
        'language': nlu_module.Entity(['ru']),
    }

    state_features = {
        'order_ids': feature_module.Feature(
            status=feature_module.Status.UNDEFINED,
            value=None,
            spec=feature_module.FeatureSpec(
                key='order_ids',
                entity='numbers',
                type_='int',
                is_array=True,
                can_be_found_without_question=True,
            ),
        ),
        'order_id': feature_module.Feature(
            status=feature_module.Status.IN_PROGRESS,
            value=None,
            spec=feature_module.FeatureSpec(
                key='order_ids',
                entity='number',
                entity_extract_order=0,
                type_='int',
                is_array=False,
            ),
        ),
    }
    state = state_module.State(feature_layers=[state_features])
    state_copy = state_module.State(feature_layers=[state_features])

    tracker.update_state_by_entities(state, entities)
    assert len(state.get_features()) == len(state_copy.get_features())
    assert state.get_features()['order_id'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value=123,
        spec=feature_module.FeatureSpec(
            key='order_id',
            entity='number',
            entity_extract_order=0,
            type_='int',
            is_array=False,
            can_be_found_without_question=False,
        ),
    )
    assert state.get_features()['order_ids'] == feature_module.Feature(
        status=feature_module.Status.UNDEFINED,
        value=None,
        spec=feature_module.FeatureSpec(
            key='order_ids',
            entity='numbers',
            type_='int',
            is_array=True,
            can_be_found_without_question=True,
        ),
    )

    entities = {
        'numbers': nlu_module.Entity([123, 456]),
        'first_name': nlu_module.Entity(['Василий']),
        'language': nlu_module.Entity(['ru']),
    }

    state_features = {
        'order_ids': feature_module.Feature(
            status=feature_module.Status.UNDEFINED,
            value=None,
            spec=feature_module.FeatureSpec(
                key='order_ids',
                entity='numbers',
                type_='int',
                is_array=True,
                can_be_found_without_question=True,
            ),
        ),
        'order_id': feature_module.Feature(
            status=feature_module.Status.IN_PROGRESS,
            value=None,
            spec=feature_module.FeatureSpec(
                key='order_id',
                entity='number',
                entity_extract_order=0,
                type_='int',
                is_array=False,
            ),
        ),
    }
    state = state_module.State(feature_layers=[state_features])
    state_copy = state_module.State(feature_layers=[state_features])

    tracker.update_state_by_entities(state, entities)
    assert len(state.get_features()) == len(state_copy.get_features())
    assert state.get_features()['order_id'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value=None,
        spec=feature_module.FeatureSpec(
            key='order_id',
            entity='number',
            entity_extract_order=0,
            type_='int',
            is_array=False,
            can_be_found_without_question=False,
        ),
    )
    assert state.get_features()['order_ids'] == feature_module.Feature(
        status=feature_module.Status.DEFINED,
        value=[123, 456],
        spec=feature_module.FeatureSpec(
            key='order_ids',
            entity='numbers',
            type_='int',
            is_array=True,
            can_be_found_without_question=True,
        ),
    )


# TODO: ksenilis add other test for tracker,
# at 23.08.2021 states are loaded from agent
@pytest.mark.skip
@pytest.mark.pgsql('supportai', files=['sample.sql'])
async def test_db_state(web_context):
    dst = tracker_module.DialogStateTracker(namespace='justschool_dialog')

    features_one = await dst.load_bot_state(chat_id='1', context=web_context)

    features_two = await dst.load_bot_state(chat_id='2', context=web_context)

    assert features_one == [
        feature_module.Feature.as_defined('feature_1', '1'),
        feature_module.Feature.as_defined('feature_2', 2),
    ]

    assert features_two == [
        feature_module.Feature.as_defined('feature_3', '3'),
        feature_module.Feature.as_defined('feature_4', 4),
    ]

    # await tracker_module.save_state( # noqa pylint: disable=E1120
    #     chat_id='1',
    #     namespace='justschool_dialog',
    #     context=web_context,
    #     states=[],
    #     tracker=tracker_module.DialogStateTracker(),
    # )

    features_one = await dst.load_bot_state(chat_id='1', context=web_context)

    features_two = await dst.load_bot_state(chat_id='2', context=web_context)

    # await tracker_module.save_state(
    #     chat_id='2',   # noqa pylint: disable=E1120
    #     namespace='justschool_dialog',
    #     context=web_context,
    #     states=[],
    #     tracker=tracker_module.DialogStateTracker(),
    # )

    assert features_one == [
        feature_module.Feature.as_defined('feature_1', 'abc'),
    ]

    assert features_two == [
        feature_module.Feature.as_defined('feature_2', 'def'),
    ]


@pytest.mark.config(
    SUPPORTAI_DST_SETTINGS={
        'default_state_ttl_sec': 3600,
        'max_feature_layer_count': 2,
    },
)
async def test_dst_max_layers_count(web_context):
    dst = tracker_module.DialogStateTracker(namespace='test_dialog')

    state_feature_layers = [
        {
            'feature1': feature_module.Feature(
                status=feature_module.Status.DEFINED,
                value=1,
                spec=feature_module.FeatureSpec(
                    key='feature1', type_='int', is_array=False,
                ),
            ),
            'feature2': feature_module.Feature(
                status=feature_module.Status.DEFINED,
                value=2,
                spec=feature_module.FeatureSpec(
                    key='feature2', type_='int', is_array=False,
                ),
            ),
        },
        {
            'feature2': feature_module.Feature(
                status=feature_module.Status.DEFINED,
                value=3,
                spec=feature_module.FeatureSpec(
                    key='feature2', type_='int', is_array=False,
                ),
            ),
        },
        {
            'feature2': feature_module.Feature(
                status=feature_module.Status.DEFINED,
                value=4,
                spec=feature_module.FeatureSpec(
                    key='feature2', type_='int', is_array=False,
                ),
            ),
            'feature3': feature_module.Feature(
                status=feature_module.Status.DEFINED,
                value='some_str',
                spec=feature_module.FeatureSpec(
                    key='feature3', type_='str', is_array=False,
                ),
            ),
        },
    ]

    state = state_module.State(feature_layers=state_feature_layers)

    await dst.save_state(chat_id='1', context=web_context, state=state)

    assert len(state.get_feature_layers()) == 2

    assert state.get_features()['feature1'].value == 1
    assert state.get_features()['feature2'].value == 2
    assert state.get_features()['feature3'].value == 'some_str'

    assert state.get_feature_layers()[1]['feature2'].value == 3
