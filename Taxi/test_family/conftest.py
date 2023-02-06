# pylint: disable=redefined-outer-name
import aiohttp.web
import pytest

import family.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['family.generated.service.pytest_plugins']

BB_USERINFO_METHOD = 'userinfo'
BB_FAMILYINFO_METHOD = 'family_info'

DEFAULT_INVITE_ID = '3e673c95-bf28-4e4d-8253-3e2920f853e7'


class UserUIDs:
    NON_EXISTENT_UID = '100500'
    USER_WITHOUT_FAMILY = '0'
    USER_FAMILY_OWNER = '1'
    USER_FAMILY_MEMBER = '2'
    USER_FAMILY_OWNER_CANT_CREATE_INVITE = '3'


class UserPhoneIDs:
    USER_WITHOUT_INVITE = '00aaaaaaaaaaaaaaaaaaaa00'
    USER_FAMILY_MEMBER = '00aaaaaaaaaaaaaaaaaaaa01'
    USER_FAMILY_VALID_INVITE = '00aaaaaaaaaaaaaaaaaaaa02'


class Invites:
    INVALID_INVITE_ID = 'invalid_invite'
    VALID_INVITE_ID = 'valid_invite'


class FamilyIDs:
    VALID_FAMILY_ID = 'f1'
    INVALID_FAMILY_ID = 'g803'


@pytest.fixture
def mock_passport_api(mockserver, load_json):
    """ Passport API fixture. Help to return mocked user- and family- info.
    """

    def _mock_family_info(params: dict):
        bb_families = load_json('bb_family_info.json')
        bb_family = bb_families.get(params.get('family_id'))
        if not bb_family:
            return {'exception': {'value': 'error'}}
        return {'family': {params['family_id']: bb_family}}

    def _mock_userinfo(params: dict):
        bb_users = load_json('bb_user_info.json')
        bb_user = bb_users.get(params.get('uid'))
        if not bb_user:
            return {'exception': {'value': 'error'}}
        return {'users': [bb_user]}

    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_bb(request, **kwargs):
        method = request.query['method']
        if method == BB_USERINFO_METHOD:
            return _mock_userinfo(request.query)
        if method == BB_FAMILYINFO_METHOD:
            return _mock_family_info(request.query)
        raise Exception('Undefined bb method')


@pytest.fixture
def mock_passport_internal_api(mockserver):
    """ Internal Passport API fixture.
    """

    @mockserver.json_handler(
        '/passport-internal/1/bundle/family/issue_invite/',
    )
    def _mock_create_invite(request, **kwargs):
        """ Mock function for creating passport invites
        """
        if (
                request.form['uid']
                == UserUIDs.USER_FAMILY_OWNER_CANT_CREATE_INVITE
        ):
            return {'status': 'error', 'errors': ['family.max_capacity']}
        return {'status': 'ok', 'invite_id': DEFAULT_INVITE_ID}

    @mockserver.json_handler('/passport-internal/1/bundle/family/invite_info/')
    def _mock_get_invite(request, **kwargs):
        invite_id = request.form['invite_id']
        if invite_id == Invites.INVALID_INVITE_ID:
            return {'status': 'error', 'errors': ['family.invalid_invite']}
        return {'status': 'ok'}

    @mockserver.json_handler('/passport-internal/1/bundle/family/create/')
    def _mock_create_family(request, **kwargs):
        user_uid = request.form['uid']
        if user_uid == UserUIDs.USER_FAMILY_OWNER:
            return {'status': 'error', 'errors': ['family.already_exists']}
        return {'status': 'ok', 'family_id': 'f49491'}


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
                {
                    '_id': 'est',
                    'national_access_code': '372',
                    'phone_code': '372',
                    'phone_max_length': 11,
                    'phone_min_length': 10,
                },
            ],
        }


@pytest.fixture
def mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user_api-api/user_phones/by_number/retrieve')
    def _get_user_phone_id(request):
        return load_json('user_phones_by_phone.json').get(
            request.json['phone'], aiohttp.web.json_response(status=404),
        )


@pytest.fixture
def mock_all_api(
        mock_passport_api,
        mock_passport_internal_api,
        mock_territories_api,
        mock_user_api,
):
    pass
