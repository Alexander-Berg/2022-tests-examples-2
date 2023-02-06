import bson
import pytest

from chatterbox import stq_task


@pytest.mark.config(
    NUMBER_OF_DAYS_FOR_INDIVIDUAL_MACROS={'macro_id_1': 0, 'macro_id_2': 1},
)
@pytest.mark.parametrize(
    'task_id, macro_ids,expected_entities',
    [
        (
            bson.ObjectId('4c717aae5d7d437fbdeea852'),
            ['macro_id_0', 'macro_id_1', 'macro_id_2'],
            [
                {
                    'entity_id': 'some_user_phone_id',
                    'entity_type': 'user_phone_id',
                    'tag': 'macro_used_macro_id_0',
                    'ttl': 1209600,
                },
                {
                    'entity_id': 'some_user_phone_id',
                    'entity_type': 'user_phone_id',
                    'tag': 'macro_used_macro_id_2',
                    'ttl': 86400,
                },
            ],
        ),
    ],
)
async def test_send_macros_to_support_tags(
        cbox,
        task_id,
        macro_ids,
        expected_entities,
        mock_support_tags_save_tags,
):
    mock_support_tags_save_tags(expected_entities)
    await stq_task.send_macros_to_support_tags(cbox.app, task_id, macro_ids)
