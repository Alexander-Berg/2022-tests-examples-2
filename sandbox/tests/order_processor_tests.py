import logging
import re
import json
from mock import MagicMock
from library.python import resource
from sandbox.projects.yabs.auto_supbs_2.lib.order_processor_lib import OrderProcessor


def test_process_order_from_caesar():
    order_info = str(resource.find('sandbox/projects/yabs/auto_supbs_2/lib/order_processor_lib/tests/order.json'))
    ad_group_info = str(resource.find('sandbox/projects/yabs/auto_supbs_2/lib/order_processor_lib/tests/ad_group.json'))
    banner_1 = str(resource.find('sandbox/projects/yabs/auto_supbs_2/lib/order_processor_lib/tests/banner_1.json'))
    banner_2 = str(resource.find('sandbox/projects/yabs/auto_supbs_2/lib/order_processor_lib/tests/banner_2.json'))

    def get_entity_from_caesar(entity, entity_id, lookup_profile_dump_text):
        response = ''
        logging.warning(entity + str(entity_id))
        if entity == 'Order':
            response = order_info
        elif entity == 'AdGroup':
            response = ad_group_info
        elif entity == 'Banner':
            if entity_id == 72057605887880719:
                response = banner_1
            else:
                response = banner_2
        else:
            return dict()

        def repl(match):
            if match.group(1) == '\\':
                return "\\\\\\\\"
            return "\\\\" + match.group(1)

        response = re.sub("\\\\([^\"])", repl, response, flags=re.MULTILINE)

        return json.loads(response)

    def execute_yql_query(query_text):
        result = []
        if 'home/yabs/dict/Operation' in query_text:
            logging.warning('home/yabs/dict/Operation')
            result = [(20L, u'match goal context'), (9L, u'less or equal'), (1L, u'match'), (26L, u'not match name and version range'), (21L, u'match inner goal context'), (2L, u'like'),
                      (3L, u'regexp'), (25L, u'match name and version range'), (23L, u'check remainder'), (18L, u'time not like'), (12L, u'not like'), (11L, u'not match'), (16L, u'domain not like'),
                      (27L, u'not match goal context'), (10L, u'icase match'), (6L, u'greater'), (15L, u'domain like'), (8L, u'greater or equal'), (19L, u'bitwise and'), (5L, u'not equal'),
                      (7L, u'less'), (13L, u'not regexp'), (14L, u'icase not match'), (24L, u'negation of bitwise and'), (4L, u'equal'), (22L, u'time ignore holiday like'), (17L, u'time like')]

        elif 'home/yabs/dict/Keyword' in query_text:
            logging.warning('home/yabs/dict/Keyword')
            result = [(236L, u'Какой то вариант'), (77L, u'Region'), (1L, u'Imp'), (17L, u'Тестируем кодировку')]

        return result, 'https://yql.yandex-team.ru/Operations/6287a62497c5b749998a33ae'

    def get_banner_ids_by_order_id_at_link(link, order_id):
        if 'an.yandex.ru' in link:
            return set([u'72057605887880719']), set()
        elif 'yabs.yandex.ru' in link:
            return set([u'72057605887880720']), set([u'4849535312'])
        else:
            return set(), set()

    order_processor = OrderProcessor(
    '',  # sdk2.Vault.data(self.owner, self.Parameters.yt_token),
    '',  # self.Parameters.caesar_adgroups_path,
    '',  # sdk2.Vault.data(self.owner, 'ROBOT_AUTOSUPBS_YQL_TOKEN_TEMPORARY'),
    '',  # sdk2.Vault.data(self.owner, self.Parameters.charts_token),
    '2022-05-11',  # issue.start,
    '2022-05-13',  # issue.end,
    params='params'
        )

    order_processor.get_entity_from_caesar = get_entity_from_caesar
    order_processor._OrderProcessor__execute_yql_query = execute_yql_query
    order_processor.get_banner_ids_by_order_id_at_link = get_banner_ids_by_order_id_at_link
    # order_processor._OrderProcessor__execute_yql_query = MagicMock(return_value=[[72057605849547209, 4839344329, '2022-05-18']])

    messages, lookup_profile_dump_text = order_processor.process_order_from_caesar(
        order_id=172056991,
        task_id=123,
        max_entity_count=123
    )

    comment_text = '\n'.join(messages)  # Test decoding process. Keep this line BaseAutoSupBsIssueProcessor -> on_execute -> for comment in comments:

    logging.info(comment_text.decode('unicode-escape'))
    return comment_text.decode('unicode-escape')


