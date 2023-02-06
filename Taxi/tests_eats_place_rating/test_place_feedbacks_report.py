import pytest


def get_feedback_reports(pgsql):
    cursor = pgsql['eats_place_rating'].dict_cursor()

    cursor.execute(
        """
        SELECT
            *
        FROM
            eats_place_rating.feedback_reports
        ORDER BY partner_id, idempotency_key
    """,
    )
    return cursor.fetchall()


async def test_add_report_same_idempotency(
        taxi_eats_place_rating, mock_authorizer_allowed, stq,
):
    report_filter = {
        'predefined_comment_ids': [1, 2, 3],
        'ratings': [3, 5],
        'place_ids': [1, 2],
        'dttm_start': '2020-11-24T00:00:00Z',
        'dttm_finish': '2020-11-24T23:59:59Z',
    }

    file_format = 'csv'
    time_zone = 'Europe/Moscow'

    partner_id = '1'
    idempotency_token1 = '1au'

    response1 = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        json={
            'filter': report_filter,
            'file_format': file_format,
            'time_zone': time_zone,
        },
        headers={
            'X-YaEda-PartnerId': partner_id,
            'X-Idempotency-Token': idempotency_token1,
        },
    )

    assert response1.status_code == 200
    response1 = response1.json()

    response2 = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        json={
            'filter': report_filter,
            'file_format': 'csv',
            'time_zone': time_zone,
        },
        headers={
            'X-YaEda-PartnerId': partner_id,
            'X-Idempotency-Token': idempotency_token1,
        },
    )

    assert response2.status_code == 200
    response2 = response2.json()

    assert response1['uuid'] == response2['uuid']

    assert stq.eats_place_rating_generate_report.times_called == 1
    call1 = stq.eats_place_rating_generate_report.next_call()['kwargs']

    assert call1['partner_id'] == 1


async def test_add_report(
        taxi_eats_place_rating, mock_authorizer_allowed, stq, pgsql,
):
    report_filter = {
        'predefined_comment_ids': [1, 2, 3],
        'ratings': [3, 5],
        'place_ids': [6, 7],
        'dttm_start': '2020-11-24T00:00:00Z',
        'dttm_finish': '2020-11-24T23:59:59Z',
    }
    time_zone = 'Europe/Moscow'
    partner_id = '1'
    idempotency_token1 = '1au'
    idempotency_token2 = '1au2'

    response1 = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        json={
            'filter': report_filter,
            'file_format': 'csv',
            'time_zone': time_zone,
        },
        headers={
            'X-YaEda-PartnerId': partner_id,
            'X-Idempotency-Token': idempotency_token1,
        },
    )

    assert response1.status_code == 200
    response1 = response1.json()

    response2 = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        json={
            'filter': report_filter,
            'file_format': 'csv',
            'time_zone': time_zone,
        },
        headers={
            'X-YaEda-PartnerId': partner_id,
            'X-Idempotency-Token': idempotency_token2,
        },
    )

    assert response2.status_code == 200
    response2 = response2.json()

    assert response1['uuid'] != response2['uuid']

    assert stq.eats_place_rating_generate_report.times_called == 2
    call1 = stq.eats_place_rating_generate_report.next_call()['kwargs']
    call2 = stq.eats_place_rating_generate_report.next_call()['kwargs']

    assert call1['partner_id'] == call2['partner_id']
    assert call1['personal_uuid'] != call2['personal_uuid']

    rows = get_feedback_reports(pgsql)
    assert rows[0]['partner_id'] == 1
    assert rows[0]['idempotency_key'] == '1au'
    assert rows[0]['filter'] == (
        '("{1,2,3}","{3,5}","{6,7}","2020-11-24 03:00:00+03"'
        ',"2020-11-25 02:59:59+03")'
    )


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_fill.sql',),
)
async def test_get_status(taxi_eats_place_rating, mock_authorizer_allowed):
    uuid = '1'
    partner_id = '1'

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        params={'uuid': uuid},
        headers={'X-YaEda-PartnerId': partner_id},
    )

    assert response.status_code == 200
    response = response.json()

    assert response['report_status'] == 'new'


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_fill.sql',),
)
async def test_get_status_no_uuid(
        taxi_eats_place_rating, mock_authorizer_allowed,
):
    uuid = '3'
    partner_id = '1'

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        params={'uuid': uuid},
        headers={'X-YaEda-PartnerId': partner_id},
    )

    assert response.status_code == 404
    response = response.json()

    assert response == {
        'code': '404',
        'message': 'There is no user with uuid 3',
    }


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_fill.sql',),
)
async def test_get_status_no_access(
        taxi_eats_place_rating, mock_authorizer_403,
):
    uuid = '1'
    partner_id = '1'

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        params={'uuid': uuid},
        headers={'X-YaEda-PartnerId': partner_id},
    )

    assert response.status_code == 403
    response = response.json()

    assert response == {
        'code': '403',
        'message': 'Access for getting status is denied',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_place_rating_predefined_comments_filter',
    consumers=['eats-place-rating/predefined_comments_filter'],
    clauses=[],
    default_value={
        'enabled_comments': [
            {'code': 'BAD_PACKAGE', 'type': 'dislike'},
            {'code': 'BAD_COURIER', 'type': 'dislike'},
        ],
    },
)
async def test_add_report_grouped_comments(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        stq,
        pgsql,
):
    report_filter = {
        'predefined_comment_ids': [10, 11, 12],
        'ratings': [3, 5],
        'place_ids': [6, 7],
        'dttm_start': '2020-11-24T00:00:00Z',
        'dttm_finish': '2020-11-24T23:59:59Z',
    }
    time_zone = 'Europe/Moscow'
    partner_id = '1'
    idempotency_token = '1au'

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/predefined-comments',
    )
    def _mock_predefined_comments(request):
        return {
            'predefined_comments': [
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 11,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_PACKAGE',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 12,
                    'show_position': 600,
                    'title': 'Испорчена упаковка',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 2,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 14,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 15,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'like',
                    'version': 'default',
                },
            ],
        }

    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks/report',
        json={
            'filter': report_filter,
            'file_format': 'csv',
            'time_zone': time_zone,
        },
        headers={
            'X-YaEda-PartnerId': partner_id,
            'X-Idempotency-Token': idempotency_token,
        },
    )

    assert response.status_code == 200
    assert stq.eats_place_rating_generate_report.times_called == 1

    rows = get_feedback_reports(pgsql)
    assert rows[0]['partner_id'] == 1
    assert rows[0]['idempotency_key'] == '1au'
    assert rows[0]['filter'] == (
        '("{11,12,14}","{3,5}","{6,7}","2020-11-24 03:00:00+03"'
        ',"2020-11-25 02:59:59+03")'
    )
