import json

import pytest

from dmp_suite.file_utils import from_same_directory
from dmp_suite.greenplum.table import \
    Boolean, Int, String, Datetime, GPTable, Array, Double, MonthPartitionScale
from dmp_suite.greenplum.task.transformations import SqlTaskSource, period_snapshot, TempTable, GreenplumQuery
from dmp_suite.task.args import use_period_arg, ValueAccessor
from dmp_suite.task.cli import StartEndDate
from dmp_suite.task.execution import run_task
from support_etl.layer.greenplum.cdm.contactcenter.fct_chatterbox_ticket_event.table import (
    FctChatterboxTicketEvent
)
from dmp_suite.greenplum import (
    GPTable, resolve_meta,
)
from test_dmp_suite.greenplum import utils
from .impl import gp_table_to_dict, recreate_and_fill, from_directory

MAX_RADIUS_JOIN_MESSAGE = 2
QUERY_PATH = 'support_etl/layer/greenplum/cdm/contactcenter/fct_chatterbox_ticket_event/query.sql'


def format_data(gp_table):
    actual_data = gp_table_to_dict(gp_table)
    for row in actual_data:
        row['utc_event_dttm'] = row['utc_event_dttm'].strftime("%Y-%m-%d %H:%M:%S.%f")
        row['utc_call_answered_dttm'] = row['utc_call_answered_dttm'].strftime("%Y-%m-%d %H:%M:%S.%f") \
            if row['utc_call_answered_dttm'] is not None else None
        row['utc_call_completed_dttm'] = row['utc_call_completed_dttm'].strftime("%Y-%m-%d %H:%M:%S.%f") \
            if row['utc_call_completed_dttm'] is not None else None
    return actual_data


# pylint: disable=missing-attribute-documentation
class ChatterboxSupportTaxiTicket(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='chatterbox_support_taxi_ticket'))

    chatterbox_ticket_id = String()
    ticket_sector_name = String()
    chat_type = String()
    startrack_ticket_code = String()
    utc_created_dttm = Datetime()
    service_name = String()
    calc_ticket_category_name = String()
    antifraud_tag_list = Array(String)
    country_name = String()
    country_code = String()
    country_iso3_code = String()
    country_label_name = String()
    park_country_name = String()
    performer_park_country_name = String()
    country_id = String()
    corp_client_id = String()
    corp_order_flg = Boolean()
    tariff_class_name = String()
    city_name_ru = String()


# pylint: disable=missing-attribute-documentation
class SupportTrackerTicket(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='support_tracker_ticket'))

    ticket_code = String()
    startrack_ticket_id = String()
    utc_created_dttm = Datetime()


# pylint: disable=missing-attribute-documentation,invalid-attribute-name
class ChatterboxSupportTaxiHistory(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='chatterbox_support_taxi_history'))

    event_id = String()
    chatterbox_ticket_id = String()
    event_seq = Int()
    ticket_sector_name = String()
    staff_login = String()
    promocode_id = String()
    csat_value = Double()
    ask_csat_flg = Boolean()
    added_tag_id_list = Array(inner_data_type=String)
    action_type = String()
    latency_sec = Double()
    ticket_new_sector_name = String()
    hidden_comment = String()
    public_comment = String()
    in_additional_shift_flg = String()
    extra_startrack_ticket_code = String()
    ml_predicted_line = String()
    csat_reason_list = Array(inner_data_type=String)
    coupon_flg = Boolean()
    macro_ml_id = Int()
    event_macro_id_list = Array(inner_data_type=String)
    macro_moder_id = Int()
    theme_name = String()
    utc_event_dttm = Datetime()
    full_added_tag_id_list = Array(inner_data_type=String)
    csat_1_question_value = Int()
    csat_2_question_value = Int()
    csat_3_question_value = Int()
    last_user_message_id = String()


# pylint: disable=missing-attribute-documentation
class SupportTrackerTicketLog(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='support_tracker_ticket_log'))

    ticket_id = String()
    comment_list = Array(inner_data_type=String)
    utc_event_dttm = Datetime()


# pylint: disable=missing-attribute-documentation
class ChatterboxSupportTaxiCall(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='chatterbox_support_taxi_call'))

    call_id = String()
    staff_login = String()
    chatterbox_ticket_id = String()
    hangup_reason_code = String()
    call_direction_name = String()
    record_url_list = Array(inner_data_type=String)
    call_completed_status = String()
    utc_created_dttm = Datetime()
    utc_answered_dttm = Datetime()
    utc_completed_dttm = Datetime()
    incoming_phone_number = String()
    user_phone_number = String()
    driver_phone_number = String()
    sector_name = String()
    park_phone_number = String()
    outgoing_phone_number = String()
    asterisk_flg = Boolean()
    csat_value = Int()


