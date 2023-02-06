import allure
import pprint
import collections

import metrika.pylib.mtapi.cluster as cluster


MockRecord = collections.namedtuple("MockRecord", ("handle", "params", "response"), defaults=[None, None, None])


class MockClusterApi:
    def __init__(self):
        self._mapping = []

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        allure.attach("MockClusterApi set mapping", pprint.pformat(value))
        self._mapping = value

    @allure.step("MockClusterApi Constructor call")
    def __call__(self, url=None):
        return self

    def _get_mock_record(self, *modules, **kwargs):
        handle = "/" + "/".join(modules)

        def predicate(mock_record):
            matched = True
            if mock_record.handle:
                matched = matched and handle == mock_record.handle
            if mock_record.params:
                for k, v in mock_record.params.items():
                    matched = matched and (k in kwargs and v == kwargs[k])
            return matched

        return next(filter(predicate, self._mapping))

    @allure.step("MockClusterApi.request")
    def request(self, *modules, **kwargs):
        handle = "/" + "/".join(modules)
        params = "\n".join([f"{k}={v}" for k, v in kwargs.items()])
        allure.attach("Request", handle + "\n" + params)
        mock_record = self._get_mock_record(*modules, **kwargs)
        allure.attach("Mock Record", "\n".join([f"{k}: {v}" for k, v in mock_record._asdict().items()]))
        return mock_record.response

    def __getattr__(self, attr):
        if attr in ('get', 'group_by'):

            def func(**kwargs):
                return self.request(attr, **kwargs)

            return func
        else:
            return cluster.ClusterAPIModuleManager(self, attr)
