from discounts_operation_calculations.repositories import suggests


async def test_get_push_segment_stats(web_context, pgsql):
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        'SELECT column_name FROM information_schema.columns '
        'WHERE table_schema = \'discounts_operation_calculations\' '
        'AND table_name = \'suggests\' ',
    )
    all_columns = [x[0] for x in cursor]
    cursor.close()

    def get_used_columns(_web_context):
        suggests_storage = suggests.SuggestsStorage(_web_context)
        result = []
        for stage_with_fields in suggests_storage.stages_with_fields:
            result.extend(list(stage_with_fields.fields_with_default_value))
        return result

    used_columns = get_used_columns(web_context)
    # fields that is not used in suggests
    used_columns.extend(['created_at', 'updated_at', 'id'])
    # Will be used in https://st.yandex-team.ru/ATLASBACK-1530
    used_columns.append('push_segments')

    assert sorted(all_columns) == sorted(used_columns)
