import pytest


@pytest.mark.yt(
    schemas=['yt_static_snapshot_schema1.yaml'],
    static_table_data=['yt_static_snapshot_content1.yaml'],
)
@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.config(
    UAFS_PASSPORT_UID_GLUE_REPLICATOR_EATS_SETTINGS_V1={
        'enabled': True,
        'yt_snapshot_table_path': '//snapshot',
        'yt_batch_size': 5000,
        'mongo_batch_size': 2,
        'mongo_batch_sleep_duration': 0,
        'max_glued_puids_per_record': 10,
        'max_records': 100,
    },
)
async def test_base(taxi_uantifraud, testpoint, mongodb, yt_apply):
    glue_db = mongodb.antifraud_mdb_passport_uid_eats_grocery_offline_glue
    replication_state_db = mongodb.antifraud_mdb_yt_replication_state

    batches = []
    expected_batch_count = 3

    @testpoint('passport-uid-glue-replicator-eats-grocery-finished')
    def handle_finished_tp(_):
        pass

    @testpoint('passport-uid-glue-replicator-eats-grocery-process-batch')
    def process_batch_tp(batch):
        batches.append(batch)

    async with taxi_uantifraud.spawn_task(
            'passport-uid-glue-replicator-eats-grocery',
    ):
        for _ in range(expected_batch_count):
            await process_batch_tp.wait_call()
        await handle_finished_tp.wait_call()

    assert len(batches) == expected_batch_count

    assert batches == [
        [
            {'glued_puids': ['1050477654', '18636304'], 'puid': '1516716547'},
            {
                'glued_puids': [
                    '1439232705',
                    '1481253534',
                    '1491965917',
                    '1516849318',
                    '275110728',
                    '656511239',
                ],
                'puid': '1516848080',
            },
        ],
        [
            {
                'glued_puids': [
                    '1505127216',
                    '1512712358',
                    '1513054468',
                    '1513774985',
                    '1515889737',
                    '1516355524',
                    '1521746168',
                    '1522444869',
                    '1523025151',
                    '1523376864',
                ],
                'puid': '1516806303',
            },
            {
                'glued_puids': [
                    '1028099737',
                    '1324749788',
                    '1519324550',
                    '1520450608',
                    '1526809826',
                    '653918564',
                    '94004317',
                ],
                'puid': '1517197767',
            },
        ],
        [
            {
                'glued_puids': [
                    '1057950969',
                    '1066340576',
                    '1130000021662975',
                    '1130000021869812',
                    '14196153',
                    '1482787344',
                    '294591270',
                    '345861206',
                    '841340131',
                    '909018291',
                ],
                'puid': '1016832256',
            },
        ],
    ]

    assert (
        sorted(
            glue_db.find({}, ['_id', 'glued_puids']), key=lambda e: e['_id'],
        )
        == [
            {
                '_id': '1016832256',
                'glued_puids': [
                    '1057950969',
                    '1066340576',
                    '1130000021662975',
                    '1130000021869812',
                    '14196153',
                    '1482787344',
                    '294591270',
                    '345861206',
                    '841340131',
                    '909018291',
                ],
            },
            {'_id': '1516716547', 'glued_puids': ['1050477654', '18636304']},
            {
                '_id': '1516806303',
                'glued_puids': [
                    '1505127216',
                    '1512712358',
                    '1513054468',
                    '1513774985',
                    '1515889737',
                    '1516355524',
                    '1521746168',
                    '1522444869',
                    '1523025151',
                    '1523376864',
                ],
            },
            {
                '_id': '1516848080',
                'glued_puids': [
                    '1439232705',
                    '1481253534',
                    '1491965917',
                    '1516849318',
                    '275110728',
                    '656511239',
                ],
            },
            {
                '_id': '1517197767',
                'glued_puids': [
                    '1028099737',
                    '1324749788',
                    '1519324550',
                    '1520450608',
                    '1526809826',
                    '653918564',
                    '94004317',
                ],
            },
        ]
    )

    replication_states = list(replication_state_db.find())
    assert len(replication_states) == 1

    replication_state = replication_states[0]

    assert (
        replication_state['replicator']
        == 'passport-uid-glue-replicator-eats-grocery'
    )
    assert replication_state['cursor_pos'] == 5
    assert replication_state['status'] == 'complete'
