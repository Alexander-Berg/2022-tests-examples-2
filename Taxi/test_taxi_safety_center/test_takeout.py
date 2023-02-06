import dataclasses
from typing import Dict
from typing import List

import pytest

from taxi_safety_center import models
from taxi_safety_center.repositories import personal


@dataclasses.dataclass
class TakeoutUser:
    id: str  # pylint: disable=invalid-name  # mirrors actual request
    yandex_uid: str
    phone_id: str


MOCK_EXISTING_USER = TakeoutUser(
    id='MOCK_EXISTING_USER_ID',
    yandex_uid='MOCK_EXISTING_YANDEX_UID',
    phone_id='MOCK_EXISTING_PHONE_ID',
)

MOCK_ANOTHER_EXISTING_USER = TakeoutUser(
    id='MOCK_ANOTHER_USER_ID',
    yandex_uid='MOCK_ANOTHER_YANDEX_UID',
    phone_id='MOCK_ANOTHER_PHONE_ID',
)

MOCK_NONEXISTENT_USER = TakeoutUser(
    id='MOCK_NONEXISTENT_USER_ID',
    yandex_uid='MOCK_NONEXISTENT_YANDEX_UID',
    phone_id='MOCK_NONEXISTENT_PHONE_ID',
)
TAKEOUT_OK_RESPONSE_FILE = 'takeout_response_ok.json'
TAKEOUT_OK_MULTIPLE_RESPONSE_FILE = 'takeout_response_ok_multiple.json'
TAKEOUT_NO_DATA_RESPONSE_FILE = 'takeout_response_no_data.json'

INITIAL_DB = dict(
    MOCK_EXISTING_YANDEX_UID='{"(foobar,+79151234567_id)"}',
    MOCK_ANOTHER_YANDEX_UID='{"(barfoo,+79157654321_id)"}',
)


async def _mock_phones_from_ids_and_names(
        ids_and_names: Dict[str, str], *args, **kwargs,
) -> models.Phones:
    phones = models.Phones()
    for phone_id, name in ids_and_names.items():
        phone = models.Phone(
            number=phone_id[:-3], personal_phone_id=phone_id, name=name,
        )
        phones.append(phone)  # pylint: disable=no-member   # False alarm
    return phones


@pytest.mark.config(TVM_RULES=[{'src': 'safety-center', 'dst': 'personal'}])
@pytest.mark.pgsql('safety_center', files=['db_safety_center.sql'])
@pytest.mark.parametrize(
    ['takeout_users', 'expected_response_file'],
    [
        pytest.param(
            [MOCK_EXISTING_USER],
            TAKEOUT_OK_RESPONSE_FILE,
            id='ok one for sure',
        ),
        pytest.param(
            [MOCK_EXISTING_USER, MOCK_NONEXISTENT_USER],
            TAKEOUT_OK_RESPONSE_FILE,
            id='ok two',
        ),
        pytest.param(
            [MOCK_NONEXISTENT_USER],
            TAKEOUT_NO_DATA_RESPONSE_FILE,
            id='not ok since no data',
        ),
        pytest.param(
            [],
            TAKEOUT_NO_DATA_RESPONSE_FILE,
            id='not ok since no users are provided',
        ),
        pytest.param(
            [MOCK_EXISTING_USER, MOCK_ANOTHER_EXISTING_USER],
            TAKEOUT_OK_MULTIPLE_RESPONSE_FILE,
            id='ok with multiple duh',
        ),
    ],
)
async def test_takeout(
        web_app_client,
        monkeypatch,
        load_json,
        takeout_users: List[TakeoutUser],
        expected_response_file: str,
):
    monkeypatch.setattr(
        personal, 'phones_from_ids_and_names', _mock_phones_from_ids_and_names,
    )
    takeout_request = {
        'yandex_uid': 'foobar',
        'users': [dataclasses.asdict(tu) for tu in takeout_users],
    }
    response = await web_app_client.post(
        '/v1/internal/takeout', json=takeout_request,
    )
    assert response.status == 200
    response_json = await response.json()
    expected_json = load_json(expected_response_file)
    assert response_json == expected_json


@pytest.mark.pgsql('safety_center', files=['db_safety_center.sql'])
@pytest.mark.parametrize(
    ['yandex_uids', 'expected_db'],
    [
        pytest.param(
            ['MOCK_EXISTING_YANDEX_UID', 'MOCK_ANOTHER_YANDEX_UID'],
            [],
            id='delete_all',
        ),
        pytest.param(
            ['MOCK_EXISTING_YANDEX_UID', 'MOCK_NONEXISTENT_YANDEX_UID'],
            ['MOCK_ANOTHER_YANDEX_UID'],
            id='delete_partially',
        ),
    ],
)
async def test_takeout_delete(web_app_client, yandex_uids, expected_db, pgsql):
    yandex_uids = [{'uid': x, 'is_portal': True} for x in yandex_uids]
    takeout_request = {'request_id': '12345', 'yandex_uids': yandex_uids}
    response = await web_app_client.post(
        '/v1/takeout/delete', json=takeout_request,
    )
    assert response.status == 200

    cursor = pgsql['safety_center'].cursor()
    cursor.execute('SELECT * from safety_center.contacts')
    result = [row[:2] for row in cursor]
    assert result == [(user, INITIAL_DB[user]) for user in expected_db]


@pytest.mark.config(TVM_RULES=[{'src': 'safety-center', 'dst': 'personal'}])
@pytest.mark.pgsql('safety_center', files=['db_safety_center.sql'])
@pytest.mark.parametrize(
    ['yandex_uids', 'data_status'],
    [
        pytest.param(
            ['MOCK_EXISTING_YANDEX_UID', 'MOCK_ANOTHER_YANDEX_UID'],
            'ready_to_delete',
            id='ready_to_delete',
        ),
        pytest.param(['MOCK_NONEXISTENT_YANDEX_UID'], 'empty', id='no_data'),
    ],
)
async def test_takeout_status(
        web_app_client, yandex_uids, data_status, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _mock_bulk_retrieve(request):
        request_json = request.json
        return {
            'items': [
                {'id': item['id'], 'value': item['id'][::-1]}
                for item in request_json['items']
            ],
        }

    yandex_uids = [{'uid': x, 'is_portal': True} for x in yandex_uids]
    takeout_request = {'yandex_uids': yandex_uids}
    response = await web_app_client.post(
        '/v1/takeout/status', json=takeout_request,
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['data_state'] == data_status
