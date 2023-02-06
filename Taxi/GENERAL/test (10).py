from business_models import greenplum, hahn
import pandas as pd
import datetime
from pandas.tseries.offsets import MonthEnd
from business_models.startrek import StartrekWrapper
from business_models.util.dates import shift_date, get_period_list, to_start, diff_scales
from business_models.botolib import Bot
from business_models.config_holder import ConfigHolder
from business_models.util.log import Handler

cfg = ConfigHolder()
bot_token = cfg.igorrubanov_tbot
default_chat_id = 1492384359
bot = Bot(token=bot_token, default_chat_id=default_chat_id)

hahn.change_token('robot_supply_yt_token')

# tickets = 'TAXIANALYTICS-12698', 'TAXIANALYTICS-14749'



with Handler(bot_report=bot, job_name='main',
                 raise_exceptions=True, notify_sucess=False):
    for agent in (['gepard', 0.5], ['altocar', 0.3]):
        config = dict(
            code_name = agent[0],
            share_agent = agent[1],
            #month = str(shift_date(datetime.datetime.now(), -1, 'month'))[0:7],
            month = '2021-03',
            goal_table = '//home/taxi-analytics/artemburnus/agent_trips/' + agent[0] + '_report',
            goal_table_gp = 'snb_taxi.artemburnus_' + agent[0] + '_report'
        )

        # script = open('premain_agent_report_script.yql').read().format(**config)
        #
        # with open('main_agent_report_script.yql') as f:
        #     yql = f.read()
        # for scale in ('Day','Week','Month'):
        #     config.update(
        #         scale = scale,
        #         city_in_select = '',
        #         city_in_groupby = 'city,'
        #     )
        #     script += yql.format(**config)
        #     config.update(
        #         city_in_select = "'Total' as ",
        #         city_in_groupby = ''
        #     )
        #     script += yql.format(**config)
        # h = hahn(script[:-16])

        greenplum("""
            delete from {goal_table_gp}
            where utc_order_dt >= '{month}-01';

        """.format(**config))

        greenplum.replicate(yt_path=config['goal_table'],
                            table_name=config['goal_table_gp'],
                            if_exists='append')
                            # if_exists='replace')

bot.send_message("ufo/Agent_trips/agent_trips_reports.py has ended")