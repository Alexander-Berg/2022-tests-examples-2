from django.conf import settings

TEST_UID = 123
TEST_LOGIN = 'test.grants.user'

settings.YAUTH_TEST_USER = {
    'uid': TEST_UID,
    'login': TEST_LOGIN,
}

settings.MIDDLEWARE_CLASSES = [
    cls if cls != 'django_yauth.middleware.YandexAuthMiddleware'
    else 'django_yauth.middleware.YandexAuthTestMiddleware'
    for cls in settings.MIDDLEWARE_CLASSES
]
