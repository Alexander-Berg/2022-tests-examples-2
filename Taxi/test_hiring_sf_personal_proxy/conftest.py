# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import random
import string
import uuid

import pytest

import hiring_sf_personal_proxy.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_sf_personal_proxy.generated.service.pytest_plugins']


def hex_uuid():
    return uuid.uuid4().hex


def _gen_string(length):
    res = ''.join(
        random.choices(string.ascii_uppercase + string.digits * 5, k=length),
    )
    return res


def gen_email():
    return 'email_{}@example.com'.format(_gen_string(random.randint(5, 15)))


def gen_license():
    return 'LIC{}'.format(_gen_string(10).upper())


def gen_phone():
    return '+79' + str(random.randint(10 ** 8, 10 ** 9 - 1))


@functools.lru_cache(None)
def personal_response(type_, id_):
    if type_ == 'license':
        value = gen_license()
    elif type_ == 'phone':
        value = gen_phone()
    else:
        value = gen_email()
    response = {'value': value, 'id': id_}
    return response


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def retrieve_phones(request):
        type_ = 'phone'
        return personal_response(type_, request.json['id'])

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def retrieve_emails(request):
        type_ = 'email'
        return personal_response(type_, request.json['id'])

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def retrieve_licenses(request):
        type_ = 'license'
        response = personal_response(type_, request.json['id'])
        return response

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def retrieve_phones_bulk(request):
        type_ = 'phone'
        items = []
        for item in request.json['items']:
            items.append(personal_response(type_, item['id']))
        return {'items': items}

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def retrieve_emails_bulk(request):
        type_ = 'email'
        items = []
        for item in request.json['items']:
            items.append(personal_response(type_, item['id']))
        return {'items': items}

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def retrieve_licenses_bulk(request):
        type_ = 'license'
        items = []
        for item in request.json['items']:
            items.append(personal_response(type_, item['id']))
        return {'items': items}


def mock_activity_check(driver_id):
    """
    Pretending that activity was checked
    :param driver_id:
    :return:
    """
    return '9' not in driver_id.split('_')[1]


@pytest.fixture  # noqa: F405
def hiring_candidates_py3(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/hiring-candidates-py3/v1/activity-check/bulk/drivers',
    )
    def activity_check(request):
        res = []
        for driver_id in request.json['driver_ids']:
            res.append(
                {
                    'driver_id': driver_id,
                    'is_active': mock_activity_check(driver_id),
                },
            )
        return {'driver_ids': res}


@pytest.fixture  # noqa: F405
def driver_profiles(mockserver, load_json):
    storage = load_json('driver-profiles-responses.json')

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_park_id',
    )
    def retrieve_by_park_id(request):
        ids = request.json['park_id_in_set']
        profiles = []
        for id_ in ids:
            if id_ in storage:
                profiles.append(storage[id_])
            else:
                profiles.append({'park_id': id_, 'profiles': []})
        data = {'profiles_by_park_id': profiles}
        return data


def main_configuration(func):
    @pytest.mark.config(  # noqa: F405
        TVM_RULES=[
            {'src': 'hiring-sf-personal-proxy', 'dst': 'personal'},
            {'src': 'hiring-sf-personal-proxy', 'dst': 'driver-profiles'},
            {'src': 'hiring-sf-personal-proxy', 'dst': 'hiring-candidates'},
        ],
    )
    @pytest.mark.usefixtures(  # noqa: F405
        'personal', 'driver_profiles', 'hiring_candidates_py3',
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched
