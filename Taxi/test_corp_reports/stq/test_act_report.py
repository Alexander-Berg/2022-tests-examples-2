import typing

import pytest
import xlrd

from corp_reports.stq import corp_generate_orders_report

REST_AMOUNT_FROM_YQL = '-345'
REST_AMOUNT_IN_ACT = '345.00'
PROMO_DRIVE = '100'
PROMO_EATS = '200'
PROMO_TAXI = '300'

DRIVE_ORDER = {
    'account_id': '5010717',
    'act_promo_value': PROMO_DRIVE,
    'act_rest_in_amount_wo_vat': REST_AMOUNT_FROM_YQL,
    'car_model': 'kia_rio_xline',
    'car_number': 'н135ох799',
    'city': 'Москва',
    'client_id': 'e744640569b1467d88f4e2718d1987ac',
    'country': 'rus',
    'created_at': 1613424606.55096,
    'currency': 'RUB',
    'department_id': None,
    'drive_user_id': '8a283dd3-2337-4b21-8a07-fd8b6f9bc85a',
    'user_nickname': '',
    'duration': 35663,
    'finish_point_address': 'Россия, Москва, Партизанская улица, 13к2',
    'finish_point_coordinates': {'lon': 37.40959167, 'lat': 55.73163605},
    'finished_at': 1613424592.0,
    'id': '8786ee8e-77ed8399-2e79418f-f6effe48',
    'personal_phone_id': 'e7ce858fa3224e81bf5d2da610985152',
    'start_point_address': 'Россия, Москва, Магистральный переулок, 7к2',
    'start_point_coordinates': {'lon': 37.52603912, 'lat': 55.77303696},
    'started_at': 1613388929.0,
    'tariff': 'Свой тариф',
    'timezone': 'Europe/Moscow',
    'total_mileage': 93.30078125,
    'total_sum': 2150.0,
    'updated_at': 1613424606.55096,
    'user_id': '3fd5decbe4364762baea7b6dd0848517',
    'yandex_uid': '',
}

EATS_ORDER = {
    'act_promo_value': PROMO_EATS,
    'act_rest_in_amount_wo_vat': REST_AMOUNT_FROM_YQL,
    'client_id': '20b62ad089a540088564cd56a6cd1c49',
    'closed_at': 1610810313.0,
    'country': 'rus',
    'courier_phone_id': None,
    'created_at': 1610801602.0,
    'currency': 'RUB',
    'department_id': None,
    'destination_address': 'Знаменская улица, 15',
    'discount': '0.0000',
    'final_cost': -1903.0,
    'id': '210116-144715',
    'order_calculation': [],
    'restaurant_name': 'McDuck',
    'restaurant_address': [],
    'status': 'delivered',
    'updated_at': 1612363510.542401,
    'user_id': '3fd5decbe4364762baea7b6dd0848517',
    'yandex_uid': '1320838221',
}

TAXI_ORDER = {
    'act_promo_value': PROMO_TAXI,
    'act_rest_in_amount_wo_vat': REST_AMOUNT_FROM_YQL,
    'application': 'corpweb',
    'city': 'Москва',
    'class': 'econom',
    'client_id': '02ecd60194a24d51ada6ecae87ef1ab7',
    'comment': 'adadasdasd',
    'corp_user': {
        'user_id': 'b1dbd758099e4b848e6c5cca2029f5c3',
        'department_id': 'dep_id',
    },
    'cost_center': {'user': 'мой умолчальный центр затрат'},
    'created_by': {'uid': '4043814827'},
    'created_date': 1618239530.172,
    'destination': {
        'extra_data': {'contact_phone_id': '5c0556ec030553e658c2d3b4'},
        'fullname': 'Россия, Москва, Котельническанабережная, 1/15кВ',
        'geopoint': [37.643431809230925, 55.748673618280066],
    },
    'distance': 5013.3107587434,
    'due_date': 1618239720.0,
    'extra_user_phone_id': '5c0556ec030553e658c2d3b4',
    'finished_date': 1618240001.252,
    'id': 'd8fbba6ef5d5cee3a0a01ee6286c9593',
    'interim_destinations': [
        {
            'extra_data': {'contact_phone_id': '5c0556ec030553e658c2d3b4'},
            'fullname': 'Россия, Москва, улица Льва Толстого, 23/7кД',
            'geopoint': [37.58310400259934, 55.73499283003445],
        },
    ],
    'nearest_zone': 'moscow',
    'order_updated': 1618240001.81,
    'performer': {
        'car': 'Audi A6 черный С475ВО750',
        'fullname': 'Брагин Спиридон Федосьевич',
        'park_name': 'ООО Автопарк',
    },
    'requirements': {'childchair_for_child_tariff': [7]},
    'source': {
        'extra_data': {'contact_phone_id': '5c0556ec030553e658c2d3b4'},
        'fullname': 'Россия, Москва, Моховая улица, 11с1',
        'geopoint': [37.61253276137941, 55.75486969466518],
    },
    'start_waiting_time': 1618239587.0,
    'started_date': 1618239676.116,
    'status': 'finished',
    'taxi_status': 'complete',
    'taxi_user_id': '25074f245f85443987c36326f9b74c08',
    'type': 'soon',
    'updated': 1618239676.116,
    'user_to_pay': {'ride': 2940000},
    'waiting': {
        # TODO:
        # crutch for act reports: YQL returns YsonUnicode instead of
        # YsonDouble because of bug in used version of YQL library.
        # Transforming to decimal can be removed after this ticket is done:
        # https://st.yandex-team.ru/CORPDEV-2104
        'waiting_cost': '123.45',
        'waiting_in_depart_time': 0,
        'waiting_in_transit_time': 0,
    },
    'cost_without_vat': 245,
    # 'without_vat_to_pay': {'ride': 2450000},
}


