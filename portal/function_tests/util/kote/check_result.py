# -*- coding: utf-8 -*-

import re
from portal.function_tests.util.common.schema import get_schema_validator, validate_schema
import portal.function_tests.util.common.utils as common_utils
from portal.function_tests.util.kote.kote_callback_functions import Callback
import portal.function_tests.util.kote.kote_exceptions as kote_exceptions


def generate_report(report, tab=0, ans=''):
    for keys, values in report.iteritems():
        if not isinstance(values, dict):
            ans += '\n' + '{}{}: {}'.format('  ' * tab, keys, values)
        else:
            ans += '\n' + '{}{}:'.format('  ' * tab, keys)
            ans = generate_report(values, tab + 1, ans)

    return ans

'''
class BugReport():
    def __init__(self, test_path):
        self.test_path = test_path
        self.report = {}

    def append(self, path, text):
        temp = self.report
        while len(path) != 1:
            key = path.pop(0)
            if not key in temp:
                temp[key] = {}
            temp = temp[key]
        temp[path[0]] = text

    def generate_report(self):
        if len(self.report) != 0:
            self.__output()

    def __output(self):
        if 'result' in self.report and 'schema' in self.report:
            raise AssertionError('\n' + self.test_path + '\n' + 'result and schema tests failed:\n' + generate_report(self.report))
        elif 'result' in self.report:
            raise AssertionError('\n' + self.test_path + '\n' + 'result tests failed:\n' + generate_report(self.report))
        elif 'schema' in self.report:
            raise AssertionError('\n' + self.test_path + '\n' + 'schema tests failed:\n' + generate_report(self.report))
'''


