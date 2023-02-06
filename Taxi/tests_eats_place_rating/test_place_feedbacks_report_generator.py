import base64
import json

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


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
async def test_place_feedbacks_report_stq_no_repeat(
        stq_runner, testpoint, mockserver,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 123, 'personal_uuid': 'uuid123'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_place_access.times_called == 1


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_report_stq_yt(
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
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        res = base64.b64decode(request.json['attachments'][0]['data']).decode(
            'utf8',
        )
        assert res == (
            '\ufeffAddress;Rating;Weight;Order nr;'
            'Created at;Custom comment;Predefined comments\r\n'
            ';5;;210405-440276;2021-04-05T10:08:19.469466+0300;blabla;'
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
    assert mock_place_access.times_called == 1
    assert mock_send_email.times_called == 1


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_report_stq_yt_null(
        stq_runner, testpoint, mockserver, yt_apply, load_json,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
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
                    'id': 136015,
                    'revision_id': 100,
                    'updated_at': '2020-03-02T20:47:44.338Z',
                    'address': {'city': 'Москва', 'short': 'ул.Васильки д.4'},
                    'name': 'name',
                },
            ],
            'not_found_place_ids': [],
        }

    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        res = base64.b64decode(request.json['attachments'][0]['data']).decode(
            'utf8',
        )
        assert res == (
            '\ufeffAddress;Rating;Weight;Order nr;'
            'Created at;Custom comment;Predefined comments\r\n'
            'ул.Васильки д.4;;;210609-477063;2021-06-10T13:11:54+0300;;'
        )
        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 888, 'personal_uuid': 'uuid999'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 1
    assert mock_retrieve_by_ids.times_called == 1
    assert mock_place_access.times_called == 1
    assert mock_send_email.times_called == 1


@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_feedback_reports_continue.sql',),
)
async def test_place_feedbacks_report_stq_continue(
        stq_runner,
        testpoint,
        mds_s3_storage,
        mockserver,
        pgsql,
        load,
        load_json,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

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
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        return mockserver.make_response(status=204)

    data = [
        {
            'place_id': 1,
            'order_nr': '100',
            'rating': 4,
            'comment': 'SuperComment1',
            'created_at': '2020-03-02T20:47:44.338Z',
            'predefined_comment_ids': [13, 14],
        },
        {
            'place_id': 1,
            'order_nr': '101',
            'rating': 2,
            'comment': 'Figna',
            'created_at': '2020-03-03T20:41:44.138Z',
            'predefined_comment_ids': [10],
        },
        {
            'place_id': 1,
            'order_nr': '102',
            'rating': 5,
            'comment': 'Supe2',
            'created_at': '2020-03-04T20:42:00.238Z',
            'predefined_comment_ids': [],
        },
    ]
    mds_s3_storage.put_object(
        'partner_123/ea535bef-99e0-4340-b007-e2eca908bedb.json',
        json.dumps(data).encode('utf-8'),
    )

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={
            'partner_id': 123,
            'personal_uuid': 'ea535bef-99e0-4340-b007-e2eca908bedb',
        },
        expect_fail=False,
    )

    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 1
    assert mock_retrieve_by_ids.times_called == 1
    assert mock_send_email.times_called == 1

    data = get_feedback_reports(pgsql)
    assert (
        len(data) == 1
        and data[0]['partner_id'] == 123
        and data[0]['status'] == 'done'
    )

    s3_data = mds_s3_storage.get_object(
        'partner_123/ea535bef-99e0-4340-b007-e2eca908bedb.csv',
    ).data
    assert s3_data
    s3_data = s3_data.replace(b'\r\n', b'\n')
    assert s3_data.decode('utf8') == load('expected_mail.csv')

    assert (
        mds_s3_storage.get_object(
            'partner_123/ea535bef-99e0-4340-b007-e2eca908bedb.xls',
        )
        is None
    )


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_report_year_not_exist_at_yt(
        stq_runner, testpoint, mockserver, yt_apply, load_json, taxi_config,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
        req_json = request.json
        assert req_json['partner_id'] == 999 and req_json['place_ids'] == [
            1,
            2,
            3,
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
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        assert request.json['data'] == {
            'dttm_start': '2020-04-05',
            'dttm_finish': '2020-04-06',
        }

        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 999, 'personal_uuid': 'uuid9999'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 0
    assert mock_retrieve_by_ids.times_called == 0
    assert mock_place_access.times_called == 1
    assert mock_send_email.times_called == 1


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_place_feedbacks_skip_comment(
        stq_runner, testpoint, mockserver, yt_apply, load_json, taxi_config,
):
    @testpoint('Reschedule')
    def reschedule_stq(arg):
        pass

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def mock_place_access(request):
        req_json = request.json
        assert req_json['partner_id'] == 100 and req_json['place_ids'] == [555]
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
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def mock_send_email(request):
        assert request.json == {
            'recipients': {'partner_ids': [100]},
            'data': {'dttm_start': '2021-06-10', 'dttm_finish': '2021-06-11'},
            'event_mode': 'asap',
        }

        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_generate_report.call(
        task_id='task1',
        kwargs={'partner_id': 100, 'personal_uuid': 'uuid100'},
        expect_fail=False,
    )
    assert reschedule_stq.times_called == 0
    assert mock_predefined_comments.times_called == 0
    assert mock_retrieve_by_ids.times_called == 0
    assert mock_place_access.times_called == 1
    assert mock_send_email.times_called == 1
