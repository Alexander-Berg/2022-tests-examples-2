# -*- coding: utf-8 -*-
# pylint: disable=import-error
from unittest.mock import patch
from odoo.addons.hire.tests.dataset import MainDataset
from odoo.tests import tagged


@tagged('hire', 'department')
class TestDepartment(MainDataset):

    def test_create_dataset(self):
        name = 'New Department'
        kwargs = {
            'name': name,
        }
        department = self.department(save=True, **kwargs)
        staff_id = department['staff_id']
        departments = self.env['hr.department'].search(
            [('staff_id', '=', staff_id)]
        )
        self.assertEqual(len(departments), 1, 'found 1 company')
        department = departments[0]

        self.assertEqual(department['name'], name, 'name')
        self.assertEqual(department['staff_id'], staff_id, 'staff_id')
        self.assertEqual(department.parent_id.id, False, 'parent_id')

    def test_update_new(self):
        new_department = self.department(save=False)
        with patch('common.client.staff.StaffClient.get_departments_query') \
                as staff_mock:
            departments = {
                new_department['staff_id']: {
                    'id': new_department['staff_id'],
                    'name': new_department['name'],
                    'is_deleted': False,
                    'ancestors': {
                        "department": {
                            "is_deleted": False,
                            "id": -1,
                        },
                        "type": "department",
                    },
                }
            }
            staff_mock.return_value = departments
            self.env['hr.department'].init_import_from_staff()

        departments = self.env['hr.department'].search(
            [('staff_id', '=', new_department['staff_id'])]
        )
        self.assertEqual(len(departments), 1, 'found 1 company')
        department = departments[0]

        self.assertEqual(department['name'], new_department['name'], 'name')
        self.assertEqual(department['staff_id'],
                         new_department['staff_id'],
                         'staff_id')
        self.assertEqual(department.parent_id.id, False, 'parent_id')

    def test_create_children(self):
        parent_department = self.department(save=True)
        child_department = self.department(save=False)

        with patch('common.client.staff.StaffClient.get_departments_query') \
                as staff_mock:
            departments = {
                child_department['staff_id']: {
                    'id': child_department['staff_id'],
                    'name': child_department['name'],
                    'is_deleted': False,
                    'ancestors': {
                        "department": {
                            "is_deleted": False,
                            "id": parent_department['staff_id'],
                        },
                        "type": "department",
                    },
                },
                parent_department['staff_id']: {
                    'id': parent_department['staff_id'],
                    'name': parent_department['name'],
                    'is_deleted': False,
                    'ancestors': {
                        "department": {
                            "is_deleted": False,
                            "id": -1,
                        },
                        "type": "department",
                    },
                },

            }
            staff_mock.return_value = departments
            self.env['hr.department'].import_all_staff_departments()

        departments = self.env['hr.department'].search(
            [('staff_id', '=', child_department['staff_id'])]
        )
        self.assertEqual(len(departments), 1, 'found 1 company')
        department = departments[0]

        self.assertEqual(department['name'], child_department['name'], 'name')
        self.assertEqual(department['staff_id'],
                         child_department['staff_id'],
                         'staff_id')
        self.assertEqual(department.parent_id.id,
                         parent_department['id'],
                         'parent_id')

        departments = self.env['hr.department'].search(
            [('staff_id', '=', parent_department['staff_id'])]
        )
        self.assertEqual(len(departments), 1, 'found 1 company')
        department = departments[0]
        self.assertEqual(len(department.child_ids),
                         1,
                         'child_ids')


@tagged('hire', 'department_import')
class TestImportDepartment(MainDataset):
    def test_add_department(self):
        parent_department = self.department(save=True)
        new_department = self.department(save=False)
        with patch('common.client.staff.StaffClient.get_departments_query') \
                as staff_mock:
            departments = {
                new_department['staff_id']: {
                    'id': new_department['staff_id'],
                    'name': new_department['name'],
                    'is_deleted': False,
                    'ancestors': {
                        "department": {
                            "is_deleted": False,
                            "id": parent_department['staff_id'],
                        },
                        "type": "department",
                    },
                },
            }
            staff_mock.return_value = departments
            department = self.env['import.department'].create(
                [{'staff_id': new_department['staff_id']}]
            )
            res_dict = department.add_department()

        self.assertIsNot(res_dict, {}, 'not empty')
        self.assertEqual(res_dict['context'].get('default_name'),
                         new_department['name'],
                         'name')
        self.assertEqual(res_dict['context']['default_staff_id'],
                         new_department['staff_id'],
                         'staff_id')
        self.assertEqual(res_dict['context']['default_parent_id'],
                         parent_department['id'],
                         'parent_id')
