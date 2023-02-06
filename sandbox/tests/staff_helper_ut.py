# -*- coding: utf-8 -*-

import unittest
import mock

from sandbox.projects.release_machine.helpers.staff_helper import StaffApi


class TestStaffClient(unittest.TestCase):
    def setUp(self):
        human_good_response = {
            "official": {
                "affiliation": "yandex",
                "organization": {
                    "is_deleted": False,
                    "name": "Яндекс.Технологии"
                },
                "is_dismissed": False,
                "is_trainee": False,
                "employment": "partial",
                "is_robot": False,
            }
        }
        robot_good_response = {
            "official": {
                "quit_at": None,
                "join_at": "2015-07-10",
                "affiliation": "external",
                "organization": {
                    "is_deleted": False,
                    "name": "Вне организаций"
                },
                "is_dismissed": False,
                "is_trainee": False,
                "employment": "full",
                "is_robot": True,
            }
        }
        self.get_human_ok = mock.Mock(return_value=human_good_response)
        self.get_robot_ok = mock.Mock(return_value=robot_good_response)
        self.get_all = mock.Mock(
            return_value={
                "page": 1,
                "limit": 50,
                "result": [
                    {
                        "login": "dkvasov",
                        "official": {"is_robot": False}
                    },
                    {
                        "login": "robot-srch-releaser",
                        "official": {"is_robot": True}
                    },
                ],
                "total": 2,
            }
        )
        self.get_persons_fail = mock.Mock(side_effect=IOError)
        self.client = StaffApi()

    def testRobotnessAndExternality(self):
        self.client.get_persons = self.get_human_ok
        self.assertFalse(self.client.check_person_is_robot("login"))
        self.assertFalse(self.client.check_person_is_external("login"))
        self.client.get_persons = self.get_robot_ok
        self.assertTrue(self.client.check_person_is_robot("login"))
        self.assertTrue(self.client.check_person_is_external("login"))
        self.client.get_persons = self.get_persons_fail
        self.assertIsNone(self.client.check_person_is_robot("login"))
        self.assertIsNone(self.client.check_person_is_external("login"))
        self.client.get_persons = self.get_all
        self.assertDictEqual(
            {"dkvasov": False, "robot-srch-releaser": True},
            self.client.get_robotness("logins")
        )


if __name__ == '__main__':
    unittest.main()
