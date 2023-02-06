import pytest

from testsuite.utils import ordered_object


async def get_sg_check_response(taxi_billing_subventions_x, request):
    response = await taxi_billing_subventions_x.post(
        '/v1/subvention_geoarea/check', request,
    )

    response_typed = {}
    for dependent_entity_info in response.json()['dependent_entities']:

        response_typed[
            dependent_entity_info['entity_type']
        ] = dependent_entity_info['dependent_entity_ids']

    return response_typed


async def run_test_for_dependent_entity(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_dependent_entity_ids,
        dependent_entity_type,
):
    request = {'name': geoarea, 'time_range': time_range}
    response_typed = await get_sg_check_response(
        taxi_billing_subventions_x, request,
    )

    actual_dependent_entity_ids = response_typed[dependent_entity_type]

    ordered_object.assert_eq(
        actual_dependent_entity_ids, expected_dependent_entity_ids, '',
    )


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-30T21:00:00+00:00',
            geoarea='sviblovo',
        ),
        a_single_ride(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            start='2020-05-02T21:00:00+00:00',
            end='2020-05-30T21:00:00+00:00',
            geoarea='sviblovo',
        ),
        a_single_ride(
            id='7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
            tariff_zone='moscow_center',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-30T21:00:00+00:00',
            geoarea='center',
        ),
        a_single_ride(
            id='1abf062a-b607-11ea-998e-07e60204cbcf',
            start='2020-05-07T21:00:00+00:00',
            end='2020-05-23T21:00:00+00:00',
            geoarea='sviblovo',
        ),
        a_single_ride(
            id='3abf062a-b607-11ea-998e-07e60204cbcf',
            tariff_zone='moscow_center',
            start='2020-05-05T21:00:00+00:00',
            end='2020-05-24T21:00:00+00:00',
            geoarea='center',
        ),
        a_single_ride(
            id='5e03538d-b607-11ea-998e-8b19d0ced3dc',
            start='2020-05-05T21:00:00+00:00',
            end='2020-05-24T21:00:00+00:00',
            geoarea='vdnh',
        ),
        a_single_ride(
            id='7fcadb4c-b607-11ea-998e-8b19d0ced3dc',
            start='2020-05-05T21:00:00+00:00',
            end='2020-05-19T21:00:00+00:00',
            geoarea='vdnh',
        ),
        a_goal(
            id='5e03538d-740b-4e0b-b5f4-1425efa59319',
            geonode='br_russia/br_moscow_center',
            start='2020-05-01T21:00:00+00:00',
            end='2020-05-29T21:00:00+00:00',
            geoarea='center',
        ),
    )


@pytest.mark.now('2020-05-28T21:00:00+00:00')
@pytest.mark.parametrize(
    'time_range, geoarea, expected_smart_rules_ids',
    [
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            ],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            [
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
            ],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            [],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            [
                '2abf062a-b607-11ea-998e-07e60204cbcf',
                'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                '1abf062a-b607-11ea-998e-07e60204cbcf',
            ],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            [
                '7fcadb4c-c02c-11ea-9e91-8b19d0ced3dc',
                '5e03538d-740b-4e0b-b5f4-1425efa59319',
                '3abf062a-b607-11ea-998e-07e60204cbcf',
            ],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            ['5e03538d-b607-11ea-998e-8b19d0ced3dc'],
        ),
    ],
)
async def test_v1_subvention_geoarea_check_only_smart_rules(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_smart_rules_ids,
):
    await run_test_for_dependent_entity(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_smart_rules_ids,
        'smart_subvention',
    )


@pytest.mark.now('2020-05-28T21:00:00+00:00')
@pytest.mark.parametrize(
    'time_range, geoarea, expected_subventions_ids,',
    [
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            ['000000000000000000000010', '000000000000000000000020'],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            ['000000000000000000000040', '000000000000000000000060'],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            [],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            [
                '000000000000000000000010',
                '000000000000000000000020',
                '000000000000000000000030',
            ],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            [
                '000000000000000000000040',
                '000000000000000000000060',
                '000000000000000000000050',
            ],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            ['000000000000000000000080'],
        ),
    ],
)
async def test_v1_subvention_geoarea_check_only_single_subventions(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_subventions_ids,
):
    await run_test_for_dependent_entity(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_subventions_ids,
        'old_ungrouped_subvention',
    )


@pytest.mark.now('2020-05-28T21:00:00+00:00')
@pytest.mark.parametrize(
    'time_range, geoarea, expected_subventions_group_ids',
    [
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            [],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            ['000000000000000000000090', '000000000000000000000100'],
        ),
        (
            {
                'start': '2020-05-28T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            [],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'sviblovo',
            [],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'center',
            ['000000000000000000000090', '000000000000000000000100'],
        ),
        (
            {
                'start': '2020-05-20T21:00:00+00:00',
                'end': '2020-05-28T21:00:00+00:00',
            },
            'vdnh',
            [],
        ),
    ],
)
async def test_v1_subvention_geoarea_check_only_grouped_subventions(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_subventions_group_ids,
):
    await run_test_for_dependent_entity(
        taxi_billing_subventions_x,
        time_range,
        geoarea,
        expected_subventions_group_ids,
        'old_grouped_subvention',
    )
