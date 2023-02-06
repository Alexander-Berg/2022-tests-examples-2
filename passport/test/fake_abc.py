# -*- coding: utf-8 -*-

from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.vault.api.builders.abc import ABC


class FakeABC(BaseFakeBuilder):
    def __init__(self):
        super(FakeABC, self).__init__(ABC)

    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):  # pragma: no cover
        if 'services/members' in url:
            return 'get_all_persons'
        if 'resources/consumers' in url:
            return 'get_all_tvm_apps'
        if 'v4/roles' in url:
            return 'get_all_roles'
        return 'get_all_departments'


TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE = {
    'next': None,
    'previous': None,
    'results': [
        {'id': 2, 'name': {'ru': u'Главная страница (Морда)', 'en': 'Portal'}, 'slug': 'home'},
        {'id': 6, 'name': {'ru': u'Мобильная Морда', 'en': 'Portal Mobile'}, 'slug': 'mobile'},
        {'id': 8, 'name': {'ru': u'Определялка мобильных телефонов', 'en': u'Определялка мобильных телефонов'},
         'slug': 'phonedetect'},
        {'id': 11, 'name': {'ru': u'Промо-сайт mobile.yandex.ru', 'en': u'Промо-сайт mobile.yandex.ru'},
         'slug': 'mobileyandex'},
        {'id': 14, 'name': {'ru': u'Паспорт', 'en': 'Passport'}, 'slug': 'passp'},
        {'id': 16, 'name': {'ru': u'LBS', 'en': 'LBS'}, 'slug': 'lbs'},
        {'id': 17, 'name': {'ru': u'Танкер', 'en': 'Tanker'}, 'slug': 'tanker'},
        {'id': 20, 'name': {'ru': u'Статистика по порталу (stat.yandex.ru)', 'en': 'stat.yandex.ru'}, 'slug': 'stat'},
        {'id': 22, 'name': {'ru': u'Настройка портала', 'en': 'Portal tuning'}, 'slug': 'custom'},
        {'id': 25, 'name': {'ru': u'Качество поиска', 'en': u'Качество поиска'}, 'slug': 'search-quality'},
        {'id': 26, 'name': {'ru': u'Веб-ранжирование', 'en': u'Веб-ранжирование'}, 'slug': 'buki'},
        {'id': 28, 'name': {'ru': u'Веб-сниппеты', 'en': 'Web-snippets'}, 'slug': 'snippets'},
        {'id': 29, 'name': {'ru': u'Подготовка данных для поиска', 'en': 'Search Content'}, 'slug': 'searchcontent'},
        {'id': 36, 'name': {'ru': 'Zora', 'en': 'Zora'}, 'slug': 'fetcher'},
        {'id': 37, 'name': {'ru': u'Навигационный источник', 'en': 'NAVSRC'}, 'slug': 'specprojects'},
        {'id': 38, 'name': {'ru': u'Свежесть', 'en': 'Freshness'}, 'slug': 'rearr'},
        {'id': 40, 'name': {'ru': u'SRE поиска', 'en': 'Runtime search SRE'}, 'slug': 'sepe'},
        {'id': 41, 'name': {'ru': 'YASM', 'en': 'YASM'}, 'slug': 'golovan'},
        {'id': 45, 'name': {'ru': u'Выдача поиска (SERP)', 'en': u'Выдача поиска (SERP)'}, 'slug': 'serp'},
        {'id': 50, 'name': {'ru': u'Перевод саджеста', 'en': 'Suggest'}, 'slug': 'suggest'},
    ]
}

