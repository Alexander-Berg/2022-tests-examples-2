from typing import NamedTuple

import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run

PHONE = '+79261234567'
PHONE_ID = '123'
PERSONAL_PHONE_ID = '456'


class Case(NamedTuple):
    phone_called_count: int
    personal_phone_called_count: int
    content: str


@pytest.mark.config(TVM_RULES=[{'src': 'taxi_exp', 'dst': 'personal'}])
@pytest.mark.parametrize(
    'phone_called_count, personal_phone_called_count, content',
    [
        pytest.param(
            *Case(3, 0, (PHONE_ID + '\n')),
            marks=[
                pytest.mark.config(
                    EXP3_ADMIN_CONFIG={
                        'settings': {
                            'backend': {
                                'tags_staff_departments': {
                                    'team': {'department_ids': [1]},
                                },
                            },
                        },
                    },
                ),
            ],
            id='default source',
        ),
        pytest.param(
            *Case(3, 0, (PHONE_ID + '\n')),
            marks=[
                pytest.mark.config(
                    EXP3_ADMIN_CONFIG={
                        'settings': {
                            'backend': {
                                'tags_staff_departments': {
                                    'team': {
                                        'department_ids': [1],
                                        'source': 'phone_id',
                                    },
                                },
                            },
                        },
                    },
                ),
            ],
            id='source phone_id',
        ),
        pytest.param(
            *Case(0, 3, (PERSONAL_PHONE_ID + '\n')),
            marks=[
                pytest.mark.config(
                    EXP3_ADMIN_CONFIG={
                        'settings': {
                            'backend': {
                                'tags_staff_departments': {
                                    'team': {
                                        'department_ids': [1],
                                        'source': 'personal_phone_id',
                                    },
                                },
                            },
                        },
                    },
                ),
            ],
            id='source personal_phone_id',
        ),
    ],
)
async def test_update_extra_tags_use_personal_phone_id(
        mockserver,
        patch_aiohttp_session,
        response_mock,
        taxi_exp_client,
        phone_called_count,
        personal_phone_called_count,
        content,
):
    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        return response_mock(
            json={
                'result': [{'phones': [{'number': PHONE}], 'id': 0}],
                'pages': 1,
                'page': 1,
            },
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _phone_ids_from_personal(request):
        return {'items': [{'id': PERSONAL_PHONE_ID, 'value': PHONE}]}

    @mockserver.json_handler('/user-api/user_phones/bulk')
    async def _phone_id_from_user_api(request):
        return {
            'items': [
                {
                    'id': PHONE_ID,
                    'phone': PHONE,
                    'type': 'yandex',
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'stat': '',
                    'is_loyal': False,
                    'is_yandex_staff': True,
                    'is_taxi_staff': True,
                },
            ],
        }

    trusted_files = []

    @mockserver.json_handler('/taxi-exp/v1/files/')
    async def _trusted_files(request):
        trusted_files_data = request.get_data()
        trusted_files.append(trusted_files_data)

        return {}

    @mockserver.json_handler('/taxi-exp/v1/trusted-files/metadata/')
    async def _trusted_file_metadata(request):
        return {}

    await cron_run.main(
        ['taxi_exp.stuff.update_tags.extra_tags_proc', '-t', '0'],
    )

    assert _phone_id_from_user_api.times_called == phone_called_count
    assert _phone_ids_from_personal.times_called == personal_phone_called_count
    assert len(trusted_files) == 1
    assert trusted_files[0] == content.encode()
