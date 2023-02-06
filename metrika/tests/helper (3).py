import django.test
import logging

logger = logging.getLogger(__name__)


class CmsBaseTestCase:
    fixtures = ('metrika/admin/python/cms/frontend/cms/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()


class NoOpQueue:
    def __init__(self, *args, **kwargs):
        logger.info("{} {}".format(args, kwargs))

    def put(self, *args, **kwargs):
        logger.info("put {} {}".format(args, kwargs))
