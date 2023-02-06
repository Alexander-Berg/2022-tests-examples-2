# coding: utf-8


from business_models.graph import Configuration, Configurator
from business_models import Handler, data_from_file
from business_models.botolib import bot
# from cron.forecast.errors_logging import create_ticket
from .common import get_filename
import os

import pytest


def get_configurator(config_path='validate_graph_config.json'):
    main_config_path = get_filename(config_path, __file__)
    path = os.path.dirname(main_config_path)
    return Configurator(main_config_path=main_config_path, paths_prefix=path)


def include_exclude_conf_tests():
    configurations = [Configuration(scale='week', type='forecast'),
                      Configuration(scale='week', to_scale='month', type='forecast', converter='scaling'),
                      Configuration(scale='month', type='forecast'),
                      Configuration(scale='week', type='forecast', converter='base_regions'),
                      Configuration(scale='month', type='forecast', converter='base_regions'),
                      Configuration(scale='week', to_scale='month', type='forecast', converter='base_regions')
                      ]

    filter_conf = Configuration(to_scale="month")

    excluded = [conf.check_contains(filter_conf, include=False) for conf in configurations]
    assert excluded == [True, False, False, True, False, False]

    included = [conf.check_contains(filter_conf, include=True) for conf in configurations]
    assert included == [False, True, True, False, True, True]

    filter_conf = [{"to_scale": "month"}, {"converter": "base_regions"}]

    all_excluded = [conf.check_contains(filter_conf, include=False, is_any=False) for conf in configurations]
    assert all_excluded == [True, False, False, False, False, False]

    all_included = [conf.check_contains(filter_conf, include=True, is_any=False) for conf in configurations]
    assert all_included == [False, False, False, False, True, True]

    any_excluded = [conf.check_contains(filter_conf, include=False, is_any=True) for conf in configurations]
    assert any_excluded == [True, True, True, True, False, False]

    any_included = [conf.check_contains(filter_conf, include=True, is_any=True) for conf in configurations]
    assert any_included == [False, True, True, True, True, True]

    any_month_config = [{"to_scale": "month"}, {"scale": "month"}]

    all_excluded = [conf.check_contains(any_month_config, include=False, is_any=False) for conf in configurations]
    assert all_excluded == [True, False, False, True, False, False]

    all_included = [conf.check_contains(any_month_config, include=True, is_any=False) for conf in configurations]
    assert all_included == [False, False, True, False, True, False]

    any_excluded = [conf.check_contains(any_month_config, include=False, is_any=True) for conf in configurations]
    assert any_excluded == [True, True, False, True, False, True]

    any_included = [conf.check_contains(any_month_config, include=True, is_any=True) for conf in configurations]
    assert any_included == [False, True, True, False, True, True]


def config_import_tests():
    graph = get_configurator('graph_config.json')
    surge_model = graph.get_forecact_model('surge')
    # Проверяем, что это действительно кастомная forecast model
    assert surge_model.name == 'surge'

# не запускаем пока не работают прогнозы
# @pytest.mark.parametrize(
#     "validation_configs",
#     [None,
#      "../../../cron/forecast/configs/Validate"  # конфиги из продакшена
#      ]
# )
# def create_ticket_tests(validation_configs, skip_ticket_creation=True):
#     """Читает ods.am_fact и ods.am_forecast и запускает на них валидацию и создание тикетов
#
#     :param validation_configs: str - путь к конфигам для валидации, если не передан, то
#         прочитаются конфиги из тестовой среды
#     """
#     bot.disable()
#     with Handler(finally_call=bot.enable):
#         graph = get_configurator('validate_graph_config.json')
#         graph.run(only_read=True)
#
#         if validation_configs is not None:
#             graph.main_config['validation_configs'] = validation_configs
#         graph.validate()
#         create_ticket(graph.validate_output, skip_ticket_creation=skip_ticket_creation)


def validate_failing_test():
    """Проверяем, что если валидация должна упасть, то она упадет"""
    bot.disable()
    with Handler(finally_call=bot.enable):
        graph = get_configurator('validate_graph_config.json')
        graph.run(only_read=True)

        for table_name in ['trips', 'demand', 'supply']:
            table = graph.data_manager.get(table_name, with_metadata=True)
            table.data[table_name] /= 2

        assert not graph.validate()
    return graph


def change_logs_paths_test():
    graph = get_configurator('validate_graph_config.json')
    new_logs_path = 'test_' + graph.main_config['logs_path']
    dm_path = graph.data_manager.logs_path
    new_dm_path = dm_path.replace(graph.main_config['logs_path'], new_logs_path)
    graph.logs_path = new_logs_path
    assert graph.data_manager.logs_path == new_dm_path


def graph_logger_test():
    graph = get_configurator('validate_graph_config.json')
    golden_error_text = 'TEST OF LOGGING'
    graph.graph_logger.error(golden_error_text)
    error_text = data_from_file(graph.graph_logger_file, determine_type=True, read_unknown=True)
    assert golden_error_text in error_text
    # TODO: при удалении файла get_logger не обновляет объект логгирования и лог перестает писаться
    open(graph.graph_logger_file, 'w').close()


def data_manager_logger_test():
    graph = get_configurator('validate_graph_config.json')
    golden_error_text = 'TEST OF LOGGING'
    dm = graph.data_manager
    dm._logger.error(golden_error_text)
    error_text = data_from_file(dm.logfile, determine_type=True, read_unknown=True)
    assert golden_error_text in error_text
    # TODO: при удалении файла get_logger не обновляет объект логгирования и лог перестает писаться
    open(dm.logfile, 'w').close()
