# -*- coding: utf-8 -*-


import mock
from passport.backend.social.common.test.types import FakeResponse


class BaseFakeProxy(object):
    def __init__(self, repo_class):

        # Для чего нужна функция dispatch?

        # Чтбы получить в методе _dispatch получить доступ и к объекту Fake и к
        # объекту Proxy.

        # С использованием одного лишь метода без функции мы потеряем доступ к
        # объекту Proxy. Как показано ниже.

        # Пусть даны 2 класса Subject и Fake.

        # class Subject(object):
        #     def f(self, a):
        #         pass

        # class Fake(object):
        #     def f(self, a):
        #         assert type(self) is Fake
        #         assert a == 1
        #         # Потеряли объект subject!

        # with patch.object(Subject, 'f', Mock(side_effect=Fake().f)):
        #     subject = Subject()
        #     subject.f(1)

        # Для чего нужно замыкание, почему нельзя использовать просто метод?

        # with patch.object(Subject, 'f', Fake().f):
        #     subject = Subject()
        #     subject.f(1)

        # dispatch учитывает обращения во все методы Proxy.
        def dispatch(repo, *args, **kwargs):
            self._dispatch(repo, *args, **kwargs)

        self._patch = mock.patch.object(
            repo_class,
            'execute_request_basic',
            dispatch,
        )

        self._method_to_mock = {}
        self.requests = []

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        self._patch.stop()

    def set_response_value(self, method, response):
        self.set_response_values(method, [response])

    def set_response_values(self, method, responses):
        http_responses = []
        for response in responses:
            http_responses.append(response)
        self._method_to_mock[method] = mock.Mock(name=method, side_effect=http_responses)

    def _dispatch(self, repo, *args, **kwargs):
        request = repo.context['request']
        self.requests.append(request)
        method = self._request_to_method(request)
        if method not in self._method_to_mock:
            raise MethodNotMocked(method)
        mock = self._method_to_mock[method]
        try:
            response = mock()
        except StopIteration:
            raise MethodNotMocked(method)
        if isinstance(response, Exception):
            raise response
        repo.context['raw_response'] = response

    def _request_to_method(self, request):
        raise NotImplementedError()


class MethodNotMocked(Exception):
    """
    Вызван незамоканый метод прокси.
    """


__all__ = ['FakeResponse']
