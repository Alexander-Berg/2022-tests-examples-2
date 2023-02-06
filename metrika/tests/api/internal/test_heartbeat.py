import pytest
import django.test

import metrika.pylib.structures.dotdict as mdd

import metrika.admin.python.cms.frontend.cms.models as cms_models

pytestmark = pytest.mark.django_db(transaction=True)


class TestGet(django.test.TestCase):
    def test_get(self):
        # предусловия
        cms_models.Heartbeat.objects.create(identity="some-identity")

        # действия
        response = self.client.get("/api/v1/internal/heartbeat/some-identity")

        # проверки
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["identity"], "some-identity")


class TestGetList(django.test.TestCase):
    def test_get_list(self):
        # предусловия
        cms_models.Heartbeat.objects.create(identity="some-identity")

        # действия
        with self.settings(CONFIG=mdd.DotDict.from_dict({'max_heartbeat_last_age_seconds': 0})):
            response = self.client.get("/api/v1/internal/heartbeat")

        # проверки
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_get_list_all(self):
        # предусловия
        cms_models.Heartbeat.objects.create(identity="some-identity")

        # действия
        with self.settings(CONFIG=mdd.DotDict.from_dict({'max_heartbeat_last_age_seconds': 0})):
            response = self.client.get("/api/v1/internal/heartbeat?all")

        # проверки
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


class TestPost(django.test.TestCase):
    def test_post_new(self):
        # предусловия
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 0)

        # действия
        response = self.client.post("/api/v1/internal/heartbeat?identity=some-uid")

        # проверки
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 1)

    def test_post_update(self):
        # предусловия
        response = self.client.post("/api/v1/internal/heartbeat?identity=some-uid", )
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 1)

        # действия
        response = self.client.post("/api/v1/internal/heartbeat?identity=some-uid", )

        # проверки
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 1)

    def test_post_multi(self):
        # предусловия
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 0)

        # действия
        response = self.client.post("/api/v1/internal/heartbeat?identity=some-uid")
        response_other = self.client.post("/api/v1/internal/heartbeat?identity=some-other-uid")

        # проверки
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response_other.status_code, 204)
        self.assertEqual(len(cms_models.Heartbeat.objects.all()), 2)
