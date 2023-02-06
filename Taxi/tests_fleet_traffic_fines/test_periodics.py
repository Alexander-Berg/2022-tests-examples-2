import decimal

import dateutil
import pytest


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_periodic_fine_retrieve(
        taxi_fleet_traffic_fines, pg_dump, mock_api,
):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_task('periodic-fine-retrieve')

    assert (
        mock_api['fines-1c']['/Fines/v1/Load'].next_call()['request'].json
        == {
            'LastRenewalDate': '1970-01-01T00:00:00+00:00',
            'Limit': 3000,
            'LoadPhotos': False,
            'Offset': 0,
        }
    )
    assert pg_dump() == {
        **pg_initial,
        'fines': {
            **pg_initial['fines'],
            'FINE_UIN_01': (
                'CARNUMBER01',
                'CARSTS01',
                None,
                None,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                'paid',
                0,
                {
                    'BIK': '010407105',
                    'INN': '2466050868',
                    'KBK': '18811601121010001140',
                    'KPP': '246601001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ КРАСНОЯРСК БАНКА РОССИИ//'
                        'УФК по Красноярскому краю г. Красноярск'
                    ),
                    'Name': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                        '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)'
                    ),
                    'OKTMO': '04701000',
                    'CorrAccount': '40102810245370000011',
                    'PaymentName': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                    ),
                    'AccountNumber': '03100643000000011900',
                },
                'УФК по Красноярскому краю '
                '(ГУ МВД России по Красноярскому краю)'
                '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'А Д ОБХОД Г. КРАСНОЯРСКА',
                'ПРЕВЫШЕНИЕ УСТАНОВЛЕННОЙ СКОРОСТИ ДВИЖЕНИЯ ТРАНСПОРТНОГО '
                'СРЕДСТВА НА ВЕЛИЧИНУ БОЛЕЕ 20, НО НЕ БОЛЕЕ 40 КМ/Ч',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('250.0000'),
            ),
            'FINE_UIN_02': (
                'CARNUMBER02',
                'CARSTS02',
                None,
                None,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                'issued',
                1,
                {
                    'BIK': '019205400',
                    'INN': '1654002946',
                    'KBK': '18811601121010001140',
                    'KPP': '165945001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ-НБ РЕСПУБЛИКА ТАТАРСТАН г. Казань//'
                        'УФК по Республике Татарстан г. Казань'
                    ),
                    'Name': 'ЦАФАП ГИБДД МВД по Республике Татарстан',
                    'OKTMO': '92701000',
                    'CorrAccount': '40102810445370000079',
                    'PaymentName': (
                        'УФК по Республике Татарстан '
                        '(УГИБДД МВД по Республике Татарстан)'
                    ),
                    'AccountNumber': '03100643000000011100',
                },
                'ЦАФАП ГИБДД МВД по Республике Татарстан',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                decimal.Decimal('2000.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'РЕСПУБЛИКА ТАТАРСТАН, АВТОДОРОГА СОРОЧЬИ ГОРЫ-ШАЛИ, 18КМ.',
                '12.9ч.6- повторное совершение административного '
                'правонарушения, предусмотренного частью 3 настоящей статьи',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('2000.0000'),
                decimal.Decimal('1000.0000'),
            ),
            'FINE_UIN_03': (
                None,
                None,
                '1234567890_PD',
                None,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                'issued',
                0,
                {
                    'BIK': '010407105',
                    'INN': '2466050868',
                    'KBK': '18811601121010001140',
                    'KPP': '246601001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ КРАСНОЯРСК БАНКА РОССИИ//'
                        'УФК по Красноярскому краю г. Красноярск'
                    ),
                    'Name': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                        '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)'
                    ),
                    'OKTMO': '04701000',
                    'CorrAccount': '40102810245370000011',
                    'PaymentName': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                    ),
                    'AccountNumber': '03100643000000011900',
                },
                'УФК по Красноярскому краю '
                '(ГУ МВД России по Красноярскому краю)'
                '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'А Д ОБХОД Г. КРАСНОЯРСКА',
                'ПРЕВЫШЕНИЕ УСТАНОВЛЕННОЙ СКОРОСТИ ДВИЖЕНИЯ ТРАНСПОРТНОГО '
                'СРЕДСТВА НА ВЕЛИЧИНУ БОЛЕЕ 20, НО НЕ БОЛЕЕ 40 КМ/Ч',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('250.0000'),
            ),
            'FINE_UIN_04': (
                None,
                None,
                '0123456789_PD',
                '123123_PD',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                'issued',
                0,
                {
                    'BIK': '010407105',
                    'INN': '2466050868',
                    'KBK': '18811601121010001140',
                    'KPP': '246601001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ КРАСНОЯРСК БАНКА РОССИИ//'
                        'УФК по Красноярскому краю г. Красноярск'
                    ),
                    'Name': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                        '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)'
                    ),
                    'OKTMO': '04701000',
                    'CorrAccount': '40102810245370000011',
                    'PaymentName': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                    ),
                    'AccountNumber': '03100643000000011900',
                },
                'УФК по Красноярскому краю '
                '(ГУ МВД России по Красноярскому краю)'
                '(ЦАФАП ОДД ГИБДД ГУ МВД России по Красноярскому краю)',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'А Д ОБХОД Г. КРАСНОЯРСКА',
                'ПРЕВЫШЕНИЕ УСТАНОВЛЕННОЙ СКОРОСТИ ДВИЖЕНИЯ ТРАНСПОРТНОГО '
                'СРЕДСТВА НА ВЕЛИЧИНУ БОЛЕЕ 20, НО НЕ БОЛЕЕ 40 КМ/Ч',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('250.0000'),
            ),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_01', 'CAR_ID_01', 'PARK-ID-01'): (
                'paid',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-02'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_03', None, 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_03', None, 'PARK-ID-04'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_04', None, 'PARK-ID-05'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
        },
        'task_completions': {
            **pg_initial['task_completions'],
            (
                'periodic-fine-retrieve',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
            ): (4,),
        },
    }


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_TRAFFIC_FINES_PERIODIC_CAR_SYNC={
        'is_enabled': True,
        'period_seconds': 3600,
        'launch_window': {
            'not_earlier_than': '11:30',
            'not_later_than': '12:30',
        },
        'latest_ride_range_hours': 2160,
        'select_cars_by_latest_ride': True,
        'select_cars_by_park_id': ['PARK_01', 'PARK_02'],
    },
)
@pytest.mark.yt(static_table_data=['yt_fines.yaml'])
async def test_periodic_car_sync_yt(
        taxi_fleet_traffic_fines, pg_dump, yt_apply, mock_api, load,
):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_task('periodic-car-sync-yt')

    yql_query = load('yql_query.sql')

    assert mock_api['yql']['/api/v2/operations'].next_call()[
        'request'
    ].json == {'action': 'SAVE', 'content': yql_query, 'type': 'SQLv1'}

    assert pg_dump() == {
        **pg_initial,
        'park_cars': {
            **pg_initial['park_cars'],
            ('CAR_ID_01', 'PARK-ID-01', 'CARNUMBER01', 'CARSTS01'): (
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                False,
            ),
            ('CAR_ID_11', 'PARK-ID-01', 'CARNUMBER11', 'CARSTS11'): (
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                True,
            ),
            ('CAR_ID_02', 'PARK-ID-01', 'CARNUMBER04', 'CARSTS04'): (
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                True,
            ),
            ('CAR_ID_02', 'PARK-ID-01', 'CARNUMBER02', 'CARSTS02'): (
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                False,
            ),
            ('CAR_ID_02', 'PARK-ID-02', 'CARNUMBER02', 'CARSTS02'): (
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                False,
            ),
        },
        'cars': {
            **pg_initial['cars'],
            ('CARNUMBER01', 'CARSTS01'): ('removing',),
            ('CARNUMBER11', 'CARSTS11'): ('adding',),
            ('CARNUMBER02', 'CARSTS02'): ('removing',),
            ('CARNUMBER04', 'CARSTS04'): ('adding',),
        },
    }


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_TRAFFIC_FINES_PERIODIC_CAR_SYNC={
        'is_enabled': True,
        'period_seconds': 3600,
        'launch_window': {
            'not_earlier_than': '18:00',
            'not_later_than': '19:00',
        },
        'latest_ride_range_hours': 2160,
    },
)
async def test_periodic_car_sync_yt_skip(
        taxi_fleet_traffic_fines, pg_dump, mock_api,
):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_task('periodic-car-sync-yt')

    assert not mock_api['yql']['/api/v2/operations'].has_calls

    assert pg_dump() == pg_initial


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_periodic_car_sync_external(
        taxi_fleet_traffic_fines, pg_dump, mock_api,
):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_task('periodic-car-sync-external')

    assert pg_dump() == {
        **pg_initial,
        'cars': {
            **pg_initial['cars'],
            ('CARNUMBER02', 'CARSTS02'): ('active',),
            ('CARNUMBER03', 'CARSTS03'): ('inactive',),
        },
    }
    assert mock_api['fines-1c']['/Car/v1/Add'].next_call()['request'].json == [
        {'Number': 'CARNUMBER02', 'STSSeries': 'CARS', 'STSNumber': 'TS02'},
    ]
    assert (
        mock_api['fines-1c']['/Car/v1/ChangeActivity']
        .next_call()['request']
        .json
        == [
            {
                'Number': 'CARNUMBER03',
                'STSSeries': 'CARS',
                'STSNumber': 'TS03',
                'Activity': False,
            },
        ]
    )


