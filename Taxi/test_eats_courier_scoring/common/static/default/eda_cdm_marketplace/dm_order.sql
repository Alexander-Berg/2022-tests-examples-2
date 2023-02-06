CREATE SCHEMA IF NOT EXISTS eda_cdm_marketplace;

DROP TABLE IF EXISTS eda_cdm_marketplace.dm_order;

CREATE TABLE IF NOT EXISTS eda_cdm_marketplace.dm_order
(
    account_correction_lcy                    numeric,
    acquiring_commission_value_lcy            numeric,
    additional_delivery_cost_lcy              integer,
    additional_delivery_time_factor_mnt       integer,
    adopted_lat                               numeric,
    adopted_lon                               numeric,
    adoption_dur_sec                          integer,
    application_platform                      varchar,
    arrived_to_customer_lat                   numeric,
    arrived_to_customer_lon                   numeric,
    assignment_dur_sec                        integer,
    brand_id                                  integer,
    brand_name                                varchar,
    brand_store_flg                           boolean,
    business_model                            varchar,
    cancelled_lat                             numeric,
    cancelled_lon                             numeric,
    commission_value_w_vat_lcy                numeric,
    confirmed_flg                             boolean,
    cooking_type                              varchar,
    country_id                                integer,
    country_name                              varchar,
    courier_assigned_lat                      numeric,
    courier_assigned_lon                      numeric,
    courier_balance_id                        integer,
    courier_delay_sec                         bigint,
    courier_id                                integer,
    courier_selfemploeyed_flg                 boolean,
    courier_service_id                        integer,
    courier_service_income_offer_id           integer,
    courier_service_name                      varchar,
    courier_type                              varchar,
    courier_username                          varchar,
    cte_dur_sec                               integer,
    currency_code                             varchar,
    currency_rate                             numeric,
    delivery_cost_w_vat_lcy                   numeric,
    delivery_fee_w_vat_lcy                    numeric,
    distance_to_customer                      numeric,
    distance_to_customer_precise_flg          boolean,
    distance_to_place                         numeric,
    distance_to_place_precise_flg             boolean,
    drop_off_dur_sec                          integer,
    fact_delivery_payment_lcy                 numeric,
    fact_goods_payment_lcy                    numeric,
    fact_place_commission_value_lcy           numeric,
    fast_food_place_flg                       boolean,
    flow_type                                 varchar,
    high_level_type                           varchar,
    in_place_dur_sec                          integer,
    incentive_refunds_lcy                     numeric,
    incentive_rejected_order_lcy              numeric,
    local_approved_dttm                       timestamp,
    local_created_dttm                        timestamp,
    local_delivered_dttm                      timestamp,
    local_place_confirmed_dttm                timestamp,
    moved_to_delivery_lat                     numeric,
    moved_to_delivery_lon                     numeric,
    msk_accepted_dttm                         timestamp,
    msk_adopted_by_courier_dttm               timestamp,
    msk_approved_dttm                         timestamp,
    msk_arrival_to_customer_fact_dttm         timestamp,
    msk_arrival_to_customer_plan_dttm         timestamp,
    msk_arrival_to_place_fact_dttm            timestamp,
    msk_arrival_to_place_plan_dttm            timestamp,
    msk_cancelled_dttm                        timestamp,
    msk_courier_assigned_dttm                 timestamp,
    msk_created_dttm                          timestamp,
    msk_delivered_dttm                        timestamp,
    msk_delivery_dttm                         timestamp,
    msk_given_dttm                            timestamp,
    msk_max_customer_arrival_time_dttm        timestamp,
    msk_max_place_arrival_time_dttm           timestamp,
    msk_order_taken_fact_dttm                 timestamp,
    msk_order_taken_plan_dttm                 timestamp,
    msk_place_confirmed_dttm                  timestamp,
    msk_ready_dttm                            timestamp,
    msk_restaurant_received_dttm              timestamp,
    msk_sent_to_restaurant_dttm               timestamp,
    order_asap_flg                            boolean,
    order_billing_status                      varchar,
    order_delivery_type                       varchar,
    order_id                                  integer primary key,
    order_items_cost_lcy                      numeric,
    order_latest_revision_id                  integer,
    order_nr                                  varchar,
    order_place_cost_lcy                      numeric,
    order_reaction_id_1_flg                   boolean,
    order_reaction_id_2_flg                   boolean,
    order_source                              varchar,
    order_status                              integer,
    our_refund_delivery_lcy                   numeric,
    our_refund_goods_lcy                      numeric,
    our_refund_total_lcy                      numeric,
    payment_method_id                         integer,
    payment_not_received_delivery_lcy         numeric,
    payment_not_received_goods_lcy            numeric,
    payment_not_received_total_lcy            numeric,
    payment_service                           varchar,
    payment_total_lcy                         numeric,
    place_acquiring_commission_pcnt           numeric,
    place_address_short                       varchar,
    place_client_id                           integer,
    place_commission_currency_code            varchar,
    place_commission_pcnt                     numeric,
    place_company_tin                         varchar,
    place_discount_value_lcy                  numeric,
    place_fixed_commission_value              numeric,
    place_id                                  integer,
    place_lat                                 numeric,
    place_lon                                 numeric,
    place_name                                varchar,
    place_person_legal_name                   varchar,
    place_subsidy_value_lcy                   numeric,
    place_type                                varchar,
    place_type_alias                          varchar,
    pre_delivery_time                         numeric,
    price_difference_goods_lcy                numeric,
    promocode_code                            varchar,
    promocode_kind                            varchar,
    promocode_type                            varchar,
    promocode_value_lcy                       numeric,
    region_id                                 integer,
    region_name                               varchar,
    region_timezone                           varchar,
    service_subsidy_delivery_lcy              numeric,
    service_subsidy_goods_lcy                 numeric,
    service_subsidy_total_lcy                 numeric,
    shift_id                                  varchar,
    shift_type                                varchar,
    shipping_type                             varchar,
    subsidy_value_lcy                         numeric,
    surge_level                               integer,
    surged_order_flg                          boolean,
    taken_lat                                 numeric,
    taken_lon                                 numeric,
    time_to_delivery                          numeric,
    time_to_delivery_max                      numeric,
    tip_amount_lcy                            numeric,
    to_customer_dur_sec                       integer,
    to_place_dur_sec                          integer,
    user_cost_w_vat_lcy                       numeric,
    user_id                                   integer,
    utc_approved_dttm                         timestamp,
    utc_created_dttm                          timestamp,
    utc_delivered_dttm                        timestamp,
    utc_place_confirmed_dttm                  timestamp,
    cancel_reason_id                          integer,
    cancel_reason_code                        varchar,
    cancel_reason_name                        varchar,
    cancel_reasons_system_flg                 boolean,
    cancel_reason_group_id                    integer,
    cancel_reason_group_name                  varchar,
    cancel_reason_group_code                  varchar,
    batched_with_order_id                     integer,
    first_in_multiorder_flg                   boolean,
    _etl_processed_dttm                       timestamp,
    payment_type                              varchar,
    account_type                              varchar,
    payment_system_name                       varchar,
    feedback_rating_val                       integer,
    msk_report_dttm                           timestamp,
    corp_order_flg                            boolean,
    order_items_cnt                           integer,
    promocode_id                              integer,
    location_lat                              numeric,
    location_lon                              numeric,
    utc_call_center_confirmed_dttm            timestamp,
    place_delivery_zone_id                    integer,
    place_delivery_zone_courier_type_code     varchar,
    place_delivery_zone_name                  varchar,
    place_delivery_zone_type                  varchar,
    taxi_dispatch_reason_code                 varchar,
    taxi_dispatch_cargo_uuid_id               varchar,
    taxi_dispatch_request_source_type         varchar,
    taxi_dispatch_offer_order_w_vat_cost_lcy  numeric,
    taxi_dispatch_final_order_w_vat_cost_lcy  numeric,
    taxi_dispatch_final_order_wo_vat_cost_lcy numeric,
    taxi_dispatch_attempt_cnt                 numeric,
    feedback_comment                          varchar,
    pickup_needed_flg                         boolean,
    courier_delivery_zone_id                  integer,
    courier_delivery_zone_name                varchar,
    order_feedback_id                         integer,
    utc_feedback_filled_dttm                  timestamp,
    user_phone_pd_id                          varchar,
    multiorder_cancel_reason_text             varchar,
    yandex_uid                                varchar,
    yandex_uid_type                           integer,
    msk_call_center_confirmed_dttm            timestamp,
    place_slug                                varchar,
    utc_accepted_dttm                         timestamp,
    local_accepted_dttm                       timestamp,
    utc_adopted_by_courier_dttm               timestamp,
    local_adopted_by_courier_dttm             timestamp,
    utc_arrival_to_customer_fact_dttm         timestamp,
    local_arrival_to_customer_fact_dttm       timestamp,
    utc_arrival_to_customer_plan_dttm         timestamp,
    local_arrival_to_customer_plan_dttm       timestamp,
    utc_arrival_to_place_fact_dttm            timestamp,
    local_arrival_to_place_fact_dttm          timestamp,
    utc_arrival_to_place_plan_dttm            timestamp,
    local_arrival_to_place_plan_dttm          timestamp,
    local_call_center_confirmed_dttm          timestamp,
    utc_cancelled_dttm                        timestamp,
    local_cancelled_dttm                      timestamp,
    utc_courier_assigned_dttm                 timestamp,
    local_courier_assigned_dttm               timestamp,
    utc_delivery_dttm                         timestamp,
    local_delivery_dttm                       timestamp,
    msk_feedback_filled_dttm                  timestamp,
    local_feedback_filled_dttm                timestamp,
    utc_given_dttm                            timestamp,
    local_given_dttm                          timestamp,
    utc_max_customer_arrival_time_dttm        timestamp,
    local_max_customer_arrival_time_dttm      timestamp,
    utc_max_place_arrival_time_dttm           timestamp,
    local_max_place_arrival_time_dttm         timestamp,
    utc_order_taken_fact_dttm                 timestamp,
    local_order_taken_fact_dttm               timestamp,
    utc_order_taken_plan_dttm                 timestamp,
    local_order_taken_plan_dttm               timestamp,
    utc_ready_dttm                            timestamp,
    local_ready_dttm                          timestamp,
    utc_report_dttm                           timestamp,
    local_report_dttm                         timestamp,
    utc_restaurant_received_dttm              timestamp,
    local_restaurant_received_dttm            timestamp,
    utc_sent_to_restaurant_dttm               timestamp,
    local_sent_to_restaurant_dttm             timestamp,
    user_device_id                            varchar,
    cooking_time_mnt                          integer,
    route_time_mnt                            integer,
    time_to_delivery_min                      numeric,
    order_item_composition_id                 integer,
    place_plus_active_flg                     boolean,
    eda_cashback_value_pcnt                   numeric,
    place_cashback_value_pcnt                 numeric,
    brand_business_type                       varchar,
    payment_error_resp_code                   varchar,
    user_has_plus_flg                         boolean,
    delivery_flow_type                        varchar,
    our_refund_mp_delivery_and_pickup_lcy     numeric,
    our_refund_our_delivery_lcy               numeric,
    user_address_city_name                    varchar,
    plus_cashback_added_by_place_lcy          numeric,
    plus_cashback_added_by_service_lcy        numeric,
    plus_cashback_added_total_lcy             numeric,
    plus_cashback_spent_by_user_lcy           numeric,
    brand_type                                varchar,
    service_code                              varchar,
    supply_code                               varchar,
    supply_subclass_code                      varchar,
    rating_excluded_flg                       boolean
);