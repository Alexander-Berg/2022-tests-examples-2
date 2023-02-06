import uuid
import dateutil.parser
from datetime import datetime, timedelta
from unittest import skip

from django.contrib.auth.models import User, Permission, Group
from django.http import HttpRequest
from django.test import TestCase
from django.test import override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token

from vehicles.models import Warehouse, Vehicle, VehicleType, VehicleBrand, \
    VehicleModel, RepairTask
from vehicles.services.vehicle_services import create_rt_by_vehicle


# Create your tests here.
# @override_settings(AXES_HANDLER='axes.handlers.dummy.AxesDummyHandler')
class Test_change_season(TestCase):
    def setUp(self):
        user = User.objects.create_superuser('admin', 'foo@foo.com', 'admin')
        user.save()
        self.client.login(
            request=HttpRequest(), username='admin', password='admin'
        )
        warehouse = Warehouse.objects.create(
            title='test_warehouse',
            extermal_id='111'
        )
        warehouse.save()
        vt = VehicleType.objects.create(title='test-vh-type')
        vt.save()
        vb = VehicleBrand.objects.create(title='test-vh-brand')
        vb.save()
        vm = VehicleModel.objects.create(title='test-vh-model')
        vm.save()
        self.season_wheels_choices = (
            ('SUMMER', 'Летняя'),
            ('WINTER', 'Зимняя'),
            ('DEMISEASON', 'Демисезонная')
        )
        self.vh = Vehicle.objects.create(
            title='test-title',
            datetime=timezone.now(),
            vin='test-vin',
            type=vt,
            brand=vb,
            mod=vm,
            condition='STOLEN',
            warehouse=warehouse,
            season_wheels='SUMMER'
        )
        self.vh.save()

        rt, create = create_rt_by_vehicle(self.vh, user)
        self.rt = rt

    @skip('Что-то не в порядке')
    @override_settings(AXES_VERBOSE=True)
    def test_season_success(self):
        # TODO: выяснить, почему тест падает, и исправить
        for i in self.season_wheels_choices:
            resp = self.client.post(
                f'/panel/tasks/v2/{self.rt.id}/_season_change',
                data={"whels": i[0]},
                content_type='application/json'
            )
            self.assertEqual(resp.status_code, 200)

    def test_season_bad_data(self):
        resp = self.client.post(f'/panel/tasks/v2/{self.rt.id}/_season_change',
                                {"whels": 'NOT-SEASON'},
                                content_type='application/json'
                                )
        self.assertEqual(resp.status_code, 500)

    def test_season_empty_data(self):
        resp = self.client.post(f'/panel/tasks/v2/{self.rt.id}/_season_change',
                                {"whels": ''},
                                content_type='application/json'
                                )
        self.assertEqual(resp.status_code, 500)


class TestRepairTask(TestCase):
    def create_randomvehicle(self):
        var = uuid.uuid4()

        vt = VehicleType.objects.create(title=f'test-vh-type-{var}')
        vt.save()
        vb = VehicleBrand.objects.create(title=f'test-vh-brand-{var}')
        vb.save()
        vm = VehicleModel.objects.create(title=f'test-vh-model-{var}')
        vm.save()

        vh = Vehicle.objects.create(
            title=f'test-title-{var}',
            datetime=timezone.now(),
            vin=f'test-vin-{var}',
            type=vt,
            brand=vb,
            mod=vm,
            condition='STOLEN',
            warehouse=self.warehouse,
            season_wheels='SUMMER'
        )
        vh.save()
        return vh

    def setUp(self):
        user = User.objects.create_user('admin', 'foo@foo.com', 'admin')
        perm = Permission.objects.get(codename='view_repairtask')
        user.user_permissions.add(perm)
        user.save()
        self.token = Token.objects.create(user=user)
        self.warehouse = Warehouse.objects.create(
            title='test_warehouse',
            extermal_id='111'
        )
        self.warehouse.save()
        vh = self.create_randomvehicle()

        self.rt = RepairTask.objects.create(vehicle=vh, warehouse=self.warehouse)
        self.rt.save()

    def test_repair_tasks(self):
        resp = self.client.post(
            f'/panel/external-api/repair-tasks',
            data={"cursor": datetime.now().astimezone() - timedelta(minutes=1)},
            HTTP_AUTHORIZATION=f'Token {self.token}',
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['result']), 1)
        self.assertEqual(data['result'][0]['source'], 'lavkach')
        self.assertEqual(data['result'][0]['id'], self.rt.id)

    def test_repair_tasks_wrong_data(self):
        resp = self.client.post(
            f'/panel/external-api/repair-tasks',
            data={"cursor": 'wrong_data'},
            HTTP_AUTHORIZATION=f'Token {self.token}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_repair_tasks_empty_data(self):
        resp = self.client.post(
            f'/panel/external-api/repair-tasks',
            HTTP_AUTHORIZATION=f'Token {self.token}',
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['result']), 1)

    def test_repair_tasks_empty_resp(self):
        resp = self.client.post(
            f'/panel/external-api/repair-tasks',
            HTTP_AUTHORIZATION=f'Token {self.token}',
            data={"cursor": datetime.now().astimezone() + timedelta(minutes=1)},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['result']), 0)

    def test_repair_tasks_update_cursor(self):
        vh = self.create_randomvehicle()
        rt = RepairTask.objects.create(vehicle=vh, warehouse=self.warehouse)
        rt.save()
        print(rt.edit)

        resp = self.client.post(
            f'/panel/external-api/repair-tasks',
            HTTP_AUTHORIZATION=f'Token {self.token}',
            data={"cursor": datetime.now().astimezone() - timedelta(minutes=1)},
            content_type='application/json'
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['result']), 2)
        self.assertEqual(dateutil.parser.isoparse(data['cursor']), rt.edit)
