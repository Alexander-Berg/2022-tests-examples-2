# -*- coding: utf-8 -*-
import re

from common        import schema
from common.client import MordaClient
from os            import walk


def get_params(request_files_dir):
    _, _, filenames = next(walk(request_files_dir))
    params = []
    for file in filenames:
        with open(request_files_dir + '/' + file) as f:
            for line in f:
                if re.match(r'/portal/api/(search|yabrowser)/2', line):
                    params.append({'request' : line.rstrip(), 'schema_version': file})

    return params


def prepare_params(params):
    # возможно условие по версии понадобится
    if not 'processAssist' in params:
        params['processAssist'] = 1

    params['request'] = re.sub(
        r"uuid=[^&]+",
        'uuid=fa18cde428c24b67867d6e47fd6dd07e',
        params['request']
    )

    params['request'] = re.sub(
        r"(did|deviceid)=[^&]+",
        'did=d56634c1-812e-4919-88e8-ce1a93c9b229',
        params['request']
    )


def check_params(params):
    if not isinstance(params, dict):
        raise Exception('Bad params, must be dictionary')

    for param in ('request', 'schema_version'):
        if not param in params:
            raise Exception('Param {} is mandatory in params'.format(param))


def get_response(params):
    response = MordaClient().simple(params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    return response.json()


def add_schema_signal(yasm, signal, is_ok):
    if not yasm:
        return

    yasm.add_to_signal('morda_schema_{}_passed_tttt'.format(signal), 1 if is_ok else 0)
    yasm.add_to_signal('morda_schema_{}_failed_tttt'.format(signal), 0 if is_ok else 1)


def format_error(error):
    message =  '[%s]' % ']['.join(repr(index) for index in error.path) + ': ' + error.message.decode('unicode_escape')

    # Более информативное сообщение об ошибке, если блок не подошел ни под одну из схем отсюда
    # https://github.yandex-team.ru/portal/morda-schema/blob/master/api/search/2/block.json#L6-L26
    if list(error.schema_path) == ['properties', 'block', 'items', 'anyOf']:
        # Определяем, у каких схем блоков нет ошибки вида "u'weather' is not one of [u'afisha']"
        # Эти схемы, скорее всего, будут соответствовать проверяемому блоку
        has_type_error = {}
        for suberror in error.context:
            block_schema_index = list(suberror.schema_path)[0]
            if block_schema_index not in has_type_error:
                has_type_error[block_schema_index] = 0
            if list(suberror.schema_path) == [block_schema_index, 'allOf', 1, 'properties', 'type', 'enum']:
                has_type_error[block_schema_index] = 1

        # Добавляем в сообщение все подошибки подходящих схем
        message += '. Maybe because of:'
        for suberror in error.context:
            block_schema_index = list(suberror.schema_path)[0]
            if has_type_error[block_schema_index] == 1:
                continue

            message += '\n[%s]' % ']['.join(repr(index) for index in suberror.absolute_path) + ': ' + suberror.message.decode('unicode_escape')

    return message

def validate_and_send_signal(response, validator, yasm, signal):
    try:
        schema.validate_schema(response, validator, formatter=format_error)
        add_schema_signal(yasm, signal, True)
    except Exception as e:
        add_schema_signal(yasm, signal, False)
        raise e