# pylint: disable=missing-attribute-documentation,blacklisted-attribute-name
class ChatterboxSupportTaxiMessage(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='chatterbox_support_taxi_message'))

    message_id = String()
    chatterbox_id = String()
    message_text = String()
    utc_event_dttm = Datetime()
    message_author_type = String()
    csat_1_question_value = Int()
    csat_2_question_value = Int()
    csat_3_question_value = Int()


# pylint: disable=missing-attribute-documentation,invalid-attribute-name
class AsteriskCommutation(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='asterisk_commutation'))

    call_id = String()
    utc_start_queue_dttm = Datetime()
    call_direction = String()
    commutation_end_reason_type = String()
    commutation_id = String()
    agent_id = String()
    commutation_queue_type = String()
    utc_answered_dttm = Datetime()
    utc_completed_dttm = Datetime()
    phone_pd_id = String()
    callcenter_phone_number = String()


# pylint: disable=missing-attribute-documentation
class AsteriskDdsOperator(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='asterisk_dds_operator'))

    operator_id = String()
    staff_login = String()
    utc_valid_from_dttm = Datetime()
    utc_valid_to_dttm = Datetime()

# pylint: disable=missing-attribute-documentation,invalid-attribute-name
class MdbCountry(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='mdb_country'))

    country_code_2 = String()
    country_code_3 = String()
    name_eng = String()
    name_rus = String()


@pytest.mark.slow('gp')
def test_query():
    class TestFctChatteboxTicketEventTable(FctChatterboxTicketEvent):
        __layout__ = utils.TestLayout(name=utils.random_name(prefix='fct_chatterbox_ticket_event'))
        __partition_scale__ = MonthPartitionScale('utc_event_dttm', start='2021-09-01', end='2021-12-01')

    def get_source():

        with open(from_same_directory(__file__, 'data/chatterbox_support_taxi_history_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(ChatterboxSupportTaxiHistory, data)

        with open(from_same_directory(__file__, 'data/chatterbox_support_taxi_call_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(ChatterboxSupportTaxiCall, data)

        with open(from_same_directory(__file__, 'data/chatterbox_support_taxi_message_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(ChatterboxSupportTaxiMessage, data)

        with open(from_same_directory(__file__, 'data/chatterbox_support_taxi_ticket_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(ChatterboxSupportTaxiTicket, data)

        with open(from_same_directory(__file__, 'data/support_tracker_ticket_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(SupportTrackerTicket, data)

        with open(from_same_directory(__file__, 'data/support_tracker_ticket_log_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(SupportTrackerTicketLog, data)

        with open(from_same_directory(__file__, 'data/asterisk_commutation_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(AsteriskCommutation, data)

        with open(from_same_directory(__file__, 'data/asterisk_dds_operator_data.json')) as f:
            data = json.load(f)
        recreate_and_fill(AsteriskDdsOperator, data)

        with open(from_same_directory(__file__, 'data/mdb_country.json')) as f:
            data = json.load(f)
        recreate_and_fill(MdbCountry, data)

        asterisk_dds_operator_query = f"""
            create temporary table dds_operator
            on commit drop
            as (
                select
                    operator_id,
                    staff_login,
                    utc_valid_from_dttm,
                    utc_valid_to_dttm
                from {resolve_meta(AsteriskDdsOperator).table_full_name}
            );
            analyze dds_operator;
        """
        return (
            SqlTaskSource
            .from_file(
                from_directory(__file__, 7, QUERY_PATH)
            ).add_tables(
                chatterbox_support_taxi_call=ChatterboxSupportTaxiCall,
                chatterbox_support_taxi_history=ChatterboxSupportTaxiHistory,
                chatterbox_support_taxi_ticket=ChatterboxSupportTaxiTicket,
                chatterbox_support_taxi_message=ChatterboxSupportTaxiMessage,
                support_tracker_ticket=SupportTrackerTicket,
                support_tracker_ticket_log=SupportTrackerTicketLog,
                ods_asterisk_commutation=AsteriskCommutation,
                mdb_country=MdbCountry
            ).add_params(
                start_dttm=use_period_arg().start,
                end_dttm=use_period_arg().end,
                max_radius_join_message=MAX_RADIUS_JOIN_MESSAGE,
            ).add_pre_sql_statement(
                asterisk_dds_operator_query,
            )
        )

    task = period_snapshot(
        name='test_taxi_cdm_fct_chatterbox_ticket_event',
        source=get_source(),
        target=TestFctChatteboxTicketEventTable,
        period_column_name='utc_event_dttm'
    ).arguments(
        period=StartEndDate(None),
    )

    run_task(task, ['--start_date', '2021-07-01', '--end_date', '2021-12-01'])

    with open(from_same_directory(__file__, 'data/expected_fct_chatterbox_ticket_event_data.json')) as f:
        expected_data = json.load(f)

    actual_data = format_data(
        TestFctChatteboxTicketEventTable
    )

    expected_data = sorted(expected_data, key=lambda d: d.get('event_id'))
    actual_data = sorted(actual_data, key=lambda d: d.get('event_id'))

    assert actual_data == expected_data
