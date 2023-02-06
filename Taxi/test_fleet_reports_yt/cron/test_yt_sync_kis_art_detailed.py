import datetime

import pytest

from fleet_reports_yt.generated.cron import run_cron

DB_FINAL_RESULT = [
    {
        'driver_profile_id': 'dr_id1',
        'kis_art_id': 'e2c3bc79165c4068a1c319fe772800c2',
        'kis_art_status': 'permanent',
        'park_id': 'pid1',
        'report_date': datetime.date(2021, 8, 3),
        'driver_full_name': 'Фамилия Имя Отчество',
    },
    {
        'driver_profile_id': 'dr_id2',
        'kis_art_id': '01b3d57f4ef742449dfdf93c21adc72c',
        'kis_art_status': 'without_id',
        'park_id': 'pid2',
        'report_date': datetime.date(2021, 8, 3),
        'driver_full_name': 'Фамилия1 Имя1 Отчество1',
    },
    {
        'driver_profile_id': 'dr_id3',
        'kis_art_id': 'a3b7063ec19a4842ab80daae93de2e2d',
        'kis_art_status': 'requested',
        'park_id': 'pid3',
        'report_date': datetime.date(2021, 8, 3),
        'driver_full_name': 'Фамилия2 Имя2 Отчество2',
    },
    {
        'driver_profile_id': 'dr_id2',
        'kis_art_id': '7427b661e08e44e996233f82fba53a54',
        'kis_art_status': 'without_id',
        'park_id': 'pid2',
        'report_date': datetime.date(2021, 8, 4),
        'driver_full_name': 'Николаев Николай Николаевич',
    },
    {
        'driver_profile_id': 'dr_id3',
        'kis_art_id': '9e159226dc2b446cad22e8b80ad46608',
        'kis_art_status': 'permanent',
        'park_id': 'pid3',
        'report_date': datetime.date(2021, 8, 4),
        'driver_full_name': 'Тест2 Екатерина2 Екатериновна2',
    },
    {
        'driver_profile_id': 'dr_id4',
        'kis_art_id': 'b3c998c726d741e1b285fe8a6f3902b0',
        'kis_art_status': 'permanent',
        'park_id': 'pid4',
        'report_date': datetime.date(2021, 8, 4),
        'driver_full_name': 'Иванов Иван Иванович',
    },
    {
        'driver_profile_id': 'dr_id90',
        'kis_art_id': '',
        'kis_art_status': 'without_id',
        'park_id': 'pid8',
        'report_date': datetime.date(2021, 8, 4),
        'driver_full_name': 'неважно',
    },
    {
        'driver_profile_id': 'dr_id99',
        'kis_art_id': 'old_id',
        'kis_art_status': 'without_id',
        'park_id': 'pid8',
        'report_date': datetime.date(2021, 8, 4),
        'driver_full_name': 'Трофимова Анна Юрьевна',
    },
]


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.pgsql('fleet_reports')
async def test_run_cron(yt_apply, cron_context):
    # Second run should not change DB or fail
    for _ in range(2):
        await run_cron.main(
            ['fleet_reports_yt.crontasks.yt_sync_kis_art_detailed', '-t', '0'],
        )
        rows = await cron_context.pg.main_master.fetch(
            """SELECT * FROM yt.kis_art_detailed_report
             ORDER BY report_date ASC, park_id ASC, driver_profile_id ASC;""",
        )
        parsed = [dict(x) for x in rows]
        for row in parsed:
            del row['id']
        assert DB_FINAL_RESULT == parsed
