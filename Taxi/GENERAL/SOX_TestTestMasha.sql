select
    service_order_id,
    utc_transaction_dttm,
    client_id,
    currency_code,
    coalesce(sum(commission_value),0) as commission_sum,
    coalesce(sum(promocode_value),0) as promocode_sum,
    type,
    sum(total_commission_value) as total_sum,
    service_id
from eda_stg_bigfood.billing_export_commission_buffer
where
    utc_transaction_dttm + interval '3 hours' >= date_trunc('month', current_date - interval '1 month')
    and utc_transaction_dttm + interval '3 hours' < date_trunc('month', current_date)
    and (service_order_id like '%%testtestmasha%%'or service_order_id like '%%TESTTESTMASHA%%')
group by service_order_id, utc_transaction_dttm, client_id, currency_code, type, service_id
order by client_id, utc_transaction_dttm;