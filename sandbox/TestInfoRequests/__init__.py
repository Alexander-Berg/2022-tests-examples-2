# -*- coding: utf-8 -*-

from sandbox.projects.common.search import components as sc
from sandbox.projects.common.search import bugbanner

from sandbox.projects.common.base_search_quality import info_requests
from sandbox.projects.common.base_search_quality import settings as bss

import sandbox.common.types.client as ctc


class TestInfoRequests(bugbanner.BugBannerTask):
    """
    **Описание**

        Тестирование базового поиска обстрелом
        `info-запросами <https://wiki.yandex-team.ru/JandeksPoisk/KachestvoPoiska/Info-zaprosy>`.
        После запуска теста происходит следующее:

        1. Запросы разделяются на несколько групп, чтобы быть запущенными в несколько потоков
        2. Запускается поиск
        3. Запускается в несколько потоков обстрел.
        4. Из каждого потока задаётся запрос, из полученного ответа берутся идентификаторы документов (параметр docs)
        5. Происходит обстрел инфо-запросами для каждого документа
        6. Если происходит ошибка, тест фейлится

    **Ресурсы**

        *Необходимые для запуска ресурсы и параметры*

        * Executable: бинарник базового, который необходимо протестировать.
        * Config: конфигурационный файл поиска
        * DB: база поиска
        * Queries: список запросов
        * Max documents: ограничение на количество запросов
    """

    type = 'TEST_INFO_REQUESTS'
    client_tags = ctc.Tag.Group.LINUX

    input_parameters = sc.DefaultBasesearchParams.params + info_requests.PARAMS

    execution_space = bss.RESERVED_SPACE

    def on_execute(self):
        self.add_bugbanner(bugbanner.Banners.WebBaseSearch)
        basesearch = sc.get_basesearch()
        info_requests.test_info_requests(basesearch)


__Task__ = TestInfoRequests
