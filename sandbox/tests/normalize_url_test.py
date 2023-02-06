from normalize_url import normalize_url


class TestNormalizeUrl(object):
    def test_remove_same_params(self):
        actual = normalize_url('https://yandex.ru/search/?a=1&a=1')
        assert actual == 'https://yandex.ru/search/?a=1'

    def test_do_not_remove_params_with_empty_value(self):
        actual = normalize_url('https://yandex.ru/search/?a=')
        assert actual == 'https://yandex.ru/search/?a='

    def test_do_not_remove_same_params_with_different_values(self):
        actual = normalize_url('https://yandex.ru/search/?a=1&a=2')
        assert actual == 'https://yandex.ru/search/?a=1&a=2'

    def test_do_not_remove_same_params_with_value_and_empty_value(self):
        actual = normalize_url('https://yandex.ru/search/?a=1&a=')
        assert actual == 'https://yandex.ru/search/?a=&a=1'

    def test_sort_params_including_values(self):
        actual = normalize_url('https://yandex.ru/search/?b=a&a=b&a=a')
        assert actual == 'https://yandex.ru/search/?a=a&a=b&b=a'

    def test_sort_params_including_values_include_empty(self):
        actual = normalize_url('https://yandex.ru/search/?z=&b=a&a=b&a=a')
        assert actual == 'https://yandex.ru/search/?a=a&a=b&b=a&z='

    def test_remove_parameters_from_exclude_set(self):
        exclude_params = {'a', 'b'}
        actual = normalize_url('https://yandex.ru/search/?a=1&b=&c=3', exclude_params)
        assert actual == 'https://yandex.ru/search/?c=3'

    def test_remove_every_parameter_from_exclude_set(self):
        exclude_params = {'a', 'b'}
        actual = normalize_url('https://yandex.ru/search/?a=1&b=&c=3&a=1&b=42', exclude_params)
        assert actual == 'https://yandex.ru/search/?c=3'
