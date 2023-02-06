

from app.api.v1.validators import validate_new_project_params
from app.db.db import new_session
from app.db.models import DebbyProject
from app.policies import create_policy
from app.projects import create_new_project
from app.projects.utils import create_projectapiinfo, get_project_info_by_id_and_api_src_id
from app.projects.utils import get_projects_by_api_src_id, delete_project_by_id_and_api_src_id
from app.validators import DebbyValidateException, DebbyRuntimeException, DebbyOwnerException

from app.settings import PROTO_TCP, API_PREFIX


def test_api_get_project_info():

    test_tvm_client_id = 0
    wrong_tvm_client_id = 1

    projects = get_projects_by_api_src_id(test_tvm_client_id)
    project_ids = list([p.get('id') for p in projects])
    s = new_session()
    s.query(DebbyProject).filter(DebbyProject.id.in_(project_ids)).delete(synchronize_session=False)
    s.commit()
    s.close()

    param_json = {
        'engine': 'nmap',
        'name': 'test_name',
        'targets': '5.255.255.5, ya.ru',
        'ports': '80, 81,82-84',
        'start_timestamp': None,
        'tags': ['AZURE'],
        'transport': PROTO_TCP,
        'additional_options': ''
    }

    params = validate_new_project_params(param_json)

    if not params.get('name').startswith(API_PREFIX):
        new_name = API_PREFIX + params.get('name')
    else:
        new_name = params.get('name')

    tag_list = list()
    for tag in params.get('tags_list'):
        if not tag.startswith(API_PREFIX):
            tag_list.append(API_PREFIX + tag)
        else:
            tag_list.append(tag)

    new_policy_id = create_policy(new_name, params.get('transport'), ports_list=params.get('ports_list'),
                                  additional_options=params.get('additional_options'))

    new_project_id = create_new_project(new_name, params.get('targets'), params.get('engine'), new_policy_id,
                                        params.get('start_timestamp'), params.get('stop_timestamp'),
                                        params.get('scan_interval'), tag_list, list())

    create_projectapiinfo(new_project_id, test_tvm_client_id)

    projects = get_projects_by_api_src_id(test_tvm_client_id)
    assert len(projects) == 1
    assert projects[0]['id'] == new_project_id

    try:
        get_project_info_by_id_and_api_src_id(new_project_id, wrong_tvm_client_id, 1, 1)
        assert False
    except DebbyOwnerException:
        assert True

    try:
        get_project_info_by_id_and_api_src_id(1111111111, test_tvm_client_id, 1, 1)
        assert False
    except DebbyRuntimeException:
        assert True

    project_info = get_project_info_by_id_and_api_src_id(new_project_id, test_tvm_client_id, 1, 1)
    assert project_info['name'] == new_name
    assert project_info['transport'] == params.get('transport')
    assert project_info['targets'] == params.get('targets')

    project_info = get_project_info_by_id_and_api_src_id(new_project_id, test_tvm_client_id, 1, 0)
    assert project_info.get('transport') is None

    project_info = get_project_info_by_id_and_api_src_id(new_project_id, test_tvm_client_id, 0, 0)
    assert project_info.get('targets') is None

    try:
        delete_project_by_id_and_api_src_id(new_project_id, test_tvm_client_id)
        assert True
    except DebbyRuntimeException:
        assert False

    try:
        delete_project_by_id_and_api_src_id(new_project_id, test_tvm_client_id)
        assert False
    except DebbyRuntimeException:
        assert True


def test_new_project_validator_valid():
    param_json = {
        'engine': 'nmap',
        'name': 'test_name',
        'targets': '5.255.255.5, ya.ru',
        'ports': '80, 81,82-84',
        'start_timestamp': None,
        'tags': ['AZURE'],
        'transport': PROTO_TCP,
        'additional_options': ''
    }

    try:
        res_json = validate_new_project_params(param_json)
    except DebbyValidateException as e:
        print(e.message)
        assert False

    assert res_json.get('additional_options') == param_json.get('additional_options')
    assert res_json.get('start_timestamp') is not None
    assert res_json.get('scan_interval') is not None
    assert res_json.get('stop_timestamp') is not None
    assert res_json.get('name') == param_json.get('name')
    assert res_json.get('tags') == param_json.get('tags_list')
    assert res_json.get('ports_list') == ['80', '81', '82-84']
    assert res_json.get('targets') == param_json.get('targets')
    assert res_json.get('transport') == param_json.get('transport')


def test_new_project_validator_ports():
    param_json = {
        'engine': 'nmap',
        'name': 'test_name',
        'targets': '5.255.255.5, ya.ru',
        'ports': '1, 2, e, 4',
        'start_timestamp': None,
        'tags': ['AZURE'],
        'transport': PROTO_TCP,
        'additional_options': ''
    }

    try:
        validate_new_project_params(param_json)
        assert False
    except DebbyValidateException:
        assert True

    param_json['ports'] = '1, 2, 4-11, 12-15-16'

    try:
        validate_new_project_params(param_json)
        assert False
    except DebbyValidateException:
        assert True

    param_json['ports'] = '1'

    try:
        validate_new_project_params(param_json)
        assert True
    except DebbyValidateException:
        assert False

    param_json['ports'] = ['1', '2']

    try:
        validate_new_project_params(param_json)
        assert False
    except DebbyValidateException:
        assert True

    param_json['ports'] = [1, 2]

    try:
        validate_new_project_params(param_json)
        assert False
    except DebbyValidateException:
        assert True
