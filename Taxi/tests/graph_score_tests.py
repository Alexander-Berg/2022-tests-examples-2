# # coding: utf-8

# import pytest
# from business_models.botolib import bot
# from business_models.util.log import Timer
# from cron.forecast.make_score import run
# from .common import folder_subsampling, reset_to_defaults


# TODO: вернуть в строй после реанимации прогнозов
# @pytest.mark.cron
# @folder_subsampling
# def make_scoring_tests(new_base=None, tmpdir='data_manager_dumps', memory_limit=500 * 1024,
#                        folds=("2020-03-26", "2020-09-28",), disable_bot=True, select_nodes=None,
#                        exclude_jobs=None, skip=False):
#     """Тест функции make_score из cron/forecast

#     :param tmpdir: str, путь для дампов датаменджера
#     :param memory_limit: int,  ограничение на размер датаменджера
#     :param folds: tuple(str),  список date_to для скоринга
#     :param disable_bot: bool - если True, то бот не будет слать письма в чат
#     """
#     if skip:
#         return
    
#     if disable_bot:
#         bot.disable()
#     init_kwargs = {"data_manager_kwargs": {"local_storage_path": tmpdir, "memory_limit": memory_limit,
#                                            "parallel": True}}

#     score_params = {"specify_folds": folds}

#     with Timer("Run scoring tests in directory {}".format(new_base), raise_exceptions=True,
#                finally_call=reset_to_defaults):
#         status = run(skip_upload=True, init_params=init_kwargs, scoring_params=score_params, select_nodes=select_nodes,
#                      logs_prefix='tests_score_', with_save=False, exclude_jobs=exclude_jobs)
#         assert all(status.values()), "Some statuses are false {}".format(status)
