INSERT INTO eda_cdm_quality.fct_executor_fault (
    courier_id
    , order_id
    , order_nr
    , lcl_defect_dttm
    , our_refund_total_lcy
    , incentive_refunds_lcy
    , incentive_rejected_order_lcy
    , executor_profile_id
    , park_taximeter_id
    , defect_type
) VALUES (
    1, 101, '101101-101101', '2020-09-19 08:00:00', 0, 0, 0, 'courier_uuid1', 'courier_dbid1',
    'damaged_order'
);
