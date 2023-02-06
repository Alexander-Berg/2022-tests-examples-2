# coding=utf-8
import os


IDM_OAUTH_TOKEN = os.environ.get('IDM_OAUTH_TOKEN', '')

IDM_SYSTEM = 'test-user-service'

prefix = '/api/v1'

IDM_ROLE_REQUEST_PATH_PATTERN = '/{consumer}/{role}/'

admin_role_name = 'admin'
user_role_name = 'user'

role_name = {'en': 'role', 'ru': 'роль'}
admin_name = {'en': 'admin', 'ru': 'администратор'}
user_name = {'en': 'user', 'ru': 'пользователь'}
