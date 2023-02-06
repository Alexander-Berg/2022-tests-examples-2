import pandas as pd
import os

from business_models.botolib import bot
from business_models.util.dates import get_str_date


FCT_ORDER_METRICS = ['trip_cnt', 'gmv_rub', 'revenue_rub', 'incentives_rub', 'net_inflow_rub',
                     'callcenter_commision_rub']
DM_COMMUTATION_METRICS = ['call_cnt', 'trip_cnt']
ERROR = 1000
MONEY_ERROR = 100000


def compare_with_alternative_source(df, metrics, test_prefix='test_', error=ERROR,
                                    money_error=MONEY_ERROR, caption_text=None):
    """Сравнивает метрики из выгрузки с альтернативными источниками и возвращает информацию о строках, где данные
    разошлись больше, чем на допустимую ошибку.
    :param df: pd.DataFrame — результат запроса с выгрузкой
    :param metrics: list — список метрик для сравнения
    :param test_prefix: str — префикс колонок с тестовыми данными из альтернативного источника
    :param error: int — максимально допустимая погрешность, при которой не логируется ошибка
    :param money_error: int — максимально допустимая погрешность для финансовых метрик, при которой не логируется ошибка
    :caption_text: str — текст ошибки до форматирования значениями ошибки
    :return: list — список строк с ошибками"""
    failed = []
    for metric in metrics:

        possible_error = money_error if 'rub' in metric else error
        diff_col = '{m}_diff'.format(m=metric)
        df[diff_col] = df['{prefix}{m}'.format(prefix=test_prefix, m=metric)] - df[metric]
        bad_rows = df[df[diff_col] > possible_error]
        if len(bad_rows) > 0:
            failed.append(caption_text.format(metric=metric))

    return failed


def sector_economics_test(df, filename='callcenter_economics.xlsx'):
    """Собирает ошибки, полученные в результате сравнений выгрузки с альтернативными источниками и отправляет в бот
    собранные ошибки в выгрузке. Возвращает True, если ошибок нет.
    :param df: pd.DataFrame — результат запроса с выгрузкой
    :param filename: str — название файла для отправки в чат мониторинга
    :return: bool — True, если ошибок нет"""
    df['month'] = get_str_date(df['month'])

    failed_dm_commutations = compare_with_alternative_source(
        df[df['callcenter'] != 'total'],
        metrics=DM_COMMUTATION_METRICS,
        caption_text='Между dm_commutations и ods_commutations+operator_actions значительные расхождения в {metric}.\n '
                     'Подробности в файле.'
    )
    failed_fct_order = compare_with_alternative_source(
        df[df['callcenter'] == 'total'],
        metrics=FCT_ORDER_METRICS,
        test_prefix='test_fct_order_',
        caption_text='Между operator_actions и fct_order значительные расхождения в {metric}.\n '
                     'Подробности в файле в строках, где callcenter = total.'
    )
    failed = failed_dm_commutations + failed_fct_order

    if failed:
        df.to_excel(filename)
        message = 'Sector economics reporting FAILED: {}'.format('\n'.join(failed))
        if bot is not None:
            bot.send_file(file=filename, caption=message)
            os.remove(filename)

    return len(failed) == 0
