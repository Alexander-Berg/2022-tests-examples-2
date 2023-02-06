import http
import random
import string
from typing import Optional

import psycopg2.extensions
import pytest

from test_family import conftest

IP_HEADER = {'X-Remote-IP': '127.0.0.1'}


@pytest.mark.parametrize(
    'user_uid, family_id, expected_code',
    [
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_OWNER,
            conftest.FamilyIDs.VALID_FAMILY_ID,
            http.HTTPStatus.NO_CONTENT,
            id='user-family-owner',
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_MEMBER,
            conftest.FamilyIDs.VALID_FAMILY_ID,
            http.HTTPStatus.FORBIDDEN,
            id='user-family-member',
        ),
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            conftest.FamilyIDs.VALID_FAMILY_ID,
            http.HTTPStatus.NOT_FOUND,
            id='user-without-family',
        ),
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            conftest.FamilyIDs.INVALID_FAMILY_ID,
            http.HTTPStatus.NOT_FOUND,
            id='invalid-family-id',
        ),
    ],
)
async def test_update_family_info(
        web_app_client,
        mock_all_api,
        pgsql,
        user_uid,
        family_id,
        expected_code,
):
    old_family_name = _get_family_name_from_db(pgsql, family_id)
    random_family_name = ''.join(
        (
            random.choice(string.ascii_letters + ' ')
            for _ in range(random.randint(1, 30))
        ),
    )
    response = await web_app_client.put(
        f'/4.0/family/v1/{family_id}/update',
        json={'name': random_family_name},
        headers={**IP_HEADER, 'X-Yandex-UID': user_uid},
    )
    assert response.status == expected_code
    new_family_name = _get_family_name_from_db(pgsql, family_id)

    if response.status == http.HTTPStatus.NO_CONTENT:
        assert new_family_name == random_family_name
        assert new_family_name != old_family_name
    else:
        assert old_family_name == new_family_name
        assert new_family_name != random_family_name


def _get_family_name_from_db(pgsql, family_id: str) -> Optional[str]:
    cursor: psycopg2.extensions.cursor = pgsql['family'].cursor()
    try:
        cursor.execute(
            'SELECT name from db_family.families WHERE family_id = %s;',
            (family_id,),
        )
        result = cursor.fetchall()

        if result and result[0]:
            return result[0][0]
        return None
    finally:
        cursor.close()
