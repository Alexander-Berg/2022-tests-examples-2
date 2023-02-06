# -*- coding: utf-8 -*-
from botocore.exceptions import ClientError


class FakeTouchFiles:
    class State:
        SET = True
        UNSET = False

    def __init__(self, s3_faker, fake_redis):
        self.s3_faker = s3_faker
        self.fake_redis = fake_redis

    def setup_set_mask(self, set_mask):
        """
        :param set_mask: Массив State.SET чтобы проверка наличия файла прошла успешно, State.UNSET, чтобы нет.
        :return: None
        """
        side_effects_s3 = []
        side_effects_redis = []
        for is_set in set_mask:
            side_effects_s3.append(None if is_set else ClientError({'Error': {'Code': '404'}}, 'test-arg'))
            side_effects_redis.append(1 if is_set else 0)

        self.s3_faker.set_response_side_effect('head_object', side_effects_s3)
        self.fake_redis.redis_set_side_effect('exists', side_effects_redis)

    def _find_touch_keys(self, method_name):
        return [call.args[0] for call in self.fake_redis.redis_calls_by_method(method_name)]

    def assert_is_set(self, touch_names):
        keys = self._find_touch_keys('setex')

        assert len(keys) == len(touch_names)

        for key, touch_name in zip(keys, touch_names):
            assert key.endswith(touch_name), '{} is no match for {}'.format(repr(key), repr(touch_name))

    def assert_was_checked(self, touch_names):
        keys = self._find_touch_keys('exists')
        assert len(keys) == len(touch_names)

        for key, touch_name in zip(keys, touch_names):
            assert key.endswith(touch_name), '{} is no match for {}'.format(repr(key), repr(touch_name))
