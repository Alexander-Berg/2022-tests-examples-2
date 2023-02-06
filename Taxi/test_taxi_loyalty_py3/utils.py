def select_account(pgsql, unique_driver_id, yt_dryrun=False, dms_dryrun=False):
    cursor = pgsql['loyalty'].cursor()
    accounts_table_name = 'loyalty.loyalty_accounts'
    if yt_dryrun:
        accounts_table_name = 'loyalty.yt_loyalty_accounts'
    if dms_dryrun:
        accounts_table_name = 'loyalty.dms_loyalty_accounts'

    cursor.execute(
        'SELECT status, next_recount '
        f'FROM {accounts_table_name} '
        f'WHERE unique_driver_id=\'{unique_driver_id}\'',
    )
    result = [row for row in cursor]
    cursor.close()
    return result


def select_logs(pgsql, unique_driver_id, yt_dryrun=False, dms_dryrun=False):
    cursor = pgsql['loyalty'].cursor()
    accounts_table_name = 'loyalty.status_logs'
    if yt_dryrun:
        accounts_table_name = 'loyalty.yt_status_logs'
    if dms_dryrun:
        accounts_table_name = 'loyalty.dms_status_logs'
    cursor.execute(
        'SELECT status, reason, points '
        f'FROM {accounts_table_name} '
        f'WHERE unique_driver_id=\'{unique_driver_id}\'',
    )
    result = [row for row in cursor]
    cursor.close()
    return result
