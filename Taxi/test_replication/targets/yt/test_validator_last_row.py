from replication.foundation import map_doc_classes as classes
from replication.targets.yt.rows_validators import last_row


async def test_last_row_validator(replication_ctx, yt_clients_storage):
    rows = [
        classes.MapDocInfo(0, {'pk': 0, 'v': 123}, '0'),
        classes.MapDocInfo(1, {'pk': 1, 'v': 123}, '1'),
        classes.MapDocInfo(2, {'pk': 2, 'v': 123}, '2'),
        classes.MapDocInfo(3, {'pk': 3, 'v': 123}, '3'),
    ]
    with yt_clients_storage(
            default_clients_data={
                'hahn': {
                    '//abc/table': {
                        '1': {'pk': 1, 'v': 123},
                        '2': {'pk': 2, 'v': 123},
                    },
                    '//abc/table/@sorted_by': ['pk'],
                },
            },
    ):
        async_yt_client = replication_ctx.shared_deps.yt_wrapper.get_client(
            'hahn',
        )
        result = await last_row.validate(async_yt_client, '//abc/table', rows)
        assert result == classes.ValidationResult(
            good_rows=[
                classes.MapDocInfo(
                    raw_doc_index=3,
                    mapped_doc={'pk': 3, 'v': 123},
                    doc_id='3',
                ),
            ],
            bad_rows=[
                classes.BadDocInfo(
                    doc=classes.MapDocInfo(
                        raw_doc_index=0,
                        mapped_doc={'pk': 0, 'v': 123},
                        doc_id='0',
                    ),
                    errors=[
                        {
                            'message': (
                                'actual doc key=0 less than last doc key=2 and'
                                ' not found in //abc/table'
                            ),
                            'details': {
                                'current_key': 0,
                                'table_last_key': 2,
                                'table_path': '//abc/table',
                            },
                        },
                    ],
                ),
            ],
            skip_rows=[
                classes.MapDocInfo(
                    raw_doc_index=1,
                    mapped_doc={'pk': 1, 'v': 123},
                    doc_id='1',
                ),
                classes.MapDocInfo(
                    raw_doc_index=2,
                    mapped_doc={'pk': 2, 'v': 123},
                    doc_id='2',
                ),
            ],
        )
