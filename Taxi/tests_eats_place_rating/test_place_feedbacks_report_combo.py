import base64

import pytest


def get_feedback_reports(pgsql):
    cursor = pgsql['eats_place_rating'].dict_cursor()

    cursor.execute(
        """
        SELECT
            *
        FROM
            eats_place_rating.feedback_reports
        ORDER BY partner_id
    """,
    )
    return cursor.fetchall()


@pytest.mark.config(
    EATS_PLACE_RATING_REPORT_CONFIGS={
        'yt_method_enabled': False,
        'eats_feedback_method_enabled': True,
    },
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_report_stq_only_service(
        stq_runner, testpoint, mockserver, yt_apply, load_json,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
        req_json = request.json
        assert req_json['partner_id'] == 777 and req_json['place_ids'] == [
            109151,
            116160,
        ]
        return {}

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/predefined-comments',
    )
    def mock_predefined_comments(request):
        return load_json('predefined_comments.json')

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def mock_retrieve_by_ids(request):
        return {
            'places': [
                {
                    'id': 1,
                    'revision_id': 100,
                    'updated_at': '2020-03-02T20:47:44.338Z',
                    'address': {'city': 'Казань', 'short': 'Тихорецкая 28'},
                    'name': 'name',
                },
            ],
            'not_found_place_ids': [],
        }

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def mock_feedbacks(request):
        if request.query['place_id'] == '116160':
            return load_json('feedbacks_response.json')
        return {'count': 0, 'feedbacks': []}

    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        res = base64.b64decode(request.json['attachments'][0]['data']).decode(
            'utf8',
        )
        assert res == (
            '\ufeffAddress;Rating;Weight;Order nr;Created at;Custom comment;'
            'Predefined comments\r\n;3;;123;2021-04-05T11:55:54.87+0300;'
            'Test Comment;Не устроил курьер, Испорчена упаковка дважды'
        )
        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 777, 'personal_uuid': 'uuid888'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 1
    assert mock_retrieve_by_ids.times_called == 1
    assert mock_place_access.times_called == 1
    assert mock_feedbacks.times_called == 2
    assert mock_send_email.times_called == 1


@pytest.mark.config(
    EATS_PLACE_RATING_REPORT_CONFIGS={
        'yt_method_enabled': True,
        'eats_feedback_method_enabled': True,
    },
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_report_stq_combo(
        stq_runner, testpoint, mockserver, yt_apply, load_json,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
        req_json = request.json
        assert req_json['partner_id'] == 777 and req_json['place_ids'] == [
            109151,
            116160,
        ]
        return {}

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/predefined-comments',
    )
    def mock_predefined_comments(request):
        return load_json('predefined_comments.json')

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def mock_retrieve_by_ids(request):
        return {
            'places': [
                {
                    'id': 1,
                    'revision_id': 100,
                    'updated_at': '2020-03-02T20:47:44.338Z',
                    'address': {'city': 'Казань', 'short': 'Тихорецкая 28'},
                    'name': 'name',
                },
            ],
            'not_found_place_ids': [],
        }

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def mock_feedbacks(request):
        if request.query['place_id'] == '116160':
            return load_json('feedbacks_response.json')
        return {'count': 0, 'feedbacks': []}

    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        res = base64.b64decode(request.json['attachments'][0]['data']).decode(
            'utf8',
        )
        assert res == (
            '\ufeffAddress;Rating;Weight;Order nr;Created at;'
            'Custom comment;Predefined comments\r\n'
            ';5;;210405-440276;2021-04-05T10:08:19.469466+0300;'
            'blabla;Не устроил курьер, Испорчена упаковка дважды\r\n'
            ';3;;123;2021-04-05T11:55:54.87+0300;Test Comment;'
            'Не устроил курьер, Испорчена упаковка дважды'
        )
        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 777, 'personal_uuid': 'uuid888'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 1
    assert mock_retrieve_by_ids.times_called == 1
    assert mock_place_access.times_called == 2
    assert mock_feedbacks.times_called == 2
    assert mock_send_email.times_called == 1
