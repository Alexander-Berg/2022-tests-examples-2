import pytest

POSITION_MSK = {'lat': 55.735961, 'lon': 37.643216}


async def _find_profile(phone, passport_uid, mongo):
    search_expression = {'is_park_change': {'$exists': False}}
    if passport_uid:
        search_expression['passport_uid'] = passport_uid
    else:
        search_expression['phone_number'] = phone
        search_expression['passport_uid'] = {'$exists': False}
    return await mongo.selfreg_profiles.find_one(search_expression)


@pytest.mark.config(
    SELFREG_NEAREST_CITY_SUGGEST_OVERRIDES={'Московская область': 'Москва'},
)
@pytest.mark.parametrize(
    'phone_number, passport_uid, location, city_id, selfreg_login_type,'
    'profile_already_exists',
    [
        [
            '+70009325297',
            None,
            POSITION_MSK,
            'Санкт-Петербург',
            'selfreg',
            True,
        ],
        ['+70009325298', None, POSITION_MSK, 'Москва', 'selfreg', False],
        ['+70001112233', None, POSITION_MSK, 'Москва', 'selfreg', False],
        [
            '+70001112233',
            '1122334455',
            POSITION_MSK,
            'Москва',
            'selfreg',
            False,
        ],
        [
            '+70009325298',
            '1122334455',
            POSITION_MSK,
            'Москва',
            'selfreg',
            False,
        ],
        [
            '+70009325297',
            '1122334455',
            POSITION_MSK,
            'Москва',
            'selfreg',
            False,
        ],
        [
            '+70004445566',
            '5566778899',
            POSITION_MSK,
            'Санкт-Петербург',
            'selfreg',
            True,
        ],
        [
            '+70001112233',
            '5566778899',
            POSITION_MSK,
            'Санкт-Петербург',
            'selfreg',
            True,
        ],
        [
            '+70009325297',
            None,
            POSITION_MSK,
            'Санкт-Петербург',
            'selfreg_professions',
            True,
        ],
        [
            '+70009325298',
            None,
            POSITION_MSK,
            'Москва',
            'selfreg_professions',
            False,
        ],
        ['+70009325299', None, POSITION_MSK, 'Москва', None, False],
        ['+70009998877', None, POSITION_MSK, 'Москва', None, False],
    ],
)
async def test_new_profile(
        taxi_selfreg,
        mockserver,
        mongo,
        phone_number,
        passport_uid,
        location,
        city_id,
        profile_already_exists,
        selfreg_login_type,
):

    before_profile = await _find_profile(phone_number, passport_uid, mongo)
    if profile_already_exists:
        assert before_profile['city'] == city_id
        orig_token = before_profile['token']
        assert 'phone_pd_id' not in before_profile
    else:
        assert not before_profile

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _personal_phone_retrieve(request, *args, **kwargs):
        return {'id': 'phone_pd_id', 'value': phone_number}

    request = {'phone_pd_id': 'phone_pd_id', 'locale': 'ru', **POSITION_MSK}
    if passport_uid:
        request['passport_uid'] = passport_uid
    if selfreg_login_type is not None:
        request['selfreg_login_type'] = selfreg_login_type
    response = await taxi_selfreg.post(
        '/internal/selfreg/v1/login/', json=request,
    )
    assert response.status == 200
    content = await response.json()

    token = content['token']
    content.pop('token')
    assert content == {'city_id': city_id, 'country_id': 'rus'}

    mongo_entry = await _find_profile(phone_number, passport_uid, mongo)
    new_token = mongo_entry.pop('token')
    assert token == new_token
    if profile_already_exists:
        assert mongo_entry.pop('chosen_flow')
        assert new_token != orig_token
    else:
        step = mongo_entry.pop('registration_step')
        assert step == 'start'
    assert mongo_entry.pop('updated_ts')
    assert mongo_entry.pop('created_date')
    assert mongo_entry.pop('modified_date')
    assert mongo_entry.pop('_id')
    assert mongo_entry.pop('selfreg_version') == (
        'v3' if selfreg_login_type == 'selfreg_professions' else 'v2'
    )
    expected_entry = {
        'phone_number': phone_number,
        'phone_confirmed': True,
        'locale': 'ru',
        'city': city_id,
        'phone_pd_id': 'phone_pd_id',
    }
    if passport_uid:
        expected_entry['passport_uid'] = passport_uid
    assert mongo_entry == expected_entry
