# coding: utf-8

# import pytest

# from business_models.util.log import Timer
# from cron.forecast.make_forecast import run, graph
# from .common import folder_subsampling, reset_to_defaults
# from business_models.botolib import bot

# TODO: вернуть в строй после реанимации прогнозов
# @pytest.mark.cron
# @folder_subsampling
# def make_forecasts_tests(new_base=None, write=True, validate=False, skip_ticket=True, select_nodes=None,
#                          disable_bot=True, week_only=False, write_models=False, dashboard_path=None):
#     """Тест функции make_forecast из cron/forecast
#     :param new_base: str - путь, по которому лежат файлы для теста (в случае их наличия)
#     :param write: bool - если True, записывает данные на YT
#     :param validate: bool - проверяем ли мы результаты прогнозов
#     :param skip_ticket: bool - если  true, то тикет по  результатам валидации
#         создаваться не будет
#     :param disable_bot: bool - если True, то бот не будет слать письма в чат
#     """
#     if disable_bot:
#         bot.disable()
#     graph.logs_path = 'tests_' + graph.main_config['logs_path']  # чтобы не перетирать продакшен лог
#     with Timer("Run forecast in directory {}".format(new_base), raise_exceptions=True,
#                finally_call=reset_to_defaults):
#         status = run(validate=validate, with_write=write, skip_ticket=skip_ticket, write_models=write_models,
#                      select_nodes=select_nodes, week_only=week_only, dashboard_path=dashboard_path)
#     assert status
