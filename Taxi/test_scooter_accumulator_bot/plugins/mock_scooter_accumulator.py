import aiohttp.web
import pytest


def sa_charge(request):
    assert request.method == 'GET' or request.method == 'POST'

    if request.method == 'POST':
        if request.query['accumulator_id'] == 'acc_1':
            return 200, {}
        return 404, {}

    if request.query['accumulator_id'] == 'acc_1':
        return 200, {'accumulator_charge': 95}
    return 404, {}


def sa_bookings(request):
    assert request.method == 'GET'

    if (
            request.query['contractor_id']
            == '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c'  # noqa: E501 line too long
    ):
        if request.query['cabinet_id'] == 'cabinet_take_all_id':
            return {
                'bookings': [
                    {
                        'booking_id': 'booking_id1',
                        'status': 'CREATED',
                        'cell_id': 'cell_id1',
                        'accumulator_id': 'acc_1',
                    },
                ],
                'cabinet_type': 'cabinet_without_validation',
            }

        if request.query['cabinet_id'] == 'cabinet_return_all_id':
            return {
                'bookings': [
                    {
                        'booking_id': 'booking_id1',
                        'status': 'CREATED',
                        'cell_id': 'cell_id1',
                    },
                ],
                'cabinet_type': 'cabinet_without_validation',
            }

        if request.query['cabinet_id'] == 'cabinet_deferred_validate_id':
            return {
                'bookings': [
                    {
                        'booking_id': 'booking_id1',
                        'status': 'DEFERRED_VALIDATED',
                        'cell_id': 'cell_id1',
                    },
                ],
                'cabinet_type': 'cabinet_without_validation',
            }

        if request.query['cabinet_id'] == 'cabinet_inconsistent_bookings_id':
            return {
                'bookings': [
                    {
                        'booking_id': 'booking_id1',
                        'status': 'CREATED',
                        'cell_id': 'cell_id1',
                    },
                    {
                        'booking_id': 'booking_id1',
                        'status': 'PROCESSED',
                        'cell_id': 'cell_id2',
                        'accumulator_id': 'acc_1',
                    },
                ],
                'cabinet_type': 'cabinet',
            }

        return {
            'bookings': [
                {
                    'booking_id': 'booking_id1',
                    'status': 'CREATED',
                    'cell_id': 'cell_id1',
                    'accumulator_id': 'acc_1',
                },
            ],
            'cabinet_type': 'charge_station',
        }

    return {'bookings': [], 'cabinet_type': 'cabinet'}


def sa_taken(request):
    assert request.method == 'POST'

    if request.query['accumulator_id'] == 'acc_1':
        return {
            'booking_id': 'booking_id1',
            'status': 'PROCESSED',
            'cell_id': 'cell_id1',
            'accumulator_id': 'acc_1',
        }

    return {'code': 'accumulator_id_was_not_found'}


def sa_taken_all(request):
    assert request.method == 'POST'

    return {
        'bookings': [
            {
                'booking_id': 'booking_id1',
                'status': 'PROCESSED',
                'cell_id': 'cell_id1',
                'accumulator_id': 'acc_1',
            },
        ],
        'cabinet_type': 'cabinet_without_validation',
    }


def sa_return(request):
    assert request.method == 'POST'

    return {
        'booking_id': 'booking_id1',
        'status': 'PROCESSED',
        'cell_id': 'cell_id1',
    }


def sa_return_all(request):
    assert request.method == 'POST'

    return {
        'bookings': [
            {
                'booking_id': 'booking_id1',
                'status': 'DEFERRED_PROCESSED',
                'cell_id': 'cell_id1',
            },
        ],
        'cabinet_type': 'cabinet_without_validation',
    }


def sa_fallback_return_validated(request):
    assert request.method == 'POST'

    return {}


def sa_add_acc(request):
    assert request.method == 'POST'

    return {
        'accumulator_id': request.json['accumulator_id'],
        'serial_number': request.json['serial_number'],
        'charge': 90,
        'created_at': '2021-11-11T15:56:12.646822+00:00',
        'updated_at': '2021-11-11T15:56:12.646822+00:00',
        'place': {'scooter_id': 'scooter_id1'},
    }


def sa_list_accs(request):
    assert request.method == 'POST'
    return {
        'accumulators': [
            {
                'accumulator_id': 'acc_1',
                'serial_number': 'acc_serial_1',
                'charge': 100,
                'created_at': '2021-09-07T15:56:12.646822+00:00',
                'updated_at': '2021-09-07T15:56:12.646822+00:00',
                'place': {},
            },
            {
                'accumulator_id': 'acc_2',
                'serial_number': 'acc_serial_2',
                'charge': 50,
                'created_at': '2021-09-07T15:56:13.646822+00:00',
                'updated_at': '2021-09-07T15:56:13.646822+00:00',
                'place': {},
            },
        ],
    }


def sa_unbook(request):
    assert request.method == 'POST'
    return {}


