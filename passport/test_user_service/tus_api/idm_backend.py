# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.common.idm.idm_settings import admin_role_name
from passport.backend.qa.test_user_service.tus_api.db import get_db
from passport.backend.qa.test_user_service.tus_api.db_schema import (
    client_table,
    consumer_clients_table,
    consumer_table,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    TusConsumerAccessDenied,
    TusConsumerAlreadyExist,
    TusConsumerNotExist,
)
from passport.backend.qa.test_user_service.tus_api.settings import (
    DEFAULT_TUS_CONSUMER,
    IDM_ROLES,
)
from sqlalchemy.exc import DBAPIError


log = logging.getLogger(__name__)


def _add_tus_client(login):
    """
    Добавляет нового клиента в базу
    """
    clients = get_db().get(client_table, login=login)
    if len(clients) == 0:
        get_db().add(client_table, login=login)


def _add_new_consumer(consumer_name):
    consumers = get_db().get(consumer_table, consumer_name=consumer_name)
    if len(consumers) == 0:
        get_db().add(consumer_table, consumer_name=consumer_name)
    else:
        raise TusConsumerAlreadyExist('TUS consumer with the same name already exists')


def _remove_consumer(consumer_name):
    get_db().remove(consumer_table, consumer_name=consumer_name)


def _get_all_logins():
    """
    [{'login_id': 'id', 'login': 'my_login'}]
    """
    return get_db().get(client_table)


def _get_all_consumers():
    """
    [{'consumer_id': 'id', 'consumer_name': 'my_consumer'}]
    """
    return get_db().get(consumer_table)


def _remove_client_role(consumer_name, role_name, login):
    get_db().remove(consumer_clients_table, login=login, consumer_name=consumer_name, role=role_name)
    log.info("Client '{login}' has lost access to the role '{role}' of the consumer '{consumer_name}'"
             .format(login=login, role=role_name, consumer_name=consumer_name))


def _delete_client(client_login):
    get_db().remove(client_table, login=client_login)
    log.info("Client '{login}' was removed from service clients due to dismissal".format(login=client_login))


def _register_client_consumer(login, consumer_name, role):
    client_roles = get_db().get(consumer_clients_table, login=login, consumer_name=consumer_name, role=role)
    if len(client_roles) == 0:
        get_db().add(consumer_clients_table, login=login, consumer_name=consumer_name, role=role)
        log.info("Client '{login}' got access to the '{consumer_name}'"
                 .format(login=login, consumer_name=consumer_name))
    else:
        log.warning("User '{login}' already has role {consumer_name}:{role}".format(
            login=login, consumer_name=consumer_name, role=role))
    return 0, 'status', 'ok'


def _is_user_bound_to_consumer(consumer, login):
    if consumer == DEFAULT_TUS_CONSUMER:
        return True
    client_consumers = get_db().get(consumer_clients_table, login=login, consumer_name=consumer)
    is_consumer_bound = len(client_consumers) > 0
    return is_consumer_bound


def _is_consumer_exist(consumer):
    is_consumer_exist = len(get_db().get(consumer_table, consumer_name=consumer)) > 0
    return is_consumer_exist


def _get_all_users_consumers():
    """
    [{'consumer_id': 'id', 'consumer_name': 'cnsmr', 'role': 'rl'}]
    """
    return get_db().get(consumer_clients_table)


def _get_all_admins_consumers():
    """
    [{'login': 'id', 'consumer_name': 'cnsmr', 'role': 'rl'}]
    """
    return get_db().get(consumer_clients_table, role=admin_role_name)


def _get_all_consumers_admins():
    """
    {"consumer_name_as_key": [{'username': 'admin'}, ...]}
    :return: словарь вида {"consumer_name_as_key": [{'username': 'admin'}, ...]}
    Почему username? посмотри в .response_examples/info.json
    """
    users_data = _get_all_admins_consumers()
    consumers_list = _get_all_consumers()
    consumers_admins = dict((consumer_entry['consumer_name'], []) for consumer_entry in consumers_list)
    for user_data in users_data:
        consumers_admins[user_data['consumer_name']].append({'username': user_data['login']})
    return consumers_admins