def _check_sheet(sheet, expected_sheet_rows):
    sheet_rows = [list(col.value for col in row) for row in sheet.get_rows()]
    assert sheet_rows == expected_sheet_rows


def _check_drive_sheet(sheet, sheet_name: str, **kwargs):
    assert sheet_name == 'report.report.drive'
    after_header_blanc_columns_qty = 24
    separator_line_columns_qty = 27
    total_string_blanc_columns_qty = 25
    expected_sheet_rows = [
        [
            'report.company',
            '',
            'Yandex.Taxi team',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.period',
            '',
            '2021-02',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.drive_orders_count',
            '',
            1.0,
            *[''] * after_header_blanc_columns_qty,
        ],
        [*[''] * separator_line_columns_qty],
        [
            'report.due_data',
            'report.due_time',
            'report.user_fullname',
            'report.user_email',
            'report.user_phone',
            'report.user_class',
            'report.department',
            'report.old_department',
            'report.department_path',
            'report.order_id',
            'report.drive_user_id',
            'report.user_nickname',
            'report.account_id',
            'report.drive_order_duration',
            'report.drive_order_finished_at',
            'report.drive_order_tariff',
            'report.start_point_coordinates',
            'report.finish_point_coordinates',
            'report.start_point_address',
            'report.finish_point_address',
            'report.city',
            'report.timezone',
            'report.car_model',
            'report.car_number',
            'report.drive_mileage',
            'report.currency',
            'report.cost',
        ],
        [
            '15.02.2021',
            '14:35:29',
            'user_name',
            'user@email.com',
            '+79998882211',
            'первый заказ',
            '',
            '',
            '',
            '8786ee8e-77ed8399-2e79418f-f6effe48',
            '8a283dd3-2337-4b21-8a07-fd8b6f9bc85a',
            '',
            '5010717',
            35663,
            '16.02.2021 00:29:52',
            'Свой тариф',
            '37.52603912, 55.77303696',
            '37.40959167, 55.73163605',
            'Россия, Москва, Магистральный переулок, 7к2',
            'Россия, Москва, Партизанская улица, 13к2',
            'Москва',
            'Europe/Moscow',
            'kia_rio_xline',
            'н135ох799',
            93.30078125,
            'RUB',
            2150,
        ],
        [*[''] * total_string_blanc_columns_qty, 'report.result', 2150],
    ]
    _check_sheet(sheet, expected_sheet_rows)


def _check_eats_sheet(sheet, sheet_name: str, has_external_id: bool, **kwargs):
    def _get_phone_and_external_id_columns():
        return (
            ['report.user_external_id']
            if has_external_id
            else ['report.user_phone']
        )

    def _get_phone_and_external_id_values():
        return ['123456'] if has_external_id else ['+79998882211']

    assert sheet_name == 'report.report.eats'
    after_header_blanc_columns_qty = 14
    separator_line_columns_qty = 17
    total_string_blanc_columns_qty = 15
    expected_sheet_rows = [
        [
            'report.company',
            '',
            'Yandex.Taxi team',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.period',
            '',
            '2021-02',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.eats_orders_count',
            '',
            1.0,
            *[''] * after_header_blanc_columns_qty,
        ],
        [*[''] * separator_line_columns_qty],
        [
            'report.due_data',
            'report.due_time',
            'report.user_fullname',
            'report.user_nickname',
            'report.user_email',
        ]
        + _get_phone_and_external_id_columns()
        + [
            'report.user_class',
            'report.department',
            'report.old_department',
            'report.department_path',
            'report.order_id',
            'report.restaurant_name',
            'report.order_destination',
            'report.eats_order_time',
            'report.eats_order_calculation',
            'report.discount',
            'report.cost',
        ],
        ['16.01.2021', '15:53:22', 'user_name', '', 'user@email.com']
        + _get_phone_and_external_id_values()
        + [
            'первый заказ',
            '',
            '',
            '',
            '210116-144715',
            'McDuck',
            'Знаменская улица, 15',
            '16.01.2021 18:18:33',
            '',
            0,
            -1903,
        ],
        [*[''] * total_string_blanc_columns_qty, 'report.result', -1903],
    ]
    _check_sheet(sheet, expected_sheet_rows)


