_UA_YANDEX_TAXI_ANDROID = (
    'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)'
)
_UA_YANDEX_TAXI_IOS = (
    'ru.yandex.taxi.develop/9.99.9 (iPhone; x86_64; iOS 12.2; Darwin)'
)
_UA_YANGO_ANDROID = 'yango/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)'
_UA_YANGO_IOS = (
    'ru.yandex.yango/3.32.3572 (iPhone; iPhone7,1; iOS 9.1; Darwin)'
)
_UA_YAUBER_ANDROID = 'yandex-uber/3.18.0.7675 Android/6.0 (testenv client)'
_UA_YAUBER_IOS = (
    'ru.yandex.uber/3.18.0.7675 (iPhone; iPhone7,1; iOS 9.1; Darwin)'
)


class brand_platform(object):
    def __init__(self, user_agent):
        self.headers = {'User-Agent': user_agent}
        self.user_agent = user_agent


class brand(object):
    def __init__(self, brand_name, user_agent_android, user_agent_ios):
        self.name = brand_name
        self.android = brand_platform(user_agent_android)
        self.iphone = brand_platform(user_agent_ios)


yataxi = brand('yataxi', _UA_YANDEX_TAXI_ANDROID, _UA_YANDEX_TAXI_IOS)
yango = brand('yango', _UA_YANGO_ANDROID, _UA_YANGO_IOS)
yauber = brand('yauber', _UA_YAUBER_ANDROID, _UA_YAUBER_IOS)
unknown = brand('default', 'unknown', 'unknown')
