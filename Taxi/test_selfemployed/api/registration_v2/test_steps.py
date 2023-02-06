import pytest

from test_selfemployed import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FILLING', 'external_id');
        """,
    ],
)
async def test_get_steps(se_client):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    response = await se_client.get(
        '/self-employment/fns-se/v2/steps',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'steps': [
            {
                'key': 'intro',
                'text': 'Получите статус самозанятого',
                'done': True,
                'visible_for_user': True,
                'previous_step': '_exit',
            },
            {
                'key': 'nalog_app',
                'text': 'Стать самозанятым',
                'done': True,
                'visible_for_user': True,
                'previous_step': 'intro',
                'title': '1 из 6',
            },
            {
                'key': 'phone_number',
                'text': 'Проверка номера',
                'done': True,
                'visible_for_user': False,
                'previous_step': 'nalog_app',
                'title': '1 из 6',
            },
            {
                'key': 'sms',
                'text': 'Код из СМС',
                'done': True,
                'visible_for_user': False,
                'previous_step': 'phone_number',
                'title': '1 из 6',
            },
            {
                'key': 'agreement',
                'text': 'Соглашение',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '2 из 6',
            },
            {
                'key': 'address',
                'text': 'Укажите адрес прописки',
                'done': False,
                'visible_for_user': True,
                'previous_step': 'agreement',
                'title': '3 из 6',
            },
            {
                'key': 'permission',
                'text': 'Свяжите профили',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '4 из 6',
            },
            {
                'key': 'await_own_park',
                'text': 'Потерпите',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '5 из 6',
            },
            {
                'key': 'requisites',
                'text': 'Укажите реквизиты',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '6 из 6',
            },
        ],
        'fns_package_name': 'com.gnivts.selfemployed',
        'fns_appstore_id': '1437518854',
        'current_step': 'agreement',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status)
        VALUES ('phone_pd_id', 'inn_pd_id', 'COMPLETED');
        INSERT INTO se.finished_profiles
            (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'phone_pd_id', 'inn_pd_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_get_steps_complete(se_client):
    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.get(
        '/self-employment/fns-se/v2/steps',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'steps': [
            {
                'key': 'requisites',
                'text': '',
                'done': False,
                'visible_for_user': True,
                'previous_step': '_exit',
                'title': '',
            },
        ],
        'fns_package_name': 'com.gnivts.selfemployed',
        'fns_appstore_id': '1437518854',
        'current_step': 'requisites',
    }
    print(content)


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_steps(se_client):
    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/steps',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'overview'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'nalog_app',
        'step_count': 7,
        'step_index': 1,
    }