def test__add_patterns_from_caesar():
    show_conditions_str = """
    {
        "ShowConditions": {
            "ContextID": 3594169837944405539,
            "Expression": {
                "and": [{
                        "or": [{
                            "operation": 1,
                            "keyword": 236,
                            "value": "542"
                        }]
                    },
                    {
                        "or": [{
                            "operation": 2,
                            "keyword": 1,
                            "value": "20044"
                        }, {
                            "operation": 4,
                            "keyword": 17,
                            "value": "47"
                        }, {
                            "operation": 5,
                            "keyword": 236,
                            "value": "972"
                        }]
                    }
                ]
            }
        }
    }
    """
    operations = {1: 'match', 2: 'like' , 3: 'regexp', 4: 'equal', 5: 'not equal', 6: 'greater', 7: 'less', 8: 'greater or equal', 9: 'less or equal', 11: 'not match', 18: 'time not like'}
    keywords = {236: 'Какой то вариант', 17: 'Region', 1: 'Imp'}

    for key in keywords:
        keywords[key] = keywords[key].decode('utf-8')
        logging.warning(keywords[key])

    def get_descriptions(query):
        if 'home/yabs/dict/Operation' in query:
            logging.warning('home/yabs/dict/Operation')
            return operations
        elif 'home/yabs/dict/Keyword' in query:
            logging.warning('home/yabs/dict/Keyword')
            return keywords
        else:
            return dict()

    order_processor = OrderProcessor(
    '',  # sdk2.Vault.data(self.owner, self.Parameters.yt_token),
    '',  # self.Parameters.caesar_adgroups_path,
    '',  # sdk2.Vault.data(self.owner, 'ROBOT_AUTOSUPBS_YQL_TOKEN_TEMPORARY'),
    '',  # sdk2.Vault.data(self.owner, self.Parameters.charts_token),
    '2022-05-11',  # issue.start,
    '2022-05-13',  # issue.end,
    params='params'
        )

    order_processor._OrderProcessor__get_descriptions = get_descriptions

    show_conditions = json.loads(show_conditions_str)
    patterns = order_processor._OrderProcessor__get_patterns_from_caesar([show_conditions['ShowConditions']])

    logging.info(patterns.decode('unicode-escape'))
    return patterns.decode('unicode-escape')


def test_process_order_genocide():
    def execute_yql_query(query_text):
        query_results = []
        if 'results_archive' in query_text:
            query_results = [[72057605849547209, 4839344329, [("2022-05-11T00:00:21", False, 0.14769844442106064), ("2022-05-12T10:05", True, 1), ("2022-05-12T14:35", False, 0.14)]],
                             [72057605849547208, 4839344328, [("2022-05-11T00:00:21", False, 0.14769844442106064), ("2022-05-12T10:05", False, 0.14769844442106064), ("2022-05-12T14:35", False, 0.1)]],
                             [72057605849547207, 4839344327, [("2022-05-11T00:00:21", True, 1), ("2022-05-12T10:05", True, 1), ("2022-05-12T14:35", True, 1)]]]
        elif 'genocide_results' in query_text:
            query_results = [[72057605849547209, 4839344329, '2022-05-18', 0.14769844442106064], [72057605849547207, 4839344327, '2022-05-17', 0.49]]

        return query_results, 'https://yql.yandex-team.ru/Operations/6287a62497c5b749998a33ae'

    order_processor = OrderProcessor(
    '',  # sdk2.Vault.data(self.owner, self.Parameters.yt_token),
    '',  # self.Parameters.caesar_adgroups_path,
    '',  # sdk2.Vault.data(self.owner, 'ROBOT_AUTOSUPBS_YQL_TOKEN_TEMPORARY'),
    '',  # sdk2.Vault.data(self.owner, self.Parameters.charts_token),
    '2022-05-11',  # issue.start,
    '2022-05-13',  # issue.end,
    params='params'
        )

    order_processor._OrderProcessor__execute_yql_query = execute_yql_query

    messages = order_processor.process_order_genocide(
        order_id=172056991,
        task_id=123,
        max_entity_count=123
    )

    comment_text = u'\n'.join(messages)  # Test decoding process. Keep this line BaseAutoSupBsIssueProcessor -> on_execute -> for comment in comments:

    logging.info(comment_text.decode('unicode-escape'))
    return comment_text.decode('unicode-escape')


def test_process_order_genocide_empty_result():
    order_processor = OrderProcessor(
    '',  # sdk2.Vault.data(self.owner, self.Parameters.yt_token),
    '',  # self.Parameters.caesar_adgroups_path,
    '',  # sdk2.Vault.data(self.owner, 'ROBOT_AUTOSUPBS_YQL_TOKEN_TEMPORARY'),
    '',  # sdk2.Vault.data(self.owner, self.Parameters.charts_token),
    '',  # issue.start,
    None,  # issue.end,
    params='params'
        )

    order_processor._OrderProcessor__execute_yql_query = MagicMock(return_value=([], 'https://yql.yandex-team.ru/Operations/6287a62497c5b749998a33ae'))

    messages = order_processor.process_order_genocide(
        order_id=172056991,
        task_id=123,
        max_entity_count=123
    )

    comment_text = u'\n'.join(messages)  # Test decoding process. Keep this line BaseAutoSupBsIssueProcessor -> on_execute -> for comment in comments:

    logging.info(comment_text.decode('unicode-escape'))
    return comment_text.decode('unicode-escape')
