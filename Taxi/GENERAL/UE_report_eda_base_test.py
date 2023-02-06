#!/usr/bin/env python
# coding: utf-8

from business_models.databases import greenplum
from business_models.botolib import Bot
from business_models.config_holder import ConfigHolder
from business_models.util.log import Handler

cfg = ConfigHolder()
bot_token = cfg.igorrubanov_tbot
default_chat_id = 279902711
bot = Bot(token=bot_token, default_chat_id=default_chat_id)

with Handler(bot_report=bot, job_name='ufo/ue_report_data/UE_report_eda_base_test.py',
             raise_exceptions=True, notify_success=True):

    df_dates = greenplum("""
    select (date_trunc('month', max(day_mnth)) - interval '2 month')::date as msc_date_from,
            (date_trunc('month', max(day_mnth)) + interval '2 month')::date as msc_date_to
    from snb_taxi.ellenl_ue_report_eda_base_final_v4
    """)

    msc_date_from = df_dates['msc_date_from'][0]
    msc_date_to = df_dates['msc_date_to'][0]
    print("msc_date_from: " + str(msc_date_from), "msc_date_to: " + str(msc_date_to))

    bot.send_message(message="[UE test] Start", chat=default_chat_id)
    # with open('ellenl_ue_report_eda_base_step1_vitrina.sql') as f:
    #     sql1 = f.read()
    # greenplum(sql1.format(msc_date_from=str(msc_date_from),
    #                       msc_date_to=str(msc_date_to)))
    # print('Table snb_taxi.ellenl_ue_report_eda_base_step1_vitrina was updated successfully')
    # # print(sql1.format(msc_date_from=str(msc_date_from),
    # #                        msc_date_to=str(msc_date_to)))
    #
    # with open('ellenl_ue_report_eda_base_step2_cpo.sql') as t:
    #     sql2 = t.read()
    # greenplum(sql2.format(msc_date_from=str(msc_date_from),
    #                       msc_date_to=str(msc_date_to)))
    # print('Table snb_taxi.ellenl_ue_report_eda_base_step2_cpo was updated successfully')

    with open('ellenl_ue_report_eda_base_step3_costs_final_test.sql') as m:
        sql3 = m.read()
    greenplum(sql3.format(msc_date_from=str(msc_date_from),
                          msc_date_to=str(msc_date_to)))
    print('Table snb_eda.krechin_max_ue_report_eda_final_test_2022_03_30 was updated successfully')

    #bot.send_message(message="[UE] End", chat=default_chat_id)
