select service_order_id,
service_id,
date_trunc('day', utc_transaction_dttm  + interval '3 hours')::date as day_mnth,
client_id,
paysys_type_cc,
transaction_type,
payment_type,
product,
currency_code,
sum(payment_value) as value
from eda_stg_bigfood.billing_export_payment_buffer
where utc_transaction_dttm + interval '3 hours' >= date_trunc('month', current_date - interval '1 month')
  and utc_transaction_dttm + interval '3 hours' < date_trunc('month', current_date)
  and (service_order_id like '%testtestmasha%' or service_order_id like '%TESTTESTMASHA%')
--  and service_order_id not in (select distinct service_order_id from eda_stg_bigfood.billing_export_commission_buffer)
group by 1,2,3,4,5,6,7,8,9
order by 1,2;