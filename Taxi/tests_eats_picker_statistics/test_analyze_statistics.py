import pytest

from . import utils


@pytest.mark.now('2021-04-23T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='config3_eats_picker_statistics_comments_settings.json',
)
@pytest.mark.experiments3(
    filename='config3_eats_picker_statistics_statistics_params.json',
)
@pytest.mark.pgsql('eats_picker_statistics', files=['fill_data.sql'])
@pytest.mark.parametrize(
    ['picker_id', 'interval', 'datetime', 'expected_response'],
    [
        # Day
        (
            '1',
            'day',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.11,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 110.13,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\n'
                    'Ваш показатель довозимости составляет 1.11, '
                    'что соответствует таргету 1.\n'
                    'Вы в среднем собираете один товар за 1.84 '
                    'минут, что соответствует целевому времени сборки '
                    'по таймеру 2.\nВы быстро и качественно '
                    'собираете, так держать!'
                ),
            },
        ),
        (
            '2',
            'day',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.2,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 130.2,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\n'
                    'Ваш показатель довозимости составляет 1.2, '
                    'что соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 2.17 минут, '
                    'что не соответствует целевому времени сборки '
                    'по таймеру 2.\nCоветуем вам следить '
                    'за таймером, чтобы больше зарабатывать.'
                ),
            },
        ),
        (
            '3',
            'day',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 0.93,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 110.3,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\n'
                    'Ваш показатель довозимости составляет 0.93, '
                    'что не соответствует таргету 1.\n'
                    'Вы в среднем собираете один товар за 1.84 '
                    'минут, что соответствует целевому времени сборки '
                    'по таймеру 2.\nCоветуем вам не '
                    'пренебрегать заменами - посмотрите обучение '
                    'по ссылке.\nС хорошими показателями довозимости '
                    'вы сможете больше зарабатывать.'
                ),
            },
        ),
        (
            '4',
            'day',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 0.94,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 130.4,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 0.94, что не '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 2.17 минут, что не '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nCоветуем вам посмотреть обучение по '
                    'ссылке.\nЕсли вы будете пренебрегать показателями '
                    'качества и скорости сборки - вы потеряете доступ '
                    'к сервису.'
                ),
            },
        ),
        # Week
        (
            '5',
            'week',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.5,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 110.5,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 1.5, что '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 1.84 минут, что '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nВы быстро и качественно собираете, '
                    'так держать!'
                ),
            },
        ),
        (
            '6',
            'week',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.6,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 130.6,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 1.6, что '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 2.18 минут, что не '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nCоветуем вам следить за таймером, '
                    'чтобы больше зарабатывать.'
                ),
            },
        ),
        (
            '7',
            'week',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 0.97,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 110.7,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 0.97, что не '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 1.84 минут, что '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nCоветуем вам не пренебрегать заменами '
                    '- посмотрите обучение по ссылке.\nС хорошими '
                    'показателями довозимости вы сможете больше '
                    'зарабатывать.'
                ),
            },
        ),
        (
            '8',
            'week',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 0.98,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 130.8,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 0.98, что не '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 2.18 минут, что не '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nCоветуем вам посмотреть обучение по '
                    'ссылке.\nЕсли вы будете пренебрегать показателями '
                    'качества и скорости сборки - вы потеряете доступ '
                    'к сервису.'
                ),
            },
        ),
        # Additional comments
        (
            'fake_picker_id',
            'day',
            '2021-04-23T00:00:01+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
        (
            'fake_picker_id',
            'week',
            '2021-04-23T00:00:01+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
        (
            '9',
            'day',
            '2021-04-22T00:00:01+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.9,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 120.9,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Вы собрали менее 10 SKU, поэтому мало '
                    'информации для расчета показателей, вы '
                    'увидите статистику в недельном разрезе.\n'
                    'Ваши показатели за 2021-04-22\nВаш показатель '
                    'довозимости составляет 1.9, что '
                    'соответствует таргету 1.\nВы в '
                    'среднем собираете один товар за 2.02 '
                    'минут, что не соответствует целевому времени '
                    'сборки по таймеру 2.\nCоветуем вам '
                    'следить за таймером, чтобы больше '
                    'зарабатывать.'
                ),
            },
        ),
        (
            '10',
            'day',
            '2021-04-23T00:00:01+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 10 SKU, поэтому мало '
                    'информации для расчета показателей, '
                    'обратитесь к статистике на следующей '
                    'неделе.\n'
                ),
            },
        ),
        (
            '10',
            'week',
            '2021-04-23T00:00:01+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 10 SKU, поэтому мало '
                    'информации для расчета показателей, '
                    'обратитесь к статистике на следующей '
                    'неделе.\n'
                ),
            },
        ),
        # A certain date
        (
            '1',
            'day',
            '2021-04-23T00:00:01+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
        (
            '1',
            'day',
            '2021-04-25T00:00:00+03:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
        (
            '1',
            'day',
            '2021-04-24T00:00:02+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.7,
                        'target': 1.0,
                        'date': '2021-04-25T00:00:01+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 122.83,
                        'target': 120.0,
                        'date': '2021-04-25T00:00:01+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-24\n'
                    'Ваш показатель довозимости составляет 1.7, '
                    'что соответствует таргету 1.\n'
                    'Вы в среднем собираете один товар за 2.05 '
                    'минут, что не соответствует целевому времени сборки '
                    'по таймеру 2.\nCоветуем вам следить за таймером, '
                    'чтобы больше зарабатывать.'
                ),
            },
        ),
        (
            '5',
            'week',
            '2021-04-20T00:00:00+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 1.6,
                        'target': 1.0,
                        'date': '2021-04-21T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 115.5,
                        'target': 120.0,
                        'date': '2021-04-21T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-20\nВаш показатель '
                    'довозимости составляет 1.6, что '
                    'соответствует таргету 1.\nВы в среднем '
                    'собираете один товар за 1.93 минут, что '
                    'соответствует целевому времени сборки по таймеру '
                    '2.\nВы быстро и качественно собираете, '
                    'так держать!'
                ),
            },
        ),
        # Month
        (
            '11',
            'month',
            '2021-04-22T00:00:00+03:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 123.45,
                        'target': 1.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 111.11,
                        'target': 120.0,
                        'date': '2021-04-23T00:00:00+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-22\n'
                    'Ваш показатель довозимости составляет 123.45, '
                    'что соответствует таргету 1.\n'
                    'Вы в среднем собираете один товар за 1.85 '
                    'минут, что соответствует целевому времени сборки '
                    'по таймеру 2.\nВы быстро и качественно '
                    'собираете, так держать!'
                ),
            },
        ),
        (
            '12',
            'month',
            '2021-04-01T00:00:00+05:00',
            {
                'metrics': [
                    {
                        'name': 'delivery_rate',
                        'value': 22.2,
                        'target': 1.0,
                        'date': '2021-04-02T00:00:01+00:00',
                    },
                    {
                        'name': 'picking_duration_per_item',
                        'value': 222.2,
                        'target': 120.0,
                        'date': '2021-04-02T00:00:01+00:00',
                    },
                ],
                'comment': (
                    'Ваши показатели за 2021-04-01\n'
                    'Ваш показатель довозимости составляет 22.2, '
                    'что соответствует таргету 1.\n'
                    'Вы в среднем собираете один товар за 3.7 '
                    'минут, что не соответствует целевому времени сборки '
                    'по таймеру 2.\nCоветуем вам следить за таймером, '
                    'чтобы больше зарабатывать.'
                ),
            },
        ),
        (
            '12',
            'month',
            '2021-04-02T15:00:00+05:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
        # timezone
        (
            '13',
            'day',
            '2021-06-01T01:00:00+05:00',
            {
                'metrics': [],
                'comment': (
                    'Вы собрали менее 1 SKU, поэтому мало информации '
                    'для расчета показателей, обратитесь к статистике '
                    'на следующей неделе.\n'
                ),
            },
        ),
    ],
)
async def test_statistics_handle(
        taxi_eats_picker_statistics,
        picker_id,
        interval,
        datetime,
        expected_response,
):
    response = await taxi_eats_picker_statistics.post(
        '/4.0/eats-picker-statistics/api/v1/analyze-statistics',
        json={
            'picker_id': picker_id,
            'interval': interval,
            'datetime': datetime,
        },
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response