def _get_all_users_data():
    """
    Собирает данные в словарь: {"login_like_key": [{"tus_consumer": "", "role": ""}...]}
    :return: словарь данных пользователя
    """
    users_data = _get_all_users_consumers()
    logins_list = _get_all_logins()
    users_roles = dict((login_entry['login'], []) for login_entry in logins_list)
    for user_data in users_data:
        role = {
            'tus_consumer': user_data['consumer_name'],
            'role': user_data['role'],
        }
        users_roles[user_data['login']].append(role)
    return users_roles


def check_access_to_consumer(login, consumer_name):
    """
    Проверяет, что у пользователя есть доступ к консюмеру
    :param login: логин пользователя со стаффа
    :param consumer_name: имя консюмера, с которым сделал запрос клиент
    :raise TusConsumerAccessDenied: если в таблице нет сооответствующей строки
    """
    if not _is_user_bound_to_consumer(consumer_name, login):
        if _is_consumer_exist(consumer_name):
            raise TusConsumerAccessDenied(
                "Client with login '{login}' cannot use consumer '{consumer_name}'. Request a role with IDM".format(
                    login=login,
                    consumer_name=consumer_name,
                )
            )
        else:
            raise TusConsumerNotExist(
                'Consumer \'{consumer_name}\' doesn`t exist. To create new consumer use /1/create_tus_consumer/'.format(
                    consumer_name=consumer_name
                )
            )
    log.debug("Client '{login}' has access to the '{consumer_name}'".format(login=login, consumer_name=consumer_name))


def bind_client_to_consumer(login, consumer_name, role):
    """
    Привязывает пользователя к консьюмеру с определенной ролью
    :param login: логин клиента со стаффа
    :param consumer_name: имя консюмера (уже существующего)
    :param role: название роли
    :return: кортеж response_code, message_type, message_value
    см .response_examples/add_role.json
    """
    try:
        _add_tus_client(login)
        if role not in IDM_ROLES['values']:
            return 1, 'fatal', 'Role does not exist.'
        return _register_client_consumer(login, consumer_name, role)
    except DBAPIError as err:
        log.error('Database error: %s', err)
        return 1, 'error', 'Error accessing database'


def unbind_consumer_from_client(consumer_name, role_name, login, fired=0):
    """
    Удаляет привязку пользователя к консьюмеру (для конкретной роли)
    :param consumer_name: имя консюмера (уже существующего)
    :param role_name: название роли
    :param login: логин со стаффа
    :param fired: 1 - сотрудник уволен
    :return: кортеж response_code, message_type, message_value
    см .response_examples/add_role.json
    """
    try:
        if fired == 1:
            _delete_client(login)
        else:
            _remove_client_role(consumer_name, role_name, login)
        return 0, 'status', 'ok'
    except DBAPIError as err:
        log.error('Database error: %s', err)
        return 1, 'error', 'Error accessing database'


def build_tus_users_list():
    """
    Собирает всю информацию о пользователях, необходимую для /idm/get-all-roles/
    :return: пример ответа на запрос см .response_examples/get_all_roles.json
    """
    users_data = _get_all_users_data()
    users = []
    for login in users_data:
        user_roles = users_data[login]
        if len(user_roles) != 0:
            user = {
                'login': login,
                'roles': user_roles,
            }
            users.append(user)
    return users


def build_tus_consumers_list():
    """
    Собирает всю информацию о сервисе, необходимую для /idm/info/
    :return: пример ответа на запрос см .response_examples/info.json
    """
    consumers_admins = _get_all_consumers_admins()
    consumers_info = {}
    for consumer in consumers_admins:
        admins = consumers_admins[consumer]
        for admin in admins:
            admin['notify'] = True
        consumers_info[consumer] = {
            'name': consumer,
            'roles': IDM_ROLES
        }
        if len(admins) != 0:
            consumers_info[consumer]['responsibilities'] = admins
    return consumers_info


def create_new_tus_consumer(tus_consumer):
    _add_new_consumer(tus_consumer)


def remove_tus_consumer(tus_consumer):
    _remove_consumer(tus_consumer)