def _check_taxi_sheet(sheet, sheet_name: str, **kwargs):
    assert sheet_name == 'report.report.taxi'
    after_header_blanc_columns_qty = 34
    separator_line_columns_qty = 37
    total_string_blanc_columns_qty = 35
    expected_sheet_rows = [
        [
            'report.company',
            '',
            'Yandex.Taxi team',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.period',
            '',
            '2021-02',
            *[''] * after_header_blanc_columns_qty,
        ],
        [
            'report.rides_count',
            '',
            1.0,
            *[''] * after_header_blanc_columns_qty,
        ],
        [*[''] * separator_line_columns_qty],
        [
            'report.due_data',
            'report.created_time',
            'report.due_time',
            'report.creator',
            'report.order_method',
            'report.due_weekday',
            'report.user_fullname',
            'report.user_class',
            'report.department',
            'report.old_department',
            'report.department_path',
            'report.user_phone',
            'report.user_email',
            'report.user_nickname',
            'report.extra_user_phone',
            'report.combo_order_phones',
            'report.order_id',
            'report.city',
            'report.source_fullname',
            'report.interim_destinations',
            'report.destination_fullname',
            'report.source',
            'report.interim_points',
            'report.destination',
            'report.start_waiting_fulldate',
            'report.start_fulldate',
            'report.finish_fulldate',
            'report.tariff_class',
            'report.cost_center',
            'report.comment',
            'report.distance',
            'report.ride_cost',
            'report.waiting_cost',
            'report.waiting_in_depart_time',
            'report.waiting_in_transit_time',
            'report.requirements',
            'report.cost',
        ],
        [
            '12.04.2021',
            '20:58:50',
            '21:02:00',
            'some_manager',
            'report.app.corpweb',
            'Weekday.monday',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '+5c0556ec030553e658c2d3b4',
            '',
            'd8fbba6ef5d5cee3a0a01ee6286c9593',
            'moscow',
            'Россия, Москва, Моховая улица, 11с1',
            'Россия, Москва, улица Льва Толстого, 23/7кД',
            'Россия, Москва, Котельническанабережная, 1/15кВ',
            '37.61253276137941, 55.75486969466518',
            '37.58310400259934, 55.73499283003445',
            '37.643431809230925, 55.748673618280066',
            '12.04.2021 20:59:47',
            '12.04.2021 21:01:16',
            '12.04.2021 21:06:41',
            'name.econom',
            'мой умолчальный центр затрат',
            'adadasdasd',
            5013.3107587434,
            245.0,
            123.45,
            0.0,
            0.0,
            'childchair_for_child_tariff',
            245.0,
        ],
        [*[''] * total_string_blanc_columns_qty, 'report.result', 245],
    ]
    _check_sheet(sheet, expected_sheet_rows)


def _check_extra_sheet(
        sheet: typing.Optional[xlrd.sheet.Sheet], sheet_name: str, **kwargs,
):
    assert sheet_name == 'report.report.extra_sheet'
    promo_services = {}
    if kwargs['has_drive']:
        promo_services['drive'] = f'{PROMO_DRIVE}.00'
    if kwargs['has_eats']:
        promo_services['eats'] = f'{PROMO_EATS}.00'
    if kwargs['has_taxi']:
        promo_services['taxi'] = f'{PROMO_TAXI}.00'
    separator_line_columns_qty = 6
    after_header_blanc_columns_qty = 3
    expected_sheet_rows = (
        [
            [
                'report.company',
                '',
                'Yandex.Taxi team',
                *[''] * after_header_blanc_columns_qty,
            ],
            [
                'report.period',
                '',
                '2021-02',
                *[''] * after_header_blanc_columns_qty,
            ],
            [*[''] * separator_line_columns_qty],
            [
                'report.report.extra_reason_title',
                'report.report.extra_service_title',
                'report.report.extra_sum_title',
                *[''] * after_header_blanc_columns_qty,
            ],
            [
                'report.report.extra_rest_title',
                '',
                REST_AMOUNT_IN_ACT,
                *[''] * after_header_blanc_columns_qty,
            ],
        ]
        + [
            [
                'report.report.extra_promo_title',
                f'report.report.{promo_service}',
                promo_sum,
                *[''] * after_header_blanc_columns_qty,
            ]
            for (promo_service, promo_sum) in promo_services.items()
        ]
    )
    _check_sheet(sheet, expected_sheet_rows)


