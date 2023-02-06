def get_all_entity_mappings_from_db(pgsql):
    cursor = pgsql['eats_data_mappings'].cursor()
    cursor.execute(
        'SELECT primary_entity_type, secondary_entity_type, '
        'tvm_write, tvm_read, takeout_policies '
        'FROM eats_data_mappings.entity_mapping',
    )
    mappings = list(
        {
            'primary_entity_type': x[0],
            'secondary_entity_type': x[1],
            'tvm_write': set(x[2]),
            'tvm_read': set(x[3]),
            'takeout_policies': x[4],
        }
        for x in list(cursor)
    )

    return mappings
