from .utils import assert_util


class PostJsonAssertUtil(assert_util.PostJsonAssertUtil):
    def __init__(self, client):
        super().__init__(client, 'autogen/x-taxi-cpp-type/openapi-3-0-0')


async def test_post_case_extra(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(
        {'extra-1': 5432, 'extra-2': 123, 'extra-3': 456},
    )


async def test_post_case_simple(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'case-simple': 5423})


async def test_post_ref_simple(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'ref-simple': 5423})


async def test_post_case_array(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'case-array': [5423, 123, 456]})


async def test_post_case_ref_array(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'case-ref-array': [5423, 123, 456]})


async def test_post_case_ref_array_item(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'case-ref-array-item': [5423, 123, 456]})


async def test_post_case_object(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(
        {
            'case-object': {
                'lat': 45,
                'lon': 112,
                'timestamp': 5423,
                'accuracy': 12,
                'speed': 421,
                'direction': 120,
            },
        },
    )


async def test_post_case_ref_object(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(
        {
            'case-ref-object': {
                'lat': 45,
                'lon': 112,
                'timestamp': 5423,
                'accuracy': 12,
                'speed': 421,
                'direction': 120,
            },
        },
    )


async def test_post_case_ref_object_simple(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(
        {
            'case-ref-object-simple': {
                'field': 'my field',
                'extra-1': 5423,
                'extra-2': 123,
                'extra-3': 456,
            },
        },
    )


async def test_post_case_ref_object_item(taxi_userver_sample):
    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(
        {
            'case-ref-object-item': {
                'field': 'my field',
                'extra-1': 5423,
                'extra-2': 123,
                'extra-3': 456,
            },
        },
    )
