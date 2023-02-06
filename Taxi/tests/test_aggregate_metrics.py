import datetime as dt

from lagg.aggregate_metrics import (
    get_timestamp_interval_start,
    is_close_to_now,
    is_metric_matching_line,
    parse_timestamp,
    timestamp_to_iso,
    update_metric,
)
from lagg.read_log import parse_log_string


async def test_parse_log_string_success(tap):
    with tap.plan(4, 'Парсинг tskv строки логов (успешные проверки)'):
        tap.eq_ok(parse_log_string('tskv\ta=a\tb=b\ttimestamp=2020-08-04 10:47:53,715\t\n'),
                  {'a': 'a', 'b': 'b', 'timestamp': '2020-08-04 10:47:53,715'},
                  'Парсинг работает')
        tap.eq_ok(parse_log_string('tskv\ta=a=a\ttimestamp=2020-08-04 10:47:53,715'),
                  {'a': 'a=a', 'timestamp': '2020-08-04 10:47:53,715'},
                  'Равно в значении')
        tap.eq_ok(parse_log_string('tskv\ta5=a$$ aa [\'\', \'\']\ttimestamp=2020-08-04 10:47:53,715'),
                  {'a5': 'a$$ aa [\'\', \'\']', 'timestamp': '2020-08-04 10:47:53,715'},
                  'Другие символы')
        tap.eq_ok(parse_log_string('tskv\ta/a:a-a=a/a:a-a.a\ttimestamp=2020-08-04 10:47:53,715'),
                  {'a/a:a-a': 'a/a:a-a.a', 'timestamp': '2020-08-04 10:47:53,715'},
                  'Ещё другие символы')


async def test_parse_log_string_failure(tap):
    with tap.plan(4, 'Парсинг tskv строки логов (неуспешные проверки): должно не упасть и вернуть {}'):
        tap.eq_ok(parse_log_string('a=a\tb=b\ttimestamp=2020-08-04 10:47:53,715'), {}, 'Без tskv в начале строки')
        tap.eq_ok(parse_log_string('tskv\ta\tb=b\ttimestamp=2020-08-04 10:47:53,715'), {}, 'Нет равно между табами')
        tap.eq_ok(parse_log_string('tskv\ta\tb=b'), {}, 'Без timestamp\'а')
        tap.eq_ok(parse_log_string('tskv\ta\tb=b\ttimestamp=2020-08-04 10:47:53.715'), {}, 'Невалидный timestamp')


async def test_parse_timestamp(tap):
    with tap.plan(1, 'Парсинг времени'):
        tap.eq_ok(
            timestamp_to_iso(parse_timestamp('2020-08-05 08:15:53,717')),
            '2020-08-05T05:15:53.717000+00:00',
            'Парсинг таймстемпа'
        )


async def test_timestamp_interval_start(tap):
    with tap.plan(4, 'Получение начала интервала для агрегации'):
        tap.eq_ok(get_timestamp_interval_start(1596615353.717), 1596615353.0,
                  'Интервал в 1 секунду')
        tap.eq_ok(get_timestamp_interval_start(1596615353.717, interval=10), 1596615350.0,
                  'Интервал в 10 секунд')
        tap.eq_ok(get_timestamp_interval_start(1596615353.717, interval=30), 1596615330.0,
                  'Интервал в 30 секунд')
        tap.eq_ok(get_timestamp_interval_start(1596615353.717, interval=60), 1596615300.0,
                  'Интервал в минуту')


async def test_is_close_to_now(tap):
    tap.ok(not is_close_to_now(1596615353.717), 'Проверка timestamp далеко от текущего времени')

    ts = dt.datetime.timestamp(dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=3))
    tap.ok(is_close_to_now(ts), 'Проверка timestamp близко к текущему времени')


async def test_is_metric_matching_line_success(tap):
    with tap.plan(4, 'Подходит ли строчка логов для метрики (успешные проверки)'):
        tap.ok(is_metric_matching_line({'line': '456'}, {'key': 'line'}), 'Подходящая строка')
        tap.ok(is_metric_matching_line({'line': '456', 'level': 'ERROR'},
                                       {'key': 'line', 'condition': {'level': 'ERROR'}}),
               'Подходящая строка с условием')
        tap.ok(is_metric_matching_line({'line': '456', 'level': 'ERROR', 'text': 'text'},
                                       {'key': 'line', 'condition': {'level': 'ERROR', 'text': 'text'}}),
               'Подходящая строка с несколькими условиями')
        tap.ok(is_metric_matching_line({'line': '456', 'level': 'ERROR', 'group': 'group_1'},
                                       {'key': 'line'}),
               'Подходящая строка с дополнительной меткой')


async def test_is_metric_matching_line_failure(tap):
    with tap.plan(4, 'Подходит ли строчка логов для метрики (неуспешные проверки)'):
        tap.ok(not is_metric_matching_line({}, {'key': 'line'}), 'Запись лога не содержит ключ')
        tap.ok(not is_metric_matching_line({'line': 'abc'}, {'key': 'line'}), 'Значение ключа не число')
        tap.ok(not is_metric_matching_line({'line': '456'}, {'key': 'line', 'condition': {'level': 'ERROR'}}),
               'Нет ключа из условия')
        tap.ok(not is_metric_matching_line({'line': '456', 'level': 'INFO'},
                                           {'key': 'line', 'condition': {'level': 'ERROR'}}),
               'Условие не прошло')


async def test_update_metric(tap):
    with tap.plan(2, 'Обновление метрик'):
        current_metrics = {'min_line': {'agg': 'min', 'running_metrics': {'min': 460.0}},
                           'max_line': {'agg': 'max', 'running_metrics': {'max': 460.0}}}
        update_metric(current_metrics, 'min_line', 456, 'min')
        tap.eq_ok(current_metrics,
                  {'min_line': {'agg': 'min', 'running_metrics': {'min': 456}},
                   'max_line': {'agg': 'max', 'running_metrics': {'max': 460.0}}},
                  'Обновление простой метрики')

        current_metrics = {'min_line': {'agg': 'min', 'running_metrics': {'min': 460.0}},
                           'avg_line': {'agg': 'avg', 'running_metrics': {'sum': 100, 'cnt': 3}}}
        update_metric(current_metrics, 'avg_line', 456, 'avg')
        tap.eq_ok(current_metrics,
                  {'min_line': {'agg': 'min', 'running_metrics': {'min': 460}},
                   'avg_line': {'agg': 'avg', 'running_metrics': {'sum': 556, 'cnt': 4}}},
                  'Обновление составной метрики')
