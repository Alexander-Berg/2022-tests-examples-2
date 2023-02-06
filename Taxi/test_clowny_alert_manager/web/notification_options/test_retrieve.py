import pytest

from testsuite.utils import matching


@pytest.mark.parametrize(
    'no_id, status, data',
    [
        (
            3,
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'notification option for id 3 not found',
            },
        ),
        (
            1,
            200,
            {
                'id': 1,
                'logins': ['d1mbas'],
                'name': 'telegram_option1',
                'repo_meta': {'config_project': '', 'file_name': ''},
                'statuses': [{'from': 'OK', 'to': 'WARN'}],
                'type': 'telegram',
                'updated_at': matching.datetime_string,
                'created_at': matching.datetime_string,
                'is_deleted': False,
            },
        ),
    ],
)
async def test_get(get_notification_option, no_id, status, data):
    assert (await get_notification_option(no_id, status)) == data


@pytest.mark.parametrize(
    'filters, max_id, options_count',
    [({}, 2, 2), ({'limit': 1}, 1, 1), ({'cursor': {'newer_than': 1}}, 2, 1)],
)
async def test_list(
        get_notification_options_list, filters, max_id, options_count,
):
    data = await get_notification_options_list(filters)
    assert len(data['notification_options']) == options_count
    assert data['cursor']['newer_than'] == max_id
