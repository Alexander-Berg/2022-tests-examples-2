import pytest


@pytest.mark.yt(
    schemas=['yt_static_snapshot_schema1.yaml'],
    static_table_data=['yt_static_snapshot_content1.yaml'],
)
@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.config(
    UAFS_PASSPORT_UID_GLUE_REPLICATOR_TAXI_SETTINGS_V1={
        'enabled': True,
        'yt_snapshot_table_path': '//snapshot',
        'yt_batch_size': 5000,
        'mongo_batch_size': 3,
        'mongo_batch_sleep_duration': 0,
        'max_glued_puids_per_record': 4,
        'max_records': 100,
    },
)
async def test_base(taxi_uantifraud, testpoint, mongodb, yt_apply):
    glue_db = mongodb.antifraud_mdb_passport_uid_taxi_offline_glue
    replication_state_db = mongodb.antifraud_mdb_yt_replication_state

    batches = []
    expected_batch_count = 3

    @testpoint('passport-uid-glue-replicator-taxi-finished')
    def handle_finished_tp(_):
        pass

    @testpoint('passport-uid-glue-replicator-taxi-process-batch')
    def process_batch_tp(batch):
        batches.append(batch)

    async with taxi_uantifraud.spawn_task('passport-uid-glue-replicator-taxi'):
        for _ in range(expected_batch_count):
            await process_batch_tp.wait_call()
        await handle_finished_tp.wait_call()

    assert len(batches) == expected_batch_count

    assert batches == [
        [
            {'puid': '1516716547', 'glued_puids': ['1050477654', '18636304']},
            {
                'puid': '1516848080',
                'glued_puids': [
                    '1481253534',
                    '1491965917',
                    '1516849318',
                    '275110728',
                ],
            },
            {
                'puid': '1516806303',
                'glued_puids': [
                    '1505127216',
                    '1513054468',
                    '1513774985',
                    '1521746168',
                ],
            },
        ],
        [
            {
                'puid': '1517197767',
                'glued_puids': [
                    '1028099737',
                    '1324749788',
                    '1519324550',
                    '1520450608',
                ],
            },
            {
                'puid': '1016832256',
                'glued_puids': [
                    '1057950969',
                    '1130000021662975',
                    '14196153',
                    '909018291',
                ],
            },
            {'puid': '1', 'glued_puids': ['2', '3', '4']},
        ],
        [{'puid': '5', 'glued_puids': ['6', '7', '8', '9']}],
    ]

    assert (
        sorted(
            glue_db.find({}, ['_id', 'glued_puids']), key=lambda e: e['_id'],
        )
        == [
            {'_id': '1', 'glued_puids': ['2', '3', '4']},
            {
                '_id': '1016832256',
                'glued_puids': [
                    '1057950969',
                    '1130000021662975',
                    '14196153',
                    '909018291',
                ],
            },
            {'_id': '1516716547', 'glued_puids': ['1050477654', '18636304']},
            {
                '_id': '1516806303',
                'glued_puids': [
                    '1505127216',
                    '1513054468',
                    '1513774985',
                    '1521746168',
                ],
            },
            {
                '_id': '1516848080',
                'glued_puids': [
                    '1481253534',
                    '1491965917',
                    '1516849318',
                    '275110728',
                ],
            },
            {
                '_id': '1517197767',
                'glued_puids': [
                    '1028099737',
                    '1324749788',
                    '1519324550',
                    '1520450608',
                ],
            },
            {'_id': '5', 'glued_puids': ['6', '7', '8', '9']},
        ]
    )

    replication_states = list(replication_state_db.find())
    assert len(replication_states) == 1

    replication_state = replication_states[0]

    assert (
        replication_state['replicator'] == 'passport-uid-glue-replicator-taxi'
    )
    assert replication_state['cursor_pos'] == 7
    assert replication_state['status'] == 'complete'
