# # pylint: disable=import-only-modules
# import datetime
#
# import pytest
#
# from tests_crm_policy.utils import select_columns_from_table
#
#
# async def send_one(taxi_crm_policy):
#     response = await taxi_crm_policy.get(
#         '/v1/check_update_send_message',
#         params={
#             'entity_id': 'testKeyID3',
#             'entity_type': 'user_id',
#             'channel_type': 'fullscreen',
#             'campaign_id': '1',
#         },
#     )
#     return response
#
#
# @pytest.mark.pgsql(
#     'crm_policy', files=['create_1_channel_1_communication.sql'],
# )
# async def test_communication_cleaned(taxi_crm_policy, pgsql, mocked_time):
#     response = await send_one(taxi_crm_policy)
#     assert response.json() == {'allowed': True}
#
#     mocked_time.set(datetime.datetime(2019, 2, 1, 0, 0))
#     await taxi_crm_policy.post(
#         'service/cron', json={'task_name': 'crm-policy-drop-tables'},
#     )
#     rows = select_columns_from_table(
#         'crm_policy.registered_external_communications',
#         ['id'],
#         pgsql['crm_policy'],
#     )
#     assert rows == [{'id': 1}]
#
#     mocked_time.set(datetime.datetime(2020, 10, 13, 14, 0))
#     await taxi_crm_policy.post(
#         'service/cron', json={'task_name': 'crm-policy-drop-tables'},
#     )
#     # Old communication moved to registered_external_communications_archive
#     rows = select_columns_from_table(
#         'crm_policy.registered_external_communications',
#         ['id'],
#         pgsql['crm_policy'],
#     )
#     assert rows == []
#
#     rows = select_columns_from_table(
#         'crm_policy.registered_external_communications_archive',
#         ['id'],
#         pgsql['crm_policy'],
#     )
#     assert rows == [{'id': 1}]
#
#     # old values from external_communications_groups also archived
#     rows = select_columns_from_table(
#         'crm_policy.external_communications_groups',
#         ['external_communication_id'],
#         pgsql['crm_policy'],
#     )
#     assert rows == []
#
#     rows = select_columns_from_table(
#         'crm_policy.external_communications_groups_archive',
#         ['external_communication_id'],
#         pgsql['crm_policy'],
#     )
#     assert rows == [{'external_communication_id': 1}]