@pytest.mark.pgsql(
    'fleet_traffic_fines', files=['add_fines.sql', 'add_park_fines.sql'],
)
@pytest.mark.now('2022-03-11T12:00:00.000000+00:00')
@pytest.mark.config(
    FLEET_TRAFFIC_FINES_PERIODIC_FINE_UPDATE={
        'is_enabled': True,
        'period_seconds': 600,
    },
)
async def test_periodic_update_fines(taxi_fleet_traffic_fines, pg_dump):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_periodic_task('periodic_fine_update')

    assert pg_dump() == {
        **pg_initial,
        'fines': {
            **pg_initial['fines'],
            'FINE_UIN_01': (
                'CARNUMBER01',
                'CARSTS01',
                None,
                None,
                dateutil.parser.parse('2022-03-11T12:00:00+03:00'),
                'overdue',
                0,
                {
                    'BIK': '010407105',
                    'INN': '2466050868',
                    'KBK': '18811601121010001140',
                    'KPP': '246601001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ КРАСНОЯРСК БАНКА РОССИИ//УФК '
                        'по Красноярскому краю г. Красноярск'
                    ),
                    'Name': 'ЦАФАП ГИБДД МВД по Республике Татарстан',
                    'OKTMO': '04701000',
                    'CorrAccount': '40102810245370000011',
                    'PaymentName': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                    ),
                    'AccountNumber': '03100643000000011900',
                },
                'ЦАФАП ГИБДД МВД по Республике Татарстан',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                None,
                dateutil.parser.parse('2022-02-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-03-11T00:00:00+00:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'А Д ОБХОД Г. КРАСНОЯРСКА',
                'ПРЕВЫШЕНИЕ УСТАНОВЛЕННОЙ СКОРОСТИ ДВИЖЕНИЯ ТРАНСПОРТНОГО '
                'СРЕДСТВА НА ВЕЛИЧИНУ БОЛЕЕ 20, НО НЕ БОЛЕЕ 40 КМ/Ч',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
            ),
            'FINE_UIN_02': (
                'CARNUMBER02',
                'CARSTS02',
                None,
                None,
                dateutil.parser.parse('2022-03-11T12:00:00+03:00'),
                'issued',
                0,
                {
                    'BIK': '010407105',
                    'INN': '2466050868',
                    'KBK': '18811601121010001140',
                    'KPP': '246601001',
                    'Bank': (
                        'ОТДЕЛЕНИЕ КРАСНОЯРСК БАНКА РОССИИ//УФК '
                        'по Красноярскому краю г. Красноярск'
                    ),
                    'Name': 'ЦАФАП ГИБДД МВД по Республике Татарстан',
                    'OKTMO': '04701000',
                    'CorrAccount': '40102810245370000011',
                    'PaymentName': (
                        'УФК по Красноярскому краю '
                        '(ГУ МВД России по Красноярскому краю)'
                    ),
                    'AccountNumber': '03100643000000011900',
                },
                'ЦАФАП ГИБДД МВД по Республике Татарстан',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                None,
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-03-12T00:00:00+00:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('0.0000'),
                'Возбуждено ИП',
                'А Д ОБХОД Г. КРАСНОЯРСКА',
                'ПРЕВЫШЕНИЕ УСТАНОВЛЕННОЙ СКОРОСТИ ДВИЖЕНИЯ ТРАНСПОРТНОГО '
                'СРЕДСТВА НА ВЕЛИЧИНУ БОЛЕЕ 20, НО НЕ БОЛЕЕ 40 КМ/Ч',
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                decimal.Decimal('500.0000'),
                decimal.Decimal('250.0000'),
            ),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_01', 'CAR_ID_01', 'PARK-ID-01'): (
                'overdue',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-03-11T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                None,
            ),
            ('FINE_UIN_01', 'CAR_ID_01', 'PARK-ID-02'): (
                'overdue',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-03-11T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                None,
            ),
        },
    }


