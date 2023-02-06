import os

from metrika.pylib.deploy import info


def test_am_i_in_deploy():
    os.environ['DEPLOY_PROJECT_ID'] = 'Awesome'
    assert info.am_i_in_deploy() is True

    os.environ.pop('DEPLOY_PROJECT_ID')
    assert info.am_i_in_deploy() is False


def test_get_deploy_info():
    environ = {
        'DEPLOY_PROJECT_ID': 'Awesome',
        'DEPLOY_BOX_ID': 'World',
    }
    os.environ.update(environ)

    deploy_info = info.get_deploy_info()

    assert deploy_info.project_id == 'Awesome'
    assert deploy_info.box_id == 'World'
