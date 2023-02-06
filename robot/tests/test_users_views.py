import robot.smelter.backend.tests.conftest  # noqa
from robot.smelter.backend.users.models import User
from robot.smelter.backend.tests.common import TestDB, prepare_test_client, prepare_anon_test_client, prepare_yandex_test_client, \
    TEST_USER, YANDEX_USER, NEW_USER
from rest_framework.test import APIClient

from django.test import TestCase


import pytest
import logging


@pytest.mark.django_db
class TestUsers(TestCase):
    def setUp(self):
        self.test_db = TestDB()
        self.client = prepare_test_client(self.test_db)
        self.anon_client = prepare_anon_test_client()
        self.yandex_client = prepare_yandex_test_client(self.test_db)

    def test_csrf(self):
        res = self.client.get("/users/csrf")
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.cookies.get("csrftoken"))

    def test_get_user(self):
        res = self.client.get("/users/get_user")
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.cookies.get("csrftoken"))
        self.assertEqual(res.data["username"], TEST_USER)

        res = self.anon_client.get("/users/get_user")
        self.assertEqual(res.status_code, 401)

    def test_change_user_flow(self):
        res = self.yandex_client.post("/users/reset_password", {
            "username": YANDEX_USER
        }, format="json")
        self.assertEqual(res.status_code, 200)
        logging.info("Got response %s", str(res.json()))
        temporary_code = res.json()["temporary_code"]

        res = self.yandex_client.post("/users/change_user", {
            "username": YANDEX_USER,
            "temporary_code": temporary_code,
            "password": "1234"
        })
        self.assertEqual(res.status_code, 201)

        res = self.yandex_client.post("/users/login", {
            "username": YANDEX_USER,
            "password": "1234"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.cookies.get("sessionid"))

        res = self.yandex_client.get("/users/logout")
        self.assertEqual(res.status_code, 200)

    def test_invite_and_delete_flow(self):
        res = self.yandex_client.get("/users/create_invite")
        self.assertEqual(res.status_code, 200)
        logging.info("Got response %s", res.json())
        temporary_code = res.json()["temporary_code"]

        res = self.anon_client.post("/users/create_user", {
            "username": NEW_USER,
            "password": "1234",
            "temporary_code": temporary_code,
            "email": "somebody@email.com"
        })
        self.assertEqual(res.status_code, 201)
        new_user = User.get_or_none(username=NEW_USER)
        new_user_client = APIClient()
        new_user_client.force_authenticate(user=new_user)

        res = new_user_client.delete("/users/change_user", {
            "username": NEW_USER,
            "password": "1234"
        })
        self.assertEqual(res.status_code, 204)