@pytest.mark.pgsql(
    'fleet_traffic_fines', files=['add_fines.sql', 'add_park_fines.sql'],
)
@pytest.mark.now('2022-07-01T12:00:00.000000+03:00')
@pytest.mark.yt(static_table_data=['yt_fines.yaml'])
async def test_periodic_contractor_assignment(
        taxi_fleet_traffic_fines, pg_dump, mock_api,
):
    pg_initial = pg_dump()

    await taxi_fleet_traffic_fines.run_task('periodic-contractor-assignment')

    assert pg_dump() == {
        **pg_initial,
        'task_completions': {
            **pg_initial['task_completions'],
            (
                'periodic-contractor-assignment',
                dateutil.parser.parse('2022-07-01T12:00:00.000000+03:00'),
            ): (4,),
        },
        'contractors': {
            **pg_initial['contractors'],
            ('FINE_UIN_01', 'PARK-ID-01', 'CONTRACTOR-ID-03'): (1.0,),
            ('FINE_UIN_02', 'PARK-ID-01', 'CONTRACTOR-ID-02'): (1.0,),
            ('FINE_UIN_03', None, None): (None,),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_01', 'CAR_ID_01', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                'CONTRACTOR-ID-03',
            ),
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                False,
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                'CONTRACTOR-ID-02',
            ),
        },
    }
