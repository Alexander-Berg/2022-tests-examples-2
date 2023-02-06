from connection.mysql import get_connection
from connection.yt import get_yt_client
from dmp_suite.yt import YTMeta, to_yson

from eda_etl.layer.yt.raw.bigfood.billing_export_commission_buffer.table import RawFoodBillingExportCommissionBuffer


def bigfood_content():
    con = get_connection('bigfood')
    cur = con.cursor(dictionary=True)

    query = """
        SELECT transaction_id
        FROM bigfood.billing_export_commission_buffer
        WHERE service_order_id = 'TESTTESTMASHA-28125'
    """
    cur.execute(query)
    return set(list(row['transaction_id'] for row in cur))


whitelist = bigfood_content()
for partition in ('2020-06', '2020-05',):
    target = YTMeta(RawFoodBillingExportCommissionBuffer, partition=partition).target_path()
    raw_data = get_yt_client().read_table(target, raw=False)

    delete_rows_values = []
    for row in raw_data:
        if row['doc'].get('service_order_id') == 'TESTTESTMASHA-28125' and row['transaction_id'] not in whitelist:
            delete_rows_values.append(to_yson({'transaction_id': row['transaction_id']}))

    if delete_rows_values:
        get_yt_client().delete_rows(
            table=target,
            input_stream=delete_rows_values,
            raw=False
        )
