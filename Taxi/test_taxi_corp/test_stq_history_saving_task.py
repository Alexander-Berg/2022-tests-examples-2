# pylint: disable=redefined-outer-name
import datetime

import bson
import pytest

from taxi_corp import stq

HISTORY_SAVING_DT = datetime.datetime(year=2021, month=4, day=14)


@pytest.mark.parametrize(
    ['doc_ids', 'expected_history'],
    [
        pytest.param(
            ['test_user_1', 'test_user_2', 'test_user_3'],
            [
                {
                    'c': 'corp_users',
                    'p': 'corp',
                    'p_uid': 123,
                    'a': 'PUT',
                    'e': {
                        '_id': 'test_user_1',
                        'client_id': 'client3',
                        'cost_centers_id': 'cost_center_0',
                        'department_id': 'dep1',
                        'email': 'svyat@yandex-team.ru',
                        'email_id': '2be877a7920342579ab7387adc67d642',
                        'fullname': 'good user',
                        'is_active': True,
                        'limits': [
                            {
                                'limit_id': 'limit3_2_with_users',
                                'service': 'taxi',
                            },
                            {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                            {'limit_id': 'drive_limit', 'service': 'drive'},
                            {
                                'limit_id': 'limit3_2_tanker',
                                'service': 'tanker',
                            },
                        ],
                        'nickname': None,
                        'personal_phone_id': (
                            'd0f7a7842295497facae12ff05441631'
                        ),
                        'phone': '+79654646546',
                        'phone_id': bson.ObjectId('aaaaaaaaaaaaa79654646546'),
                        'services': {
                            'drive': {'drive_user_id': 'drive_user_id_1'},
                            'eats2': {
                                'is_active': True,
                                'was_sms_sent': False,
                            },
                            'taxi': {'send_activation_sms': True},
                        },
                        'stat': {'2021-04': {'spent_with_vat': 2000000}},
                    },
                    'ip': '123',
                    'cl': 'client3',
                    'd': HISTORY_SAVING_DT,
                },
                {
                    'c': 'corp_users',
                    'p': 'corp',
                    'p_uid': 123,
                    'a': 'PUT',
                    'e': {
                        '_id': 'test_user_2',
                        'client_id': 'client3',
                        'cost_centers_id': 'cost_center_1',
                        'department_id': None,
                        'email': 'svyat@yandex-team.ru',
                        'email_id': '2be877a7920342579ab7387adc67d642',
                        'fullname': 'user in root department',
                        'is_active': True,
                        'limits': [
                            {
                                'limit_id': 'limit3_2_with_users',
                                'service': 'taxi',
                            },
                        ],
                        'nickname': None,
                        'personal_phone_id': (
                            'd0f7a7842295497facae12ff05441632'
                        ),
                        'phone': '+79654646545',
                        'phone_id': bson.ObjectId('aaaaaaaaaaaaa79654646545'),
                        'services': {
                            'drive': {'task_id': 'updating_limits_in_drive'},
                            'eats2': {
                                'is_active': True,
                                'was_sms_sent': False,
                            },
                            'taxi': {'send_activation_sms': True},
                        },
                    },
                    'ip': '123',
                    'cl': 'client3',
                    'd': HISTORY_SAVING_DT,
                },
            ],
            id='common path',
        ),
        pytest.param(['unknown_id'], [], id='unknown doc id'),
    ],
)
async def test_common_flow(
        db, taxi_corp_app_stq, mock_drive, doc_ids, expected_history,
):
    await stq.save_to_history(
        taxi_corp_app_stq,
        'corp_users',
        doc_ids,
        {'login': 'corp', 'uid': 123, 'method': 'PUT', 'user_ip': '123'},
        HISTORY_SAVING_DT,
    )

    history = (
        await db.corp_history.find(
            {'d': HISTORY_SAVING_DT}, projection={'_id': False},
        )
        .sort('e._id', 1)
        .to_list(None)
    )
    assert history == expected_history