def sa_cabinets(request):
    assert request.method == 'POST'

    if request.json['cabinet_name'] == 'cabinet_take_all_name':
        return {
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_take_all_id',
                    'depot_id': 'depot_id',
                    'cabinet_name': 'cabinet_take_all_name',
                    'cabinet_type': 'cabinet_without_validation',
                    'created_at': '2021-11-11T15:56:12.646822+00:00',
                    'updated_at': '2021-11-11T15:56:12.646822+00:00',
                    'accums_available_for_booking': 0,
                    'empty_cells_available_for_booking': 0,
                    'accumulators_count': 0,
                    'cells_count': 0,
                },
            ],
        }

    if request.json['cabinet_name'] == 'cabinet_return_all_name':
        return {
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_return_all_id',
                    'depot_id': 'depot_id',
                    'cabinet_name': 'cabinet_return_all_name',
                    'cabinet_type': 'cabinet_without_validation',
                    'created_at': '2021-11-11T15:56:12.646822+00:00',
                    'updated_at': '2021-11-11T15:56:12.646822+00:00',
                    'accums_available_for_booking': 0,
                    'empty_cells_available_for_booking': 0,
                    'accumulators_count': 0,
                    'cells_count': 0,
                },
            ],
        }

    if request.json['cabinet_name'] == 'cabinet_deferred_validate_name':
        return {
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_deferred_validate_id',
                    'depot_id': 'depot_id',
                    'cabinet_name': 'cabinet_deferred_validate_name',
                    'cabinet_type': 'cabinet_without_validation',
                    'created_at': '2021-11-11T15:56:12.646822+00:00',
                    'updated_at': '2021-11-11T15:56:12.646822+00:00',
                    'accums_available_for_booking': 0,
                    'empty_cells_available_for_booking': 0,
                    'accumulators_count': 0,
                    'cells_count': 0,
                },
            ],
        }

    if request.json['cabinet_name'] == 'cabinet_inconsistent_bookings_name':
        return {
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_inconsistent_bookings_id',
                    'depot_id': 'depot_id',
                    'cabinet_name': 'cabinet_inconsistent_bookings_name',
                    'cabinet_type': 'cabinet_without_validation',
                    'created_at': '2021-11-11T15:56:12.646822+00:00',
                    'updated_at': '2021-11-11T15:56:12.646822+00:00',
                    'accums_available_for_booking': 0,
                    'empty_cells_available_for_booking': 0,
                    'accumulators_count': 0,
                    'cells_count': 0,
                },
            ],
        }

    if request.json['cabinet_name'] == 'cabinet_name':
        return {
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_id',
                    'depot_id': 'depot_id',
                    'cabinet_name': 'cabinet_name',
                    'cabinet_type': 'charge_station',
                    'created_at': '2021-11-11T15:56:12.646822+00:00',
                    'updated_at': '2021-11-11T15:56:12.646822+00:00',
                    'accums_available_for_booking': 0,
                    'empty_cells_available_for_booking': 0,
                    'accumulators_count': 0,
                    'cells_count': 0,
                },
            ],
        }

    return {'cabinets': []}


@pytest.fixture
def scooter_accumulator_bot_scooter_accumulator_mocks(
        mock_scooter_accumulator,
):  # pylint: disable=C0103
    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/accumulator/charge',
    )
    async def _get_charge(request):
        code, json = sa_charge(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/cabinet/operating-bookings',
    )
    async def _operating_bookings(request):
        return aiohttp.web.json_response(sa_bookings(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/booking/accumulator-taken-processed',  # noqa: E501 line too long
    )
    async def _taken_processed(request):
        return aiohttp.web.json_response(sa_taken(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/booking/accumulator-taken-processed-all',  # noqa: E501 line too long
    )
    async def _taken_processed_all(request):
        return aiohttp.web.json_response(sa_taken_all(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/booking/accumulator-return-processed',  # noqa: E501 line too long
    )
    async def _return_processed(request):
        return aiohttp.web.json_response(sa_return(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/booking/accumulator-return-processed-all',  # noqa: E501 line too long
    )
    async def _return_processed_all(request):
        return aiohttp.web.json_response(sa_return_all(request))

    @mock_scooter_accumulator('/scooter-accumulator/v1/admin-api/accumulator')
    async def _add_accumulator(request):
        return aiohttp.web.json_response(sa_add_acc(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/admin-api/accumulator/list',
    )
    async def _list_accumulators(request):
        return aiohttp.web.json_response(sa_list_accs(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/admin-api/cabinet/booking/unbook',
    )
    async def _unbook(request):
        return aiohttp.web.json_response(sa_unbook(request))

    @mock_scooter_accumulator('/scooter-accumulator/v1/admin-api/cabinet/list')
    async def _list_cabinets(request):
        return aiohttp.web.json_response(sa_cabinets(request))

    @mock_scooter_accumulator(
        '/scooter-accumulator/v1/fallback-api/cabinet/booking/accumulator-return-validated',  # noqa: E501 line too long
    )
    async def _return_validated(request):
        return aiohttp.web.json_response(sa_fallback_return_validated(request))