def _check_file_contents(
        file_contents,
        has_drive: bool,
        has_eats: bool,
        has_taxi: bool,
        has_external_id: bool,
):
    book = xlrd.open_workbook(file_contents=file_contents)
    sheets = book.sheets()
    if not any([has_drive, has_eats, has_taxi]):
        assert len(sheets) == 1  # empty sheet
        return
    check_funcs = []
    if has_drive:
        check_funcs.append(_check_drive_sheet)
    if has_eats:
        check_funcs.append(_check_eats_sheet)  # type: ignore
    if has_taxi:
        check_funcs.append(_check_taxi_sheet)
    check_funcs.append(_check_extra_sheet)
    sheet_names = book.sheet_names()
    assert len(sheets) == len(sheet_names) == len(check_funcs)
    for sheet, sheet_name, check_func in zip(sheets, sheet_names, check_funcs):
        check_func(
            sheet,
            sheet_name,
            has_drive=has_drive,
            has_eats=has_eats,
            has_taxi=has_taxi,
            has_external_id=has_external_id,
        )


def make_contracts_response(has_drive: bool, has_eats: bool, has_taxi: bool):
    services = []
    if has_drive:
        services.append('drive')
    if has_eats:
        services.append('eats')
    if has_taxi:
        services.append('taxi')
    return {
        'contracts': [
            {
                'contract_id': 111,
                'services': services,
                'external_id': 'contract_eid',
                'billing_client_id': 'billing_client_id',
                'billing_person_id': 'billing_person_id',
                'currency': 'currency',
                'is_offer': True,
                'payment_type': 'prepaid',
            },
        ],
    }


@pytest.mark.parametrize('has_drive', [pytest.param(True, id='drive'), False])
@pytest.mark.parametrize(
    'has_eats, has_external_id',
    [
        pytest.param(True, False, id='eats (user with out external_id)'),
        pytest.param(True, True, id='eats (user with external_id)'),
        pytest.param(False, False, id='no eats'),
    ],
)
@pytest.mark.parametrize('has_taxi', [pytest.param(True, id='taxi'), False])
@pytest.mark.now('2020-02-02T03:00:00.000')
async def test_act_report_generation(
        stq3_context,
        db,
        mockserver,
        patch,
        autotranslations,
        mock_corp_discounts,
        mock_corp_clients,
        mock_user_api,
        has_drive: bool,
        has_eats: bool,
        has_external_id: bool,
        has_taxi: bool,
):
    report_id = 'new_act_task_id_000'
    mock_corp_clients.data.get_contracts_response = make_contracts_response(
        has_drive, has_eats, has_taxi,
    )

    @patch('corp_reports.utils.yql_extensions.run_query')
    async def _run_query(query, title, query_parameters=None, **kwargs):
        assert query_parameters is None
        if 'services/taxi-corp/raw_reports/drive/' in query:
            return [DRIVE_ORDER]
        if 'services/taxi-corp/raw_reports/eats/' in query:
            return [EATS_ORDER]
        if 'services/taxi-corp/raw_reports/taxi/' in query:
            return [TAXI_ORDER]

        assert False, 'unexpected query'

    @patch('corp_reports.internal.orders.acts.fetchers.read_yt_orders')
    async def _read_table(app, table_path, contract_id):
        if 'drive' in table_path:
            return [DRIVE_ORDER]
        if 'eats' in table_path:
            return [EATS_ORDER]
        if 'taxi' in table_path:
            return [TAXI_ORDER]
        assert False, f'unexpected service table path "{table_path}"'

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_uid(*args, **kwargs):
        return {'uid': '11111', 'login': 'some_manager'}

    file_contents = None

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(*args, **kwargs):
        nonlocal file_contents

        assert 'file_obj' in kwargs
        file_contents = kwargs['file_obj']
        return 'mds_key'

    if has_external_id:
        await db.corp_users.update(
            {'_id': '3fd5decbe4364762baea7b6dd0848517'},
            {'$set': {'external_id': '123456'}},
        )

    await corp_generate_orders_report.task(stq3_context, report_id=report_id)

    _check_file_contents(
        file_contents, has_drive, has_eats, has_taxi, has_external_id,
    )
