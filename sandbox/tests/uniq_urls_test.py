from uniq_urls import uniq_urls


class TestUniqUrls(object):
    def test_should_uniq_the_same_urls(self):
        input = [
            'https://yandex.ru/search/?a=1',
            'https://yandex.ru/search/?a=1'
        ]
        expected = {
            'https://yandex.ru/search/?a=1'
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_not_uniq_urls_with_same_params_but_different_values(self):
        input = [
            'https://yandex.ru/search/?a=1',
            'https://yandex.ru/search/?a=2'
        ]
        expected = {
            'https://yandex.ru/search/?a=1',
            'https://yandex.ru/search/?a=2'
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_not_uniq_different_urls_without_params(self):
        input = [
            'https://yandex.ru/search/',
            'https://yandex.com/search/'
        ]
        expected = {
            'https://yandex.ru/search/',
            'https://yandex.com/search/'
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_not_uniq_different_urls_with_the_same_params(self):
        input = [
            'https://yandex.ru/search/?a=1',
            'https://yandex.com/search/?a=1'
        ]
        expected = {
            'https://yandex.ru/search/?a=1',
            'https://yandex.com/search/?a=1'
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_uniq_urls_with_params_with_empty_values(self):
        input = [
            'https://yandex.ru/search/?t=1&a=',
            'https://yandex.ru/search/?t=1&a='
        ]
        expected = {
            'https://yandex.ru/search/?t=1&a='
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_not_change_input_url(self):
        input = [
            'https://yandex.ru/search/?z=999&text=1&a=1&a=0&a=',
            'https://yandex.ru/search/?z=999&text=1&a=1&a=0&a=',
        ]
        expected = {
            'https://yandex.ru/search/?z=999&text=1&a=1&a=0&a='
        }
        actual = uniq_urls(input)
        assert actual == expected

    def test_should_ignore_params_during_uniq(self):
        input = [
            'https://yandex.ru/search/?a=1&b=1',
            'https://yandex.ru/search/?a=1&b=2',
        ]
        expected = {
            'https://yandex.ru/search/?a=1&b=1'
        }
        exclude_params = {'b'}
        actual = uniq_urls(input, exclude_params)
        assert actual == expected
