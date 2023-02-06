import pytest


def relations_tree(data):
    subject = {'type': data['type'], 'id': data['external_id'], 'rel': {}}
    data['linked_subjects'] = sorted(
        data['linked_subjects'], key=lambda x: x['external_id'],
    )
    for rel in data['linked_subjects']:
        rel_str_key = rel['type'] + '|' + rel['external_id']
        subject['rel'][rel_str_key] = relations_tree(rel)

    return subject


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.parametrize(
    'post_requests, assert_result',
    [
        (['subjects_delivery_request1.json'], 'assert_single_delivery.json'),
        (
            [
                'subjects_delivery_request1.json',
                'subjects_delivery_request2.json',
                'subjects_waybill_request1.json',
                'subjects_delivery_request1.json',
            ],
            'assert_batch_of_two_deliveries.json',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_for_calc_tree_json_testpoint(
        taxi_eats_logistics_performer_payouts,
        load_json,
        testpoint,
        post_requests,
        assert_result,
):
    @testpoint('test_subject_for_read')
    def json_testpoint(data):
        pass

    async def post_subject_json(static_file_name):
        response = await taxi_eats_logistics_performer_payouts.post(
            '/v1/subjects', json=load_json(static_file_name),
        )
        assert response.status_code == 200
        assert json_testpoint.times_called == 1

    for request_file in post_requests:
        await post_subject_json(request_file)
        res = json_testpoint.next_call()

    assert relations_tree(res['data']) == relations_tree(
        load_json(assert_result),
    )
