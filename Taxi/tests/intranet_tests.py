# coding: utf-8

from business_models.intranet import ABC, IDM, Search, Wiki, datalens
import PIL
import getpass

USER = getpass.getuser()

token_key = 'st_token'

def idm_tests():
    idm = IDM(system='taxi-dwh-idm-integration')
    assert idm.role_info('44992945')['id'] == 44992945
    assert type(idm.roles_list(path='/new_geo/', type='active')) == list
    assert idm.role_request(path='greenplum_analyst/greenplum_schema_access/rw_snb_calltaxi',
                            group='198644').json()['error_code'] == 'CONFLICT'

def abc_tests():
    abc = ABC()
    assert abc.info('tableau-creators-taxi')['slug'] == 'tableau-creators-taxi'
    assert abc.slug_from_id('31883') == 'tableau-creators-taxi'
    assert abc.id_from_slug('tableau-creators-taxi') == 31883


def search_tests():
    """Поиск опционов что-то выдает. Выдача может отличаться в зависимости от доступов"""
    search = Search()
    assert len(search.make_search("Опционы", scope='stsearch', page_depth=1)) > 0


def wiki_tests():
    """У всех есть доступ на чтение личного кластера"""
    wiki = Wiki()
    link = '/users/{}'.format(USER)
    assert wiki.page_info('https://wiki.yandex-team.ru' + link)['url'] == link


def datalens_tests():
    assert datalens.get_dashboard_json('obbiex3ge6x8g')['entryId'] == 'obbiex3ge6x8g'
    assert type(datalens.get_dashboard_image('obbiex3ge6x8g', 'Вкладка 1')) == PIL.Image.Image
