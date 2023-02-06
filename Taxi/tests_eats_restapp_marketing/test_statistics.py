import datetime

import pytest

from . import sql


@pytest.mark.suspend_periodic_tasks('periodic-campaign-statistics-fetch')
@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_campaigns.sql'])
async def test_metrics(
        taxi_eats_restapp_marketing, taxi_eats_restapp_marketing_monitor,
):
    await taxi_eats_restapp_marketing.run_periodic_task(
        'periodic-campaign-statistics-fetch',
    )

    metrics_name = 'campaign-metrics'
    metrics = (
        await taxi_eats_restapp_marketing_monitor.get_metrics(metrics_name)
    )[metrics_name]

    assert metrics == {
        'active_count': 5,
        'inactive_count': {'for_30_days': 5},
        'error_count': {'for_24_hours': 4},
        'active_without_banner_count': 3,
        'all_campaigns_count': 6,
        'success_campaigns_count': 3,
        'on_moderation_campaigns_count': 2,
        'not_created_campaigns_count': 1,
        'count_passport_id': 5,
        'place_without_banner': {'for_30_days': 4},
        'campaign_without_banner': {'for_30_days': 2},
        'ad_without_banner': {'for_30_days': 3},
        'content_without_banner': {'for_30_days': 1},
        'content_without_banner_more_2_days': 2,
        'all_campaigns_without_banner_more_2_days': 3,
        'advert_for_create_false_more_1_day_count': 3,
        'advert_keywords_count': 10,
        'advert_keywords_count_status_draft': 2,
        'advert_keywords_count_status_accepted': 3,
        'advert_keywords_count_status_rejected': 4,
        'advert_keywords_count_status_unknown': 1,
        'advert_keywords_count_state_on': 3,
        'advert_keywords_count_state_off': 5,
        'advert_keywords_count_state_suspended': 2,
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_DAILY_STATISTICS_SETTINGS={'period-ms': 120},
)
async def test_daily_statistics(
        taxi_eats_restapp_marketing, eats_restapp_marketing_db, statistics,
):
    """
    EDACAT-2983: проверяет что в сервис статистики
    оправляются рекламодатели за сутки
    """

    today_date = datetime.date.today().strftime('%Y-%m-%d')
    yersterday_date = (
        datetime.date.today() - datetime.timedelta(days=1)
    ).strftime('%Y-%m-%d')
    yersterday_client = sql.AdvertClient(
        id=1,
        client_id=1,
        passport_id='1',
        created_at=f'{yersterday_date}T13:41:21.145013+0000',
    )
    today_client_1 = sql.AdvertClient(
        id=2,
        client_id=2,
        passport_id='2',
        created_at=f'{today_date}T00:50:21.145013+0000',
    )
    today_client_2 = sql.AdvertClient(
        id=3,
        client_id=3,
        passport_id='3',
        created_at=f'{today_date}T09:40:21.145013+0000',
    )

    sql.insert_advert_client(
        database=eats_restapp_marketing_db, advert_client=yersterday_client,
    )
    sql.insert_advert_client(
        database=eats_restapp_marketing_db, advert_client=today_client_1,
    )
    sql.insert_advert_client(
        database=eats_restapp_marketing_db, advert_client=today_client_2,
    )

    async with statistics.capture(taxi_eats_restapp_marketing) as capture:
        await taxi_eats_restapp_marketing.run_periodic_task(
            'periodic-daily-statistics-collector',
        )

    metric_name = 'new-advertizers'
    inserted = sql.get_advert_clients(eats_restapp_marketing_db)
    assert len(inserted) == 3

    assert metric_name in capture.statistics, capture.statistics.keys()
    assert capture.statistics[metric_name] == 2
