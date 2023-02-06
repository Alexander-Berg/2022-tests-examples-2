import django.test


class DutyBaseTestCase:
    fixtures = ('metrika/admin/python/duty/frontend/duty/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()