TEST_ABC_GET_ALL_ROLES_RESPONSE = {
    'next': None,
    'previous': None,
    'results': [
        {u'code': u'product_head',
         u'created_at': u'2012-05-04T16:51:20Z',
         u'id': 1,
         u'name': {u'en': u'Head of product',
                   u'ru': u'\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u0441\u0435\u0440\u0432\u0438\u0441\u0430'},
         u'scope': {u'id': 1,
                    u'name': {u'en': u'Service management',
                              u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u043c'},
                    u'protected': False,
                    u'slug': u'services_management'},
         u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 2,
            u'name': {u'en': u'Project manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432'},
            u'scope': {u'id': 2,
                       u'name': {u'en': u'Project management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'projects_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 3,
            u'name': {u'en': u'Content manager ',
                      u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442-\u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 4,
            u'name': {u'en': u'Analyst',
                      u'ru': u'\u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a'},
            u'scope': {u'id': 3,
                       u'name': {u'en': u'Analitics',
                                 u'ru': u'\u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'analitics'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 5,
            u'name': {u'en': u'Marketing manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u043c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433\u0443'},
            u'scope': {u'id': 10,
                       u'name': {u'en': u'Marketing and advertising',
                                 u'ru': u'\u041c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433 \u0438 \u0440\u0435\u043a\u043b\u0430\u043c\u0430'},
                       u'protected': False,
                       u'slug': u'marketing'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 6,
            u'name': {u'en': u'Advertising manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u0440\u0435\u043a\u043b\u0430\u043c\u0435'},
            u'scope': {u'id': 10,
                       u'name': {u'en': u'Marketing and advertising',
                                 u'ru': u'\u041c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433 \u0438 \u0440\u0435\u043a\u043b\u0430\u043c\u0430'},
                       u'protected': False,
                       u'slug': u'marketing'},
            u'service': None},
        {u'code': u'developer',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 8,
            u'name': {u'en': u'Developer',
                      u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a'},
            u'scope': {u'id': 5,
                       u'name': {u'en': u'Development',
                                 u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'development'},
            u'service': None},
        {u'code': u'frontend_developer',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 11,
            u'name': {u'en': u'Frontend developer',
                      u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u043e\u0432'},
            u'scope': {u'id': 5,
                       u'name': {u'en': u'Development',
                                 u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'development'},
            u'service': None},
        {u'code': u'designer',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 13,
            u'name': {u'en': u'Designer',
                      u'ru': u'\u0414\u0438\u0437\u0430\u0439\u043d\u0435\u0440'},
            u'scope': {u'id': 4,
                       u'name': {u'en': u'Design', u'ru': u'\u0414\u0438\u0437\u0430\u0439\u043d'},
                       u'protected': False,
                       u'slug': u'design'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 14,
            u'name': {u'en': u'Interface researcher',
                      u'ru': u'\u0418\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u043e\u0432'},
            u'scope': {u'id': 4,
                       u'name': {u'en': u'Design', u'ru': u'\u0414\u0438\u0437\u0430\u0439\u043d'},
                       u'protected': False,
                       u'slug': u'design'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 16,
            u'name': {u'en': u'System administrator',
                      u'ru': u'\u0421\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0439 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440'},
            u'scope': {u'id': 8,
                       u'name': {u'en': u'Administration',
                                 u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'administration'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 17,
            u'name': {u'en': u'Database administrator',
                      u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u0431\u0430\u0437 \u0434\u0430\u043d\u043d\u044b\u0445'},
            u'scope': {u'id': 8,
                       u'name': {u'en': u'Administration',
                                 u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'administration'},
            u'service': None},
        {u'code': u'functional_tester',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 19,
            u'name': {u'en': u'Functional tester',
                      u'ru': u'\u0424\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0449\u0438\u043a'},
            u'scope': {u'id': 6,
                       u'name': {u'en': u'Testing',
                                 u'ru': u'\u0422\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'testing'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 21,
            u'name': {u'en': u'Load tester',
                      u'ru': u'\u041d\u0430\u0433\u0440\u0443\u0437\u043e\u0447\u043d\u044b\u0439 \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0449\u0438\u043a'},
            u'scope': {u'id': 6,
                       u'name': {u'en': u'Testing',
                                 u'ru': u'\u0422\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'testing'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 22,
            u'name': {u'en': u'Technical writer',
                      u'ru': u'\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043f\u0438\u0441\u0430\u0442\u0435\u043b\u044c'},
            u'scope': {u'id': 7,
                       u'name': {u'en': u'Support',
                                 u'ru': u'\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'support'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 24,
            u'name': {u'en': u'Support specialist',
                      u'ru': u'\u0421\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a \u0441\u043b\u0443\u0436\u0431\u044b \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438'},
            u'scope': {u'id': 7,
                       u'name': {u'en': u'Support',
                                 u'ru': u'\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'support'},
            u'service': None},
        {u'code': u'consultant',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 25,
            u'name': {u'en': u'Consultant',
                      u'ru': u'\u041a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 26,
            u'name': {u'en': u'Partner relationship manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 \u0441 \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430\u043c\u0438'},
            u'scope': {u'id': 11,
                       u'name': {u'en': u'Sales management',
                                 u'ru': u'\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044b'},
                       u'protected': False,
                       u'slug': u'sales_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-04T16:51:20Z',
            u'id': 27,
            u'name': {u'en': u'Sales manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0430\u043c'},
            u'scope': {u'id': 11,
                       u'name': {u'en': u'Sales management',
                                 u'ru': u'\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044b'},
                       u'protected': False,
                       u'slug': u'sales_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 28,
            u'name': {u'en': u'Undefined role',
                      u'ru': u'\u0420\u043e\u043b\u044c \u043d\u0435 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0430'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 29,
            u'name': {u'en': u'Administrator of assessors',
                      u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u0430\u0441\u0441\u0435\u0441\u0441\u043e\u0440\u043e\u0432'},
            u'scope': {u'id': 3,
                       u'name': {u'en': u'Analitics',
                                 u'ru': u'\u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'analitics'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 30,
            u'name': {u'en': u'Videographer',
                      u'ru': u'\u0412\u0438\u0434\u0435\u043e\u043e\u043f\u0435\u0440\u0430\u0442\u043e\u0440'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 31,
            u'name': {u'en': u'Cartographer',
                      u'ru': u'\u041a\u0430\u0440\u0442\u043e\u0433\u0440\u0430\u0444'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 32,
            u'name': {u'en': u'Leading cartographer',
                      u'ru': u'\u0412\u0435\u0434\u0443\u0449\u0438\u0439 \u043a\u0430\u0440\u0442\u043e\u0433\u0440\u0430\u0444'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2012-05-22T17:35:11Z',
            u'id': 33,
            u'name': {u'en': u'Senior cartographer',
                      u'ru': u'\u0413\u043b\u0430\u0432\u043d\u044b\u0439 \u043a\u0430\u0440\u0442\u043e\u0433\u0440\u0430\u0444'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-03-14T18:41:22Z',
            u'id': 34,
            u'name': {u'en': u'Content Project Manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043d\u044b\u0445 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432'},
            u'scope': {u'id': 2,
                       u'name': {u'en': u'Project management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'projects_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-05-23T12:11:52Z',
            u'id': 35,
            u'name': {u'en': u'Product manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u0430'},
            u'scope': {u'id': 1,
                       u'name': {u'en': u'Service management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u043c'},
                       u'protected': False,
                       u'slug': u'services_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-05-23T12:24:58Z',
            u'id': 36,
            u'name': {u'en': u'Lawyer', u'ru': u'\u042e\u0440\u0438\u0441\u0442'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-05-23T12:28:34Z',
            u'id': 37,
            u'name': {u'en': u'Mobile interface developer',
                      u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a '
                             u'\u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0445 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u043e\u0432'},
            u'scope': {u'id': 5,
                       u'name': {u'en': u'Development',
                                 u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'development'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-05-23T12:36:15Z',
            u'id': 38,
            u'name': {u'en': u'Server component developer',
                      u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a '
                             u'\u0441\u0435\u0440\u0432\u0435\u0440\u043d\u044b\u0445 \u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442'},
            u'scope': {u'id': 5,
                       u'name': {u'en': u'Development',
                                 u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'development'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-09-18T06:24:21Z',
            u'id': 39,
            u'name': {u'en': u'Security consultant',
                      u'ru': u'\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 '
                             u'\u043f\u043e \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u043e\u043d\u043d\u043e'
                             u'\u0439 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438'},
            u'scope': {u'id': 8,
                       u'name': {u'en': u'Administration',
                                 u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'administration'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2013-11-21T06:49:53Z',
            u'id': 40,
            u'name': {u'en': u'Editor',
                      u'ru': u'\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-01-17T07:31:58Z',
            u'id': 41,
            u'name': {u'en': u'Speaker',
                      u'ru': u'\u0414\u043e\u043a\u043b\u0430\u0434\u0447\u0438\u043a'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-01-17T16:46:30Z',
            u'id': 42,
            u'name': {u'en': u'Photographer',
                      u'ru': u'\u0424\u043e\u0442\u043e\u0433\u0440\u0430\u0444'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-01-17T16:47:32Z',
            u'id': 43,
            u'name': {u'en': u'Author',
                      u'ru': u'\u0410\u0432\u0442\u043e\u0440 \u0441\u0442\u0430\u0442\u044c\u0438'},
            u'scope': {u'id': 9,
                       u'name': {u'en': u'Content',
                                 u'ru': u'\u041a\u043e\u043d\u0442\u0435\u043d\u0442'},
                       u'protected': False,
                       u'slug': u'content'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-08-25T12:34:23Z',
            u'id': 44,
            u'name': {u'en': u'DC infrastructure IT specialist',
                      u'ru': u'\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 IT \u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b \u0414\u0426'},
            u'scope': {u'id': 7,
                       u'name': {u'en': u'Support',
                                 u'ru': u'\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'support'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-11-06T13:02:13Z',
            u'id': 45,
            u'name': {u'en': u'Autotest developer',
                      u'ru': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a \u0430\u0432\u0442\u043e\u0442\u0435\u0441\u0442\u043e\u0432'},
            u'scope': {u'id': 6,
                       u'name': {u'en': u'Testing',
                                 u'ru': u'\u0422\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'testing'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2014-11-26T10:09:35Z',
            u'id': 46,
            u'name': {u'en': u'Architect',
                      u'ru': u'\u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u043e\u0440'},
            u'scope': {u'id': 6,
                       u'name': {u'en': u'Testing',
                                 u'ru': u'\u0422\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'testing'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2015-03-04T11:42:34Z',
            u'id': 47,
            u'name': {u'en': u'Moderator',
                      u'ru': u'\u041c\u043e\u0434\u0435\u0440\u0430\u0442\u043e\u0440'},
            u'scope': {u'id': 7,
                       u'name': {u'en': u'Support',
                                 u'ru': u'\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'support'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2015-03-04T11:43:58Z',
            u'id': 48,
            u'name': {u'en': u'Secretary',
                      u'ru': u'\u0421\u0435\u043a\u0440\u0435\u0442\u0430\u0440\u044c'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2015-04-06T10:02:46Z',
            u'id': 49,
            u'name': {u'en': u'Category manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439'},
            u'scope': {u'id': 11,
                       u'name': {u'en': u'Sales management',
                                 u'ru': u'\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044b'},
                       u'protected': False,
                       u'slug': u'sales_management'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2015-04-06T10:03:33Z',
            u'id': 50,
            u'name': {u'en': u'Quality manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0443'},
            u'scope': {u'id': 12,
                       u'name': {u'en': u'Quality management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u043e\u043c'},
                       u'protected': False,
                       u'slug': u'quality_management'},
            u'service': None},
        {u'code': u'product_manager',
            u'created_at': u'2015-06-16T10:27:32Z',
            u'id': 51,
            u'name': {u'en': u'Service manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0441\u0435\u0440\u0432\u0438\u0441\u0430'},
            u'scope': {u'id': 1,
                       u'name': {u'en': u'Service management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u043c'},
                       u'protected': False,
                       u'slug': u'services_management'},
            u'service': None},
        {u'code': u'product_deputy_head',
            u'created_at': u'2015-08-05T12:12:51Z',
            u'id': 52,
            u'name': {u'en': u'Deputy head of product',
                      u'ru': u'\u0417\u0430\u043c\u0435\u0441\u0442\u0438\u0442\u0435\u043b\u044c '
                             u'\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044f \u0441\u0435\u0440\u0432\u0438\u0441\u0430'},
            u'scope': {u'id': 1,
                       u'name': {u'en': u'Service management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 '
                                 u'\u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u043c'},
                       u'protected': False,
                       u'slug': u'services_management'},
            u'service': None},
        {u'code': u'helpdesk',
            u'created_at': u'2015-09-21T10:32:02Z',
            u'id': 53,
            u'name': {u'en': u'Office infrastructure IT specialist',
                      u'ru': u'\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 IT '
                             u'\u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b '
                             u'\u043e\u0444\u0438\u0441\u043e\u0432'},
            u'scope': {u'id': 7,
                       u'name': {u'en': u'Support',
                                 u'ru': u'\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'},
                       u'protected': False,
                       u'slug': u'support'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2016-06-27T08:41:08Z',
            u'id': 161,
            u'name': {u'en': u'HR-partner',
                      u'ru': u'HR-\u043f\u0430\u0440\u0442\u043d\u0451\u0440'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2016-07-26T11:06:18Z',
            u'id': 181,
            u'name': {u'en': u'Approver',
                      u'ru': u'\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044e\u0449\u0438\u0439'},
            u'scope': {u'id': 13,
                       u'name': {u'en': u'Other roles',
                                 u'ru': u'\u0414\u0440\u0443\u0433\u0438\u0435 \u0440\u043e\u043b\u0438'},
                       u'protected': False,
                       u'slug': u'other'},
            u'service': None},
        {u'code': u'robot',
            u'created_at': u'2017-05-19T06:25:49Z',
            u'id': 383,
            u'name': {u'en': u'Robot', u'ru': u'\u0420\u043e\u0431\u043e\u0442'},
            u'scope': {u'id': 14,
                       u'name': {u'en': u'Virtual',
                                 u'ru': u'\u0412\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0435 '
                                 u'\u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438'},
                       u'protected': False,
                       u'slug': u'virtual'},
            u'service': None},
        {u'code': u'duty',
            u'created_at': u'2017-08-11T13:37:01.853740Z',
            u'id': 413,
            u'name': {u'en': u'Duty',
                      u'ru': u'\u0414\u0435\u0436\u0443\u0440\u043d\u044b\u0439'},
            u'scope': {u'id': 16,
                       u'name': {u'en': u'Duty work',
                                 u'ru': u'\u0414\u0435\u0436\u0443\u0440\u0441\u0442\u0432\u043e'},
                       u'protected': False,
                       u'slug': u'dutywork'},
            u'service': None},
        {u'code': u'other',
            u'created_at': u'2017-10-30T18:54:18.349053Z',
            u'id': 556,
            u'name': {u'en': u'Virtual user (passp)',
                      u'ru': u'\u0412\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a (passp)'},
            u'scope': {u'id': 14,
                       u'name': {u'en': u'Virtual',
                                 u'ru': u'\u0412\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0435 \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438'},
                       u'protected': False,
                       u'slug': u'virtual'},
            u'service': {u'id': 14,
                         u'name': {u'en': u'Passport',
                                   u'ru': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442'},
                         u'parent': 848,
                         u'slug': u'passp'}},
        {u'code': u'l3_responsible',
            u'created_at': u'2018-01-22T11:04:35.969495Z',
            u'id': 700,
            u'name': {u'en': u'L3 responsible',
                      u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0437\u0430 L3'},
            u'scope': {u'id': 50,
                       u'name': {u'en': u'Resources responsible',
                                 u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0435 '
                                 u'\u0437\u0430 \u0440\u0435\u0441\u0443\u0440\u0441\u044b'},
                       u'protected': True,
                       u'slug': u'resources_responsible'},
            u'service': None},
        {u'code': u'hardware_resources_manager',
            u'created_at': u'2018-03-13T16:49:37.657933Z',
            u'id': 742,
            u'name': {u'en': u'Hardware resources manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 '
                             u'\u0430\u043f\u043f\u0430\u0440\u0430\u0442\u043d\u044b\u0445 \u0440\u0435\u0441\u0443\u0440\u0441\u043e\u0432'},
            u'scope': {u'id': 51,
                       u'name': {u'en': u'Hardware management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0436\u0435\u043b\u0435\u0437\u043e\u043c'},
                       u'protected': True,
                       u'slug': u'hardware_management'},
            u'service': None},
        {u'code': u'responsible',
            u'created_at': u'2018-06-28T13:52:36.040762Z',
            u'id': 830,
            u'name': {u'en': u'Responsible',
                      u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u0439'},
            u'scope': {u'id': 1,
                       u'name': {u'en': u'Service management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u043c'},
                       u'protected': False,
                       u'slug': u'services_management'},
            u'service': None},
        {u'code': u'certs-resp',
            u'created_at': u'2018-08-30T12:21:59.175025Z',
            u'id': 960,
            u'name': {u'en': u'Certificates responsibe',
                      u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0437\u0430 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442'},
            u'scope': {u'id': 85,
                       u'name': {u'en': u'Certificate management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'cert'},
            u'service': None},
        {u'code': u'xiva_manager',
            u'created_at': u'2018-09-07T16:29:21.598505Z',
            u'id': 967,
            u'name': {u'en': u'Xiva manager',
                      u'ru': u'\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 Xiva'},
            u'scope': {u'id': 50,
                       u'name': {u'en': u'Resources responsible',
                                 u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0435 \u0437\u0430 \u0440\u0435\u0441\u0443\u0440\u0441\u044b'},
                       u'protected': True,
                       u'slug': u'resources_responsible'},
            u'service': None},
        {u'code': u'devops',
            u'created_at': u'2018-12-05T09:49:03.748844Z',
            u'id': 1097,
            u'name': {u'en': u'DevOps', u'ru': u'DevOps'},
            u'scope': {u'id': 84,
                       u'name': {u'en': u'DevOps', u'ru': u'DevOps'},
                       u'protected': True,
                       u'slug': u'devops'},
            u'service': None},
        {u'code': u'mdb_admin',
            u'created_at': u'2019-02-14T15:07:53.408801Z',
            u'id': 1258,
            u'name': {u'en': u'MDB admin',
                      u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 MDB'},
            u'scope': {u'id': 86,
                       u'name': {u'en': u'DB Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0431\u0430\u0437\u0430\u043c\u0438 \u0434\u0430\u043d\u043d\u044b\u0445'},
                       u'protected': True,
                       u'slug': u'db_management'},
            u'service': None},
        {u'code': u'mdb_viewer',
            u'created_at': u'2019-02-14T15:08:28.879529Z',
            u'id': 1259,
            u'name': {u'en': u'MDB viewer',
                      u'ru': u'\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c MDB'},
            u'scope': {u'id': 86,
                       u'name': {u'en': u'DB Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0431\u0430\u0437\u0430\u043c\u0438 \u0434\u0430\u043d\u043d\u044b\u0445'},
                       u'protected': True,
                       u'slug': u'db_management'},
            u'service': None},
        {u'code': u'robots_manager',
            u'created_at': u'2019-02-15T11:32:15.918949Z',
            u'id': 1260,
            u'name': {u'en': u'Robots manager',
                      u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u0439 \u0440\u043e\u0431\u043e\u0442\u0430\u043c\u0438'},
            u'scope': {u'id': 87,
                       u'name': {u'en': u'Robots management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0440\u043e\u0431\u043e\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'robots_management'},
            u'service': None},
        {u'code': u'robots_user',
            u'created_at': u'2019-02-15T11:32:39.146717Z',
            u'id': 1261,
            u'name': {u'en': u'Robots user',
                      u'ru': u'\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0440\u043e\u0431\u043e\u0442\u043e\u0432'},
            u'scope': {u'id': 87,
                       u'name': {u'en': u'Robots management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0440\u043e\u0431\u043e\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'robots_management'},
            u'service': None},
        {u'code': u'maintenance_manager',
            u'created_at': u'2019-03-25T11:15:22.868228Z',
            u'id': 1369,
            u'name': {u'en': u'Maintenance manager',
                      u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 '
                             u'\u0437\u0430 \u0440\u0435\u0433\u043b\u0430\u043c\u0435\u043d\u0442\u043d\u044b\u0435 '
                             u'\u0440\u0430\u0431\u043e\u0442\u044b'},
            u'scope': {u'id': 8,
                       u'name': {u'en': u'Administration',
                                 u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'},
                       u'protected': False,
                       u'slug': u'administration'},
            u'service': None},
        {u'code': u'quotas_manager',
            u'created_at': u'2019-06-04T20:49:23.238181Z',
            u'id': 1553,
            u'name': {u'en': u'Quotas manager',
                      u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u0439 \u043a\u0432\u043e\u0442\u0430\u043c\u0438'},
            u'scope': {u'id': 90,
                       u'name': {u'en': u'Quotas Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0432\u043e\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'quotas_management'},
            u'service': None},
        {u'code': u'mdb_admin_inheritance',
            u'created_at': u'2019-06-06T17:57:43.424854Z',
            u'id': 1563,
            u'name': {u'en': u'MDB admin with inheritance',
                      u'ru': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 MDB '
                             u'\u0441 \u043d\u0430\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u0435\u043c'},
            u'scope': {u'id': 86,
                       u'name': {u'en': u'DB Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0431\u0430\u0437\u0430\u043c\u0438 \u0434\u0430\u043d\u043d\u044b\u0445'},
                       u'protected': True,
                       u'slug': u'db_management'},
            u'service': None},
        {u'code': u'qyp_user',
            u'created_at': u'2019-06-17T08:35:14.608876Z',
            u'id': 1586,
            u'name': {u'en': u'QYP User',
                      u'ru': u'\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c QYP'},
            u'scope': {u'id': 90,
                       u'name': {u'en': u'Quotas Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0432\u043e\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'quotas_management'},
            u'service': None},
        {u'code': u'responsible_for_duty',
            u'created_at': u'2019-07-11T07:45:53.957187Z',
            u'id': 1735,
            u'name': {u'en': u'Duty Manager',
                      u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u0439 \u0434\u0435\u0436\u0443\u0440\u0441\u0442\u0432\u0430\u043c\u0438'},
            u'scope': {u'id': 16,
                       u'name': {u'en': u'Duty work',
                                 u'ru': u'\u0414\u0435\u0436\u0443\u0440\u0441\u0442\u0432\u043e'},
                       u'protected': False,
                       u'slug': u'dutywork'},
            u'service': None},
        {u'code': u'capacity_planner',
            u'created_at': u'2019-08-08T09:23:20.479350Z',
            u'id': 1796,
            u'name': {u'en': u'Capacity Planning Manager',
                      u'ru': u'\u041e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0437\u0430 Capacity Planning'},
            u'scope': {u'id': 90,
                       u'name': {u'en': u'Quotas Management',
                                 u'ru': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0432\u043e\u0442\u0430\u043c\u0438'},
                       u'protected': False,
                       u'slug': u'quotas_management'},
            u'service': None}
    ],
}

TEST_ABC_EMPTY_RESPONSE = {
    'next': None,
    'previous': None,
    'results': [],
}

TEST_ABC_GET_ALL_PERSONS_RESPONSE = {
    'next': None,
    'previous': None,
    'results': [
        {
            'id': 23383,
            'state': u'approved',
            'person': {
                'id': 18489,
                'login': u'ppodolsky',
                'first_name': u'Паша',
                'last_name': u'Переведенцев',
                'uid': u'1120000000038274',
            },
            'service': {
                'id': 14,
                'slug': u'passp',
                'name': {
                    'ru': u'Паспорт',
                    'en': u'Passport',
                },
                'parent': 848,
            },
            'role': {
                'id': 8,
                'name': {
                    'ru': u'Разработчик',
                    'en': u'Developer',
                },
                'service': None,
                'scope': {
                    'id': 5,
                    'slug': u'development',
                    'name': {
                        'ru': u'Разработка',
                        'en': u'Development',
                    },
                }, 'code': None,
            },
            'created_at': u'2016-02-25T18:02:26Z',
            'modified_at': u'2017-11-09T21:29:14.555202Z',
        },
        {
            'id': 56953,
            'person': {
                'id': 3645,
                'login': u'arhibot',
                'name': {
                    'ru': u'Дмитрий Ковега',
                    'en': u'Dmitry Kovega'
                },
                'first_name': {
                    'ru': u'Дмитрий',
                    'en': u'Dmitry'
                },
                'last_name': {
                    'ru': u'Ковега',
                    'en': u'Kovega'
                },
                'uid': u'1120000000005594',
                'department': 6465,
                'is_dismissed': False,
                'is_robot': False,
                'affiliation': u'yandex'
            },
            'service': {
                'id': 14,
                'slug': u'passp',
                'name': {
                    'ru': u'Паспорт',
                    'en': u'Passport'
                },
                'parent': 848
            },
            'role': {
                'id': 630,
                'name': {
                    'ru': u'TVM менеджер',
                    'en': u'TVM manager'
                },
                'service': None,
                'scope': {
                    'id': 17,
                    'slug': u'tvm_management',
                    'name': {
                        'ru': u'Управление TVM',
                        'en': u'TVM management'
                    }
                },
                'code': u'tvm_manager'
            },
            'created_at': u'2018-03-06T14:32:31.155756Z',
            'modified_at': u'2018-07-03T10:00:08.465702Z',
            'department_member': None
        },
        {
            u"id": 5583,
            u"person": {
                u"id": 1502,
                u"login": u"vsavenkov",
                u"name": {
                    u"ru": u"Владимир Савенков",
                    u"en": u"Vladimir Savenkov"
                },
                u"first_name": {
                    u"ru": u"Владимир",
                    u"en": u"Vladimir"
                },
                u"last_name": {
                    u"ru": u"Савенков",
                    u"en": u"Savenkov"
                },
                u"uid": u"1120000000000878",
                u"department": 1950,
                u"is_dismissed": False,
                u"is_robot": False,
                u"affiliation": u"yandex"
            },
            u"service": {
                u"id": 50,
                u"slug": u"suggest",
                u"name": {
                    u"ru": u"Саджест",
                    u"en": u"Suggest"
                },
                u"parent": 1380
            },
            u"role": {
                u"id": 8,
                u"name": {
                    u"ru": u"Разработчик",
                    u"en": u"Developer"
                },
                u"service": None,
                u"scope": {
                    u"id": 5,
                    u"slug": u"development",
                    u"name": {
                        u"ru": u"Разработка",
                        u"en": u"Development"
                    }
                },
                u"code": None
            },
            u"created_at": u"2012-05-02T07:17:57Z",
            u"modified_at": u"2018-05-04T10:04:38.145018Z",
            u"department_member": None
        },
        {
            u"id": 21658,
            u"person": {
                u"id": 16580,
                u"login": u"bykanov",
                u"name": {
                    u"ru": u"Владимир Быканов",
                    u"en": u"Vladimir Bykanov"
                },
                u"first_name": {
                    u"ru": u"Владимир",
                    u"en": u"Vladimir"
                },
                u"last_name": {
                    u"ru": u"Быканов",
                    u"en": u"Bykanov"
                },
                u"uid": u"1120000000027354",
                u"department": 1950,
                u"is_dismissed": False,
                u"is_robot": False,
                u"affiliation": u"yandex"
            },
            u"service": {
                u"id": 50,
                u"slug": u"suggest",
                u"name": {
                    u"ru": u"Саджест",
                    u"en": u"Suggest"
                },
                u"parent": 1380
            },
            u"role": {
                u"id": 16,
                u"name": {
                    u"ru": u"Системный администратор",
                    u"en": u"System administrator"
                },
                u"service": None,
                u"scope": {
                    u"id": 8,
                    u"slug": u"administration",
                    u"name": {
                        u"ru": u"Администрирование",
                        u"en": u"Administration"
                    }
                },
                u"code": None
            },
            u"created_at": u"2015-11-18T14:55:07Z",
            u"modified_at": u"2018-05-04T10:11:07.086252Z",
            u"department_member": None
        },
        {
            u"id": 33992,
            u"person": {
                u"id": 3229,
                u"login": u"alex-sh",
                u"name": {
                    u"ru": u"Алексей Шаграев",
                    u"en": u"Alexey Shagraev"
                },
                u"first_name": {
                    u"ru": u"Алексей",
                    u"en": u"Alexey"
                },
                u"last_name": {
                    u"ru": u"Шаграев",
                    u"en": u"Shagraev"
                },
                u"uid": u"1120000000004890",
                u"department": 1750,
                u"is_dismissed": False,
                u"is_robot": False,
                u"affiliation": u"yandex"
            },
            u"service": {
                u"id": 50,
                u"slug": u"suggest",
                u"name": {
                    u"ru": u"Саджест",
                    u"en": u"Suggest"
                },
                u"parent": 1380
            },
            u"role": {
                u"id": 8,
                u"name": {
                    u"ru": u"Разработчик",
                    u"en": u"Developer"
                },
                u"service": None,
                u"scope": {
                    u"id": 5,
                    u"slug": u"development",
                    u"name": {
                        u"ru": u"Разработка",
                        u"en": u"Development"
                    }
                },
                u"code": None
            },
            u"created_at": u"2017-04-14T09:12:16Z",
            u"modified_at": u"2018-05-04T10:20:45.997856Z",
            u"department_member": None
        },
        {
            u"id": 33993,
            u"person": {
                u"id": 1502,
                u"login": u"vsavenkov",
                u"name": {
                    u"ru": u"Владимир Савенков",
                    u"en": u"Vladimir Savenkov"
                },
                u"first_name": {
                    u"ru": u"Владимир",
                    u"en": u"Vladimir"
                },
                u"last_name": {
                    u"ru": u"Савенков",
                    u"en": u"Savenkov"
                },
                u"uid": u"1120000000000878",
                u"department": 1950,
                u"is_dismissed": False,
                u"is_robot": False,
                u"affiliation": u"yandex"
            },
            u"service": {
                u"id": 50,
                u"slug": u"suggest",
                u"name": {
                    u"ru": u"Саджест",
                    u"en": u"Suggest"
                },
                u"parent": 1380
            },
            u"role": {
                u"id": 16,
                u"name": {
                    u"ru": u"Системный администратор",
                    u"en": u"System administrator"
                },
                u"service": None,
                u"scope": {
                    u"id": 8,
                    u"slug": u"administration",
                    u"name": {
                        u"ru": u"Администрирование",
                        u"en": u"Administration"
                    }
                },
                u"code": None
            },
            u"created_at": u"2017-04-14T09:12:17Z",
            u"modified_at": u"2018-05-04T10:20:47.362244Z",
            u"department_member": None
        },
    ],
}

TEST_ABC_GET_ALL_TVM_APPS_RESPONSE = {
    u"next": None,
    u"previous": None,
    u"results": [
        {
            u"actions": [],
            u"id": 2446617,
            u"request_id": 66031,
            u"modified_at": u"2017-12-20T12:44:22.574130Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2163352,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"test_resource",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 1855,
                u"slug": u"glader_test_6",
                u"name": {
                    u"ru": u"glader_test_6",
                    u"en": u"glader_test_6"
                },
                u"parent": 842
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2451578,
            u"request_id": 67649,
            u"modified_at": u"2017-09-28T09:36:26.301182Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2164249,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"TestABC",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2451583,
            u"request_id": 67691,
            u"modified_at": u"2017-09-28T09:36:26.309265Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2164254,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"TestABC2",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2452202,
            u"request_id": None,
            u"modified_at": u"2017-10-20T12:39:18.680268Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2164692,
                u"external_id": u"2000196",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"TestABC2",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2452203,
            u"request_id": None,
            u"modified_at": u"2017-09-28T09:36:26.292424Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2164691,
                u"external_id": u"2000079",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"Паспорт [testing]",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2494555,
            u"request_id": 79632,
            u"modified_at": u"2017-10-12T16:39:41.897040Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2204560,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"TestABC3",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2494563,
            u"request_id": None,
            u"modified_at": u"2017-10-20T12:39:18.670993Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2204567,
                u"external_id": u"2000220",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"TestABC3",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2495930,
            u"request_id": 81777,
            u"modified_at": u"2017-10-18T13:39:48.168347Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2205410,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"push-client-passport",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2495931,
            u"request_id": None,
            u"modified_at": u"2017-10-18T13:39:48.163955Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2205411,
                u"external_id": u"2000230",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"push-client-passport",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2496518,
            u"request_id": 82496,
            u"modified_at": u"2017-10-19T14:39:41.731954Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2205582,
                u"external_id": None,
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"Sentry",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 795,
                u"slug": u"tools-sentry",
                u"name": {
                    u"ru": u"Sentry",
                    u"en": u"Sentry"
                },
                u"parent": 1937
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2496629,
            u"request_id": None,
            u"modified_at": u"2017-10-19T14:39:41.724027Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2205693,
                u"external_id": u"2000232",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"Sentry",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 795,
                u"slug": u"tools-sentry",
                u"name": {
                    u"ru": u"Sentry",
                    u"en": u"Sentry"
                },
                u"parent": 1937
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2514191,
            u"request_id": 116685,
            u"modified_at": u"2017-12-08T13:20:15.122708Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2214066,
                u"external_id": u"2000347",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"Тестовое твм приложение 3",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2514203,
            u"request_id": 116790,
            u"modified_at": u"2017-12-08T14:38:23.923194Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2214070,
                u"external_id": u"2000348",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"test_tvm25",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 1902,
                u"slug": u"gladertest7",
                u"name": {
                    u"ru": u"glader_test_7",
                    u"en": u"glader_test_7"
                },
                u"parent": 842
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [],
            u"id": 2515237,
            u"request_id": 117997,
            u"modified_at": u"2017-12-11T14:43:46.435564Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2214454,
                u"external_id": u"2000353",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"TestClientToBeDeleted",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"deprived",
            u"state_display": {
                u"ru": u"Отозван",
                u"en": u"Отозван"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2515251,
            u"request_id": 118060,
            u"modified_at": u"2017-12-11T15:25:57.104405Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2214468,
                u"external_id": u"2000354",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"Проверка создания TVM2",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2515443,
            u"request_id": 118385,
            u"modified_at": u"2018-03-06T14:33:51.838904Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2214524,
                u"external_id": u"2000355",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"passport_likers3",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": [
                {
                    u"id": 2,
                    u"name": {
                        u"ru": u"Продакшен",
                        u"en": u"Production"
                    },
                    u"slug": u"production",
                    u"type": u"internal",
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Окружение",
                            u"en": u"Environment"
                        },
                        u"slug": u"environment"
                    },
                    u"service": None,
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    }
                },
                {
                    u"id": 25,
                    u"name": {
                        u"ru": u"HistoryDB",
                        u"en": u"HistoryDB"
                    },
                    u"slug": u"historydb",
                    u"type": u"internal",
                    u"category": None,
                    u"service": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    }
                }
            ]
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2520867,
            u"request_id": 121540,
            u"modified_at": u"2017-12-15T10:23:01.904196Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2216446,
                u"external_id": u"2000367",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"social api (dev)",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 14,
                u"slug": u"passp",
                u"name": {
                    u"ru": u"Паспорт",
                    u"en": u"Passport"
                },
                u"parent": 848
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2520901,
            u"request_id": 121669,
            u"modified_at": u"2017-12-15T11:52:26.735109Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2216480,
                u"external_id": u"2000368",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"test-moodle",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 1931,
                u"slug": u"moodle",
                u"name": {
                    u"ru": u"Moodle",
                    u"en": u"Moodle"
                },
                u"parent": 907
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2520943,
            u"request_id": None,
            u"modified_at": u"2017-12-15T14:44:31.823102Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2216502,
                u"external_id": u"2000201",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": None,
                u"name": u"sandy-moodle-dev",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 1931,
                u"slug": u"moodle",
                u"name": {
                    u"ru": u"Moodle",
                    u"en": u"Moodle"
                },
                u"parent": 907
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        },
        {
            u"actions": [
                u"edit",
                u"meta_info",
                u"recreate_secret",
                u"restore_secret",
                u"delete_old_secret",
                u"delete"
            ],
            u"id": 2532799,
            u"request_id": 123071,
            u"modified_at": u"2017-12-18T16:02:08.459468Z",
            u"obsolete_id": None,
            u"resource": {
                u"id": 2216892,
                u"external_id": u"2000371",
                u"type": {
                    u"category": {
                        u"id": 1,
                        u"name": {
                            u"ru": u"Безопасность",
                            u"en": u"Security"
                        },
                        u"slug": u"security",
                        u"description": u""
                    },
                    u"description": {
                        u"ru": u"",
                        u"en": u""
                    },
                    u"form_link": u"https://forms.yandex-team.ru/surveys/2669/",
                    u"has_editable_tags": False,
                    u"has_multiple_consumers": False,
                    u"has_supplier_tags": False,
                    u"has_tags": True,
                    u"id": 47,
                    u"is_enabled": True,
                    u"is_important": False,
                    u"name": {
                        u"ru": u"TVM приложение",
                        u"en": u"TVM приложение"
                    },
                    u"supplier": {
                        u"id": 14,
                        u"slug": u"passp",
                        u"name": {
                            u"ru": u"Паспорт",
                            u"en": u"Passport"
                        },
                        u"parent": 848
                    },
                    u"tags": [],
                    u"usage_tag": None,
                    u"dependencies": [
                        {
                            u"id": 50,
                            u"name": u"HistoryDB API",
                            u"supplier": {
                                u"id": 14,
                                u"slug": u"passp",
                                u"name": {
                                    u"ru": u"Паспорт",
                                    u"en": u"Passport"
                                },
                                u"parent": 848
                            }
                        }
                    ]
                },
                u"link": u"",
                u"name": u"Test app",
                u"parent": None,
                u"attributes": [],
                u"obsolete_id": None
            },
            u"service": {
                u"id": 848,
                u"slug": u"authorization-and-security",
                u"name": {
                    u"ru": u"Авторизация и безопасность",
                    u"en": u"Authorization and security"
                },
                u"parent": 847
            },
            u"state": u"granted",
            u"state_display": {
                u"ru": u"Выдан",
                u"en": u"Выдан"
            },
            u"supplier_tags": [],
            u"tags": []
        }
    ]
}