class SmartCheck():
    def __init__(self, response=None, result=None, params=None, test_path=None, schema=None, exception=None):
        self.response = response
        self.result = result
        self.params = params
        # self.errors = BugReport(test_path)
        self.schema = schema
        self.test_path = test_path
        self.exception = exception

    def check_schema(self):
        if self.schema:
            for items in self.schema:
                schema_item = items[0]
                test_response = self.response.copy()
                if len(items) > 1:
                    for blocks in items[-1:0:-1]:
                        test_response = test_response[blocks]
                validator = get_schema_validator(schema_item)
                validate_schema(test_response, validator)

    def raise_missed_exception(self):
        if self.exception:
            if 'class' in self.exception:
                raise kote_exceptions.MissedException(self.exception['class'])

    def check_exception(self, exc, exceptions):
        if self.exception:
            if 'class' in self.exception:
                try:
                    if isinstance(exc, Exception):
                        assert self.exception['class'] == exc.__class__.__name__
                    else:
                        assert self.exception['class'] == exc
                except AssertionError as new_exc:
                    exceptions.append(kote_exceptions.CheckException(new_exc, self.test_path, None))

                return 1
        return 0

    def check(self, response='YAML_TEST_RESPONSE_FLAG', result='YAML_TEST_RESULT_FLAG', path=None):
        if self.result is None:
            return True
        if response == 'YAML_TEST_RESPONSE_FLAG':
            response = self.response
        if result == 'YAML_TEST_RESULT_FLAG':
            result = self.result
        if path is None:
            try:
                common_utils.check_madm_error(response)
            except common_utils.MadmMockError as exc:
                raise common_utils.MadmMockError('{}\nFailed on test {}'.format(exc, self.test_path))
            path = []
        if isinstance(result, dict) and isinstance(response, dict):
            for keys in result:
                if keys in response:
                    if result[keys] == 'IS_EXIST':
                        continue
                    elif result[keys] == 'NOT_EXIST':
                        assert False, '{} unexpected key {}\nFailed on test {}'.format(self.recreate_path(path), keys, self.test_path)
                else:
                    if result[keys] == 'NOT_EXIST':
                        continue
                    else:
                        assert False, '{} missing key {}\nFailed on test {}'.format(self.recreate_path(path), keys, self.test_path)
                temp_path = path[:]
                temp_path.append(keys)
                self.check(response=response[keys], result=result[keys], path=temp_path)
            return True
        elif isinstance(response, list) and isinstance(result, dict):
            response_to_check = response
            _result = result.copy()
            is_length_checked = False

            if 'LENGTH' in _result:
                is_length_checked = True
                temp_path = path[:]
                temp_path.append('LENGTH')
                length = _result.pop('LENGTH')
                self.check(response=len(response), result=length, path=temp_path)

            if 'FILTER' in _result:
                response_to_check = []
                filter_dict = _result.pop('FILTER')
                for item in response:
                    if self._matching_item(item, filter_dict, path):
                        response_to_check.append(item)

                if 'FILTERED_LENGTH' in _result:
                    is_length_checked = True
                    # filtered_length = _result['FILTERED_LENGTH']
                    temp_path = path[:]
                    temp_path.append('FILTERED_LENGTH')
                    length = _result.pop('FILTERED_LENGTH')
                    self.check(response=len(response_to_check), result=length, path=temp_path)

            assert is_length_checked or len(response_to_check) > 0, '{} no matching items in array.\nFailed on test {}'.format(self.recreate_path(path), self.test_path)

            if 'ITEM' in _result:
                n_item = 0
                temp_path = path[:]
                array_elem = temp_path[-1]
                item = _result.pop('ITEM')
                for r_items in response_to_check:
                    temp_path.pop()
                    index_elem = array_elem + '[' + str(n_item) + ']'
                    temp_path.append(index_elem)
                    self.check(response=r_items, result=item, path=temp_path)
                    n_item += 1

            for keys in _result:
                assert isinstance(keys, int), '{} is a list, no keys named {}\nFailed on test {}'.format(self.recreate_path(path), keys, self.test_path)
                assert keys < len(response), '{} is too short, doesn\'t have element with index {}\nFailed on test {}'.format(self.recreate_path(path), keys, self.test_path)
                temp_path = path[:]
                temp_path.append(keys)
                self.check(response=response[keys], result=_result[keys], path=temp_path)

        elif isinstance(result, dict) and not isinstance(response, dict):
            assert False, '{}: {} is not dict\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif isinstance(result, list):
            self.list_manager(response, result, path)
        else:
            self.check_outer_simple(response, result, path)

    def check_outer_simple(self, response, result, path):
        if result == 'IS_EMPTY':
            assert response is None
        elif result == 'NOT_EMPTY':
            assert response is not None, '{}{} is None\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_INT':
            assert isinstance(response, int), '{}{} is not int\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_ARRAY':
            assert isinstance(response, list), '{}{} is not array\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_STRING':
            assert isinstance(response, str) or isinstance(response, bytes), '{}{} is not string\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_DICT':
            assert isinstance(response, dict), '{}{} is not dict\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_EXIST':
            pass
        else:
            assert self.equality_check(response, result), '{}{} is not {}\nFailed on test {}'.format(self.recreate_path(path), response, result, self.test_path)

    def check_outer_simple_not(self, response, result, path):
        if result == 'IS_EMPTY':
            assert response is not None, '{}{} in None\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'NOT_EMPTY':
            assert response is None, '{}{} is not None\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_INT':
            assert not isinstance(response, int), '{}{} is int\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_ARRAY':
            assert not isinstance(response, list), '{}{} is array\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_STRING':
            assert not isinstance(response, str), '{}{} is string\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_DICT':
            assert not isinstance(response, dict), '{}{} is dict\nFailed on test {}'.format(self.recreate_path(path), response, self.test_path)
        elif result == 'IS_EXIST':
            pass
        else:
            assert not self.equality_check(response, result), '{}{} is {}\nFailed on test {}'.format(self.recreate_path(path), response, result, self.test_path)

    def check_outer_and(self, response, result, path):
        for items in result[1:]:
            self.check_outer_simple(response, items, path)

    def check_outer_not(self, response, result, path):
        for items in result[1:]:
            self.check_outer_simple_not(response, items, path)

    def check_outer_or(self, response, result, path):
        flag = 0
        big_report = []
        for items in result[1:]:
            flag_add, report = self._help_for_outer_or(response, items)
            if not flag_add:
                big_report.append(report)
            flag += flag_add
        big_report = ', '.join(big_report)

        assert flag != 0, '{}{} {}'.format(self.recreate_path(path), response, big_report)

    def recreate_path(self, path):
        format_path = ''.join('\n{}{}: '.format('  ' * i , items) for i, items in enumerate(path))

        return format_path

    def _help_for_outer_or(self, response, result):
        if result == 'IS_EMPTY':
            return response is None, 'in not None'
        elif result == 'NOT_EMPTY':
            return response is not None, 'is None'
        elif result == 'IS_INT':
            return isinstance(response, int), 'is not int'
        elif result == 'IS_ARRAY':
            return isinstance(response, list), 'is not array'
        elif result == 'IS_STRING':
            return isinstance(response, str), 'is not string'
        elif result == 'IS_DICT':
            return isinstance(response, dict), 'is not dict'
        elif result == 'IS_EXIST':
            return True, ''
        else:
            return self.equality_check(response, result), 'is not {}'.format(result)

        return True, ''

    # тут будет функция, которая работает со вложенностью, нужно добавить list_type_check в check и вызывать manager
    def list_manager(self, response, result, path):
        if self.list_type_check(result):
            assert self._check_big_logic(response, result), '{}{} \nFailed check {}\nFailed on test {}'.format(self.recreate_path(path), response, result, self.test_path)
        elif result[0] == 'AND':
            self.check_outer_and(response, result, path)
        elif result[0] == 'OR':
            self.check_outer_or(response, result, path)
        elif result[0] == 'NOT':
            self.check_outer_not(response, result, path)
        elif result[0] == 'RE':
            match = re.findall(result[1], response)
            assert self.equality_check(len(match), '>0'), '{}{} \nFailed check {}\nFailed on test {}'.format(self.recreate_path(path), response, result[1], self.test_path)
        elif result[0] == 'CALLBACK':
            callback_func = getattr(Callback, result[1])
            callback_func(response, self.test_path)
        else:
            self.check_outer_simple(response, result, path)

    def _matching_item(self, response, predicate, path):
        if predicate is None:  # Filter не задан
            return True

        match = True
        try:
            # Стандартный check assert-ит
            match = self.check(response=response, result=predicate, path=path)
        except Exception:
            match = False
        finally:
            if match is None:
                match = False
        return match

    def _check_big_logic(self, response, result):
        if isinstance(result, dict):
            if not isinstance(response, dict):
                return False
            for keys in result:
                ans = True
                if keys not in response:
                    return False
                if ans:
                    check = self._check_big_logic(response[keys], result[keys])
                    ans = check
            return ans
        if not isinstance(result, list):
            check, _ = self._help_for_outer_or(response, result)
            return check
        else:
            if result[0] == 'OR':
                for items in result[1:]:
                    if self._check_big_logic(response, items):
                        return True
                return False
            if result[0] == 'AND':
                for items in result[1:]:
                    if not self._check_big_logic(response, items):
                        return False
                return True
            if result[0] == 'NOT':
                for items in result[1:]:
                    if self._check_big_logic(response, items):
                        return False
                return True

    @staticmethod
    def list_type_check(lst):
        for items in lst:
            if isinstance(items, list):
                if items[0] == 'OR' or items[0] == 'AND' or items[0] == 'NOT':
                    return True
        return False

    # HOME-76758, функция для операторов сравнения
    def equality_check(self, response, result):
        if (isinstance(result, bytes) or isinstance(result, str)) and (isinstance(response, float) or isinstance(response, int)):
            if result.startswith('<='):
                try:
                    result = int(result[2:])
                    return response <= result
                except ValueError:
                    result = float(result[2:])
                    return response <= result
                except ValueError:
                    return response == result
            elif result.startswith('>='):
                try:
                    result = int(result[2:])
                    return response >= result
                except ValueError:
                    result = float(result[2:])
                    return response >= result
                except ValueError:
                    return response == result
            elif result.startswith('>'):
                try:
                    result = int(result[1:])
                    return response > result
                except ValueError:
                    result = float(result[1:])
                    return response > result
                except ValueError:
                    return response == result
            elif result.startswith('<'):
                try:
                    result = int(result[1:])
                    return response < result
                except ValueError:
                    result = float(result[1:])
                    return response < result
                except ValueError:
                    return response == result
            elif result.find('..') != -1:
                a, b = result.split('..')
                try:
                    a = int(a)
                except ValueError:
                    a = float(a)
                except ValueError:
                    return response == result
                try:
                    b = int(b)
                except ValueError:
                    b = float(b)
                except ValueError:
                    return response == result
                return a <= response <= b
        if isinstance(result, str):
            if result.startswith('@'):
                value = result
                name = result[1:]
                if name in self.params:
                    value = self.params[name]
                # Сравниваем как строки
                return str(response) == str(value)
        return response == result
