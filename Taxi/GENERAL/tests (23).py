import datetime as dt
import json
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Optional
from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpRequest
from django.test import TestCase
from django.test import override_settings
from django.test.client import Client
from django.utils import timezone

from vehicles.management.commands.fixlog import fix_vehicle_log
from vehicles.models import CourierLog, CourierImported
from vehicles.models import LockModel
from vehicles.models import StoreUser
from vehicles.models import TaskPhoto, RepairTask, Vehicle, Contractor
from vehicles.models import VehicleLog
from vehicles.models import Warehouse
from vehicles.tasks import do_drop_old_images
from vehicles.sync import (update_received_stores,
                           reassign_stores,
                           get_or_create_user_by_barcode,
                           sync_store_users,
                           update_received_couriers)
from vehicles.client.wms import WMS


class TestLockModel(TestCase):
    def test_acquire_release(self):
        lock_name = 'some_test_lock'
        self.assertEqual(LockModel.acquire(lock_name), True,
                         msg='Lock acquired')
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, True)
        self.assertEqual(LockModel.acquire(lock_name), False,
                         msg='Cannot acquire acquired lock')
        LockModel.release(lock_name)
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, False)

        self.assertEqual(LockModel.acquire(lock_name), True,
                         msg='Released lock acquired again')
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, True)
        LockModel.release(lock_name)
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, False)

    def test_lock_expiration(self):
        lock_name = 'another_test_lock'
        self.assertEqual(LockModel.acquire(lock_name, timeout=2), True,
                         msg='Lock acquired')
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, True)
        self.assertEqual(LockModel.acquire(lock_name), False,
                         msg='Cannot acquire acquired lock')

        lock = LockModel.objects.get(name=lock_name)
        # Simulate passing of time:
        lock.expires = timezone.now() - dt.timedelta(seconds=0.1)
        lock.save()

        self.assertEqual(LockModel.acquire(lock_name), True,
                         msg='Lock acquired after timeout')
        LockModel.release(lock_name)
        self.assertEqual(LockModel.objects.get(name=lock_name).locked, False,
                         msg='Lock released')


def create_repair_task(warehouse: Optional[Warehouse] = None):
    now = dt.datetime.now().astimezone()
    contractor = Contractor.objects.create()
    vehicle = Vehicle.objects.create(pref_contr=contractor,
                                     datetime=now)
    rt = RepairTask.objects.create(vehicle=vehicle, warehouse=warehouse)
    return rt


class TestDeleteObsolete(TestCase):
    @override_settings(MEDIA_ROOT=TemporaryDirectory(prefix='mediatest').name)
    def test_delete_old_task_photo(self):
        rt = create_repair_task()
        now = dt.datetime.now().astimezone()

        with NamedTemporaryFile() as f1, NamedTemporaryFile() as f2:
            new_photo = TaskPhoto.objects.create(feed=rt)
            new_photo.file.save(os.path.basename(f1.name), File(f1))
            TaskPhoto.objects.filter(pk=new_photo.pk).update(
                edit=now - dt.timedelta(days=1) + dt.timedelta(seconds=1))

            old_photo = TaskPhoto.objects.create(feed=rt)
            old_photo.file.save(os.path.basename(f2.name), File(f2))
            TaskPhoto.objects.filter(pk=old_photo.pk).update(
                edit=now - dt.timedelta(days=1) - dt.timedelta(seconds=1))

            self.assertEqual(TaskPhoto.objects.all().count(), 2,
                             '2 photos present')
            old_photo_path = old_photo.file.path
            self.assertTrue(os.path.isfile(old_photo_path),
                            'Old file exists')
            new_photo_path = new_photo.file.path
            self.assertTrue(os.path.isfile(new_photo_path),
                            'New file exists')

            do_drop_old_images(max_age_days=1)

            self.assertEqual(TaskPhoto.objects.all().count(), 1,
                             '1 photo present')
            self.assertFalse(os.path.isfile(old_photo_path),
                             'Old file does not exist')
            self.assertTrue(os.path.isfile(new_photo_path),
                            'New file still exists')

    @override_settings(MEDIA_ROOT=TemporaryDirectory(prefix='mediatest').name)
    def test_delete_old_courier_photo(self):
        now = dt.datetime.now().astimezone()

        with NamedTemporaryFile() as f1, NamedTemporaryFile() as f2:
            old_log = CourierLog.objects.create()
            old_log.photo.save(os.path.basename(f1.name), File(f1))
            CourierLog.objects.filter(pk=old_log.pk).update(
                created=now - dt.timedelta(days=1) - dt.timedelta(seconds=1))

            new_log = CourierLog.objects.create()
            new_log.photo.save(os.path.basename(f2.name), File(f2))
            CourierLog.objects.filter(pk=new_log.pk).update(
                created=now - dt.timedelta(days=1) + dt.timedelta(seconds=1))

            old_log_path = old_log.photo.path
            self.assertTrue(os.path.isfile(old_log_path),
                            'Old file exists')
            new_log_path = new_log.photo.path
            self.assertTrue(os.path.isfile(new_log_path),
                            'New file exists')

            do_drop_old_images(max_age_days=1)

            self.assertFalse(os.path.isfile(old_log_path),
                             'Old file does not exist')
            self.assertTrue(os.path.isfile(new_log_path),
                            'New file still exists')


def create_vehicle(contractor=None, condition=None):
    now = dt.datetime.now().astimezone()
    contractor = contractor or Contractor.objects.create()
    attrs = {}
    if condition:
        attrs['status'] = condition
    vehicle = Vehicle.objects.create(pref_contr=contractor,
                                     datetime=now,
                                     **attrs)
    return vehicle


class TestFixVehicleLog(TestCase):
    def test_fix_log(self):
        vehicle1 = create_vehicle(condition='CREATED')
        vehicle2 = create_vehicle(condition='MOVING')
        vehicle3 = create_vehicle(condition='STOLEN')

        log1 = VehicleLog.objects.filter(
            vehicle=vehicle1).order_by('-datetime').first()
        log2 = VehicleLog.objects.filter(
            vehicle=vehicle2).order_by('-datetime').first()
        log3 = VehicleLog.objects.filter(
            vehicle=vehicle3).order_by('-datetime').first()

        self.assertEqual(log1.condition, 'CREATED', 'correct status in log1')
        self.assertEqual(log2.condition, 'CREATED', 'correct status in log2')
        self.assertEqual(log3.condition, 'CREATED', 'correct status in log3')

        Vehicle.objects.filter(id=vehicle2.id).update(condition='MOVING')
        Vehicle.objects.filter(id=vehicle3.id).update(condition='STOLEN')

        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle1).order_by('-datetime').first(),
            log1,
            'log1 did not change')
        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle2).order_by('-datetime').first(),
            log2,
            'log2 did not change')
        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle3).order_by('-datetime').first(),
            log3,
            'log3 did not change')

        user_model = get_user_model()
        user = user_model.objects.create()

        fix_vehicle_log(user, write=True)

        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle1).order_by('-datetime').first(),
            log1,
            'log1 did not change')
        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle2).order_by('-datetime').first().condition,
            'MOVING',
            'log2 status is correct')
        self.assertEqual(
            VehicleLog.objects.filter(
                vehicle=vehicle3).order_by('-datetime').first().condition,
            'STOLEN',
            'log3 status is correct')


class TestUpdateWarehouses(TestCase):
    def test_update(self):
        Warehouse.objects.create(extermal_id='1',
                                 title='store 1',
                                 store_id='wms_store_id1',
                                 coord='11, 22')
        Warehouse.objects.create(extermal_id='2',
                                 title='store to update',
                                 store_id='wms_store_id2',
                                 coord='33, 44')
        Warehouse.objects.create(extermal_id='4',
                                 title='another store to update',
                                 store_id='wms_store_id4',
                                 coord='33, 44')

        update_received_stores([
            {
                'external_id': '2',
                'title': 'updated store',
                'store_id': 'wms_store_id2',
                'location': {
                    'geometry': {'coordinates': [11.33, 22.44],
                                 'type': 'Point'},
                    'type': 'Feature',
                },
                'address': 'Цурюпа 13',
                'cluster': 'abra',
                'lang': 'ru_RU',
            },
            {
                'external_id': '3',
                'title': 'new store',
                'store_id': 'wms_store_id3',
                'location': {
                    'geometry': {'coordinates': [55.66, 77.88],
                                 'type': 'Point'},
                    'type': 'Feature',
                },
                'address': 'Улица Красных молдавских партизан',
                'cluster': 'kadabra',
                'lang': 'en_UK',
            },
            {
                'external_id': '4',
                'title': 'new title for another store to update',
                'store_id': 'wms_store_id4',
                'location': None,
                'address': 'Улица Вязов',
                'cluster': 'dallas',
            },
        ])

        store1 = Warehouse.objects.get(extermal_id='1')
        store2 = Warehouse.objects.get(extermal_id='2')
        store3 = Warehouse.objects.get(extermal_id='3')
        store4 = Warehouse.objects.get(extermal_id='4')

        self.assertEqual(store1.title, 'store 1')
        self.assertEqual(store1.store_id, 'wms_store_id1')
        self.assertEqual(store1.coord, '11, 22')
        self.assertIsNotNone(store1.edit)

        self.assertEqual(store2.title, 'updated store')
        self.assertEqual(store2.store_id, 'wms_store_id2')
        self.assertEqual(store2.coord, '11.33, 22.44')
        self.assertEqual(store2.cluster, 'abra')
        self.assertEqual(store2.map_link,
                         'https://yandex.ru/maps/?pt=11.33%2C22.44')
        self.assertIsNotNone(store2.edit)

        self.assertEqual(store3.title, 'new store')
        self.assertEqual(store3.store_id, 'wms_store_id3')
        self.assertEqual(store3.coord, '55.66, 77.88')
        self.assertEqual(store3.cluster, 'kadabra')
        self.assertEqual(store3.map_link,
                         'https://maps.google.com/'
                         '?saddr=Current%2BLocation&daddr=77.88%2C55.66')
        self.assertIsNotNone(store3.edit)

        self.assertEqual(store4.title, 'new title for another store to update')
        self.assertEqual(store4.store_id, 'wms_store_id4')
        self.assertEqual(store4.coord, '')
        self.assertEqual(store4.cluster, 'dallas')
        self.assertIsNotNone(store4.edit)

    def test_no_stores_to_update(self):
        update_received_stores([])

    def test_get_cursor_save_cursor(self):
        cursor = WMS.get_last_cursor('some_cursor')
        self.assertEqual(cursor, '', 'At first run cursor is empty')

        WMS.save_cursor('some_cursor', 'some_cursor_value1')
        cursor = WMS.get_last_cursor('some_cursor')
        self.assertEqual(cursor, 'some_cursor_value1', 'cursor updated')

        cursor = WMS.get_last_cursor('another_cursor')
        self.assertEqual(cursor, '', 'At first run cursor is empty')

        WMS.save_cursor('another_cursor', 'another_cursor_value1')
        cursor = WMS.get_last_cursor('another_cursor')
        self.assertEqual(cursor, 'another_cursor_value1',
                         'another cursor updated')


class TestCreateOrUpdateCouriers(TestCase):
    def test_create(self):
        CourierImported.objects.create(phone_pd_id='aisjfdnvalskjv',
                                       first_name='John',
                                       middle_name='Ray',
                                       last_name='Smith',
                                       wms_id='asdjnfkjjasbd314edqa',
                                       external_id='adfaaf')
        CourierImported.objects.create(phone_pd_id='aisjfdnvalwwww',
                                       first_name='Michael',
                                       middle_name='James',
                                       last_name='Keane',
                                       wms_id='asdjnfkjjasbd314bbbb',
                                       external_id='adfccc')

        update_received_couriers([
            {
                'external_id': 'adfaaf',
                'first_name': 'John1',
                'middle_name': 'Ray1',
                'last_name': 'Smith1',
                'courier_id': 'asdjnfkjjasbd314edq1',
                'phone_pd_ids': [
                    {'pd_id': 'aisjfdnvalskj1'}
                ]
            },
            {
                'external_id': 'adfccc',
                'first_name': 'Michael1',
                'middle_name': 'James1',
                'last_name': 'Keane1',
                'courier_id': 'asdjnfkjjasbd314bbb1',
                'phone_pd_ids': [
                    {'pd_id': 'aisjfdnvalwww1'}
                ]
            },
            {
                'external_id': 'adfddd',
                'first_name': 'Kevin',
                'middle_name': 'Smith',
                'last_name': 'Patrick',
                'courier_id': 'asdjnfkjjasbd314dddd',
                'phone_pd_ids': [
                    {'pd_id': 'aisjfdnvalxxxx'}
                ]
            },
        ])

        courier1 = CourierImported.objects.get(external_id='adfaaf')
        courier2 = CourierImported.objects.get(external_id='adfccc')
        courier3 = CourierImported.objects.get(external_id='adfddd')

        self.assertEqual(courier1.middle_name, 'Ray1')
        self.assertEqual(courier1.phone_pd_id, 'aisjfdnvalskj1')
        self.assertEqual(courier1.wms_id, 'asdjnfkjjasbd314edq1')

        self.assertEqual(courier2.first_name, 'Michael1')
        self.assertEqual(courier2.phone_pd_id, 'aisjfdnvalwww1')
        self.assertEqual(courier2.wms_id, 'asdjnfkjjasbd314bbb1')

        self.assertEqual(courier3.last_name, 'Patrick')
        self.assertEqual(courier3.phone_pd_id, 'aisjfdnvalxxxx')
        self.assertEqual(courier3.wms_id, 'asdjnfkjjasbd314dddd')

    def test_no_couriers_to_create(self):
        update_received_couriers([])


def get_response(data, status_code=200):
    resp = requests.Response()
    resp.code = "expired"
    resp.error_type = "expired"
    resp.status_code = status_code
    resp._content = json.dumps(data).encode()
    return resp


class BarcodeAuth(TestCase):
    def test_get_user(self):
        store = Warehouse.objects.create(extermal_id='1',
                                         title='store 1',
                                         store_id='wms_store_id1',
                                         coord='11, 22')
        user_model = get_user_model()
        expected_user = user_model.objects.create()
        expected_user.userprofile.wms_user_id = 'some_user_id'
        expected_user.save()
        resp_data = {
            'code': 'OK',
            'user': 'some_user_id',
            'store': 'wms_store_id1',
            'fullname': 'Vasiliy Zadov',
            'token': ';j;oioei34980fs',
            'mode': 'wms',
            'permits': [],
        }
        with patch.object(requests, 'post',
                          return_value=get_response(resp_data)):
            user_from_wms = get_or_create_user_by_barcode('some_device',
                                                          'some_barcode')
        self.assertEqual(user_from_wms, expected_user)
        self.assertEqual(store.users.filter(pk=user_from_wms.pk).count(), 1,
                         'User has correct store')

    def test_create_user(self):
        store = Warehouse.objects.create(extermal_id='1',
                                         title='store 1',
                                         store_id='wms_store_id1',
                                         coord='11, 22')
        resp_data = {
            'code': 'OK',
            'user': 'some_user_id',
            'store': 'wms_store_id1',
            'fullname': 'Vasiliy Zadov',
            'token': ';j;oioei34980fs',
            'mode': 'wms',
            'permits': [],
        }
        with patch.object(requests, 'post',
                          return_value=get_response(resp_data)):
            user_from_wms = get_or_create_user_by_barcode('some_device',
                                                          'some_barcode')

        self.assertEqual(user_from_wms.userprofile.wms_user_id, 'some_user_id')
        self.assertEqual(user_from_wms.first_name, 'Vasiliy')
        self.assertEqual(user_from_wms.last_name, 'Zadov')
        self.assertRegex(user_from_wms.username, r'vasiliy-zadov-\d+')
        self.assertEqual(store.users.filter(pk=user_from_wms.pk).count(), 1,
                         'User has correct store')


class UserProfileTest(TestCase):
    def test_create_user(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username='vasilii-zadov',
            email='vasilii-zadov@mail.example.com',
            first_name='Vasilii',
            last_name='Zadov',
        )
        self.assertEqual(user.userprofile.username, 'vasilii-zadov')
        self.assertEqual(user.userprofile.email,
                         'vasilii-zadov@mail.example.com')
        self.assertEqual(user.userprofile.first_name, 'Vasilii')
        self.assertEqual(user.userprofile.last_name, 'Zadov')
        self.assertEqual(user.userprofile.is_active, user.is_active)
        self.assertEqual(user.userprofile.is_staff, user.is_staff)
        self.assertEqual(user.userprofile.is_superuser, user.is_superuser)
        self.assertEqual(user.userprofile.date_joined, user.date_joined)

    def test_update_user(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username='vasilii-zadov',
            email='vasilii-zadov@mail.example.com',
            first_name='Vasilii',
            last_name='Zadov',
        )

        user.username = 'petr-traktorenko'
        user.first_name = 'Petr'
        user.last_name = 'Traktorenko'
        user.email = 'petr-traktorenko@mail.example.com'
        user.save()
        self.assertEqual(user.userprofile.username, 'petr-traktorenko')
        self.assertEqual(user.userprofile.email,
                         'petr-traktorenko@mail.example.com')
        self.assertEqual(user.userprofile.first_name, 'Petr')
        self.assertEqual(user.userprofile.last_name, 'Traktorenko')
        self.assertEqual(user.userprofile.is_active, user.is_active)
        self.assertEqual(user.userprofile.is_staff, user.is_staff)
        self.assertEqual(user.userprofile.is_superuser, user.is_superuser)
        self.assertEqual(user.userprofile.date_joined, user.date_joined)


def create_user(username='', first_name='',
                last_name='', wms_user_id='',
                warehouses=None):
    user_model = get_user_model()
    user = user_model.objects.create(username=username,
                                     first_name=first_name,
                                     last_name=last_name)
    user.userprofile.wms_user_id = wms_user_id
    user.save()
    if warehouses:
        user.warehouse_set.set(warehouses)
    return user


class SynchronizeSupervisors(TestCase):
    def test_change_stores(self):
        store1 = Warehouse.objects.create(store_id='wms_store_id1')
        store2 = Warehouse.objects.create(store_id='wms_store_id2')
        store3 = Warehouse.objects.create(store_id='wms_store_id3')

        user = create_user(username='vasilii-zadov',
                           wms_user_id='wms_user_id1',
                           warehouses=[store1, store2])

        reassign_stores([
            {'stores_allow': ['wms_store_id2', 'wms_store_id3', 'not_exist'],
             'user_id': 'wms_user_id1', 'fullname': 'Vasilii Zadov'},
        ])

        user_model = get_user_model()
        new_stores = user_model.objects.get(pk=user.pk).warehouse_set.all()
        new_stores = set(s.pk for s in new_stores)
        self.assertEqual(new_stores, {store2.pk, store3.pk}, 'Stores updated')

    def test_create_user(self):
        store1 = Warehouse.objects.create(store_id='wms_store_id1')
        store2 = Warehouse.objects.create(store_id='wms_store_id2')

        reassign_stores([
            {'stores_allow': ['wms_store_id1', 'wms_store_id2', 'not_exist'],
             'user_id': 'wms_user_id1', 'fullname': 'Vasilii Zadov'},
        ])

        user_model = get_user_model()
        created_user = user_model.objects.get(first_name='Vasilii',
                                              last_name='Zadov')
        new_stores = created_user.warehouse_set.all()
        new_stores = set(s.pk for s in new_stores)
        self.assertEqual(created_user.userprofile.wms_user_id, 'wms_user_id1')
        self.assertRegex(created_user.username, r'vasilii-zadov-\d+')
        self.assertEqual(new_stores, {store1.pk, store2.pk},
                         'Stores assigned')

    def test_multiple_users(self):
        store1 = Warehouse.objects.create(store_id='wms_store_id1')
        store2 = Warehouse.objects.create(store_id='wms_store_id2')
        store3 = Warehouse.objects.create(store_id='wms_store_id3')
        store4 = Warehouse.objects.create(store_id='wms_store_id4')

        create_user(username='vasilii-zadov',
                    wms_user_id='wms_user_id1',
                    warehouses=[store4])

        create_user(username='vasilii-zadov2',
                    wms_user_id='wms_user_id2',
                    warehouses=[store2])

        reassign_stores([
            {'stores_allow': ['wms_store_id1', 'wms_store_id2'],
             'user_id': 'wms_user_id1', 'fullname': 'Vasilii Zadov'},
            {'stores_allow': ['wms_store_id2', 'wms_store_id3'],
             'user_id': 'wms_user_id2', 'fullname': 'Vasilii Zadov2'},
            {'stores_allow': ['wms_store_id3', 'wms_store_id4'],
             'user_id': 'wms_user_id3', 'fullname': 'Petr Traktorenko'},
        ])

        user_model = get_user_model()

        user1 = user_model.objects.get(
            userprofile__wms_user_id='wms_user_id1')
        user2 = user_model.objects.get(
            userprofile__wms_user_id='wms_user_id2')
        user3 = user_model.objects.get(
            userprofile__wms_user_id='wms_user_id3')

        self.assertEqual(
            set(s.pk for s in user1.warehouse_set.all()),
            {store1.pk, store2.pk},
            'Correct store assigned to user 1'
        )
        self.assertEqual(
            set(s.pk for s in user2.warehouse_set.all()),
            {store2.pk, store3.pk},
            'Correct store assigned to user 2'
        )
        self.assertEqual(
            set(s.pk for s in user3.warehouse_set.all()),
            {store3.pk, store4.pk},
            'Correct store assigned to user 3'
        )

        self.assertRegex(user3.username, r'petr-traktorenko-\d+')


@patch('vehicles.sync.read_yt_table', return_value=[
    {'company_id': '2fda2738434434543543543543435434354444343430',
     'email': 'zadov@yandex-team.ru',
     'fullname': 'Василий Задов',
     'phone': '+78005553535',
     'provider': 'yandex-team',
     'role': 'vice_store_admin',
     'store_external_id': '111111',
     'store_id': '7746133713113135b286617f10e9a0cb010154545577',
     'stores_cluster': 'Москва',
     'stores_title': 'Красных молдавских партизан, 19',
     'user_id': 'user_1',
     'user_status': 'active'},

    {'company_id': '13137331713317170000000000000000000000005551',
     'email': 'traktorenko@yandex.ru',
     'fullname': 'Петр Тракторенко',
     'phone': None,
     'provider': 'yandex',
     'role': 'store_admin',
     'store_external_id': '202929',
     'store_id': '44453435435413310000000000000000000000111110',
     'stores_cluster': 'Москва',
     'stores_title': 'Цветочная улица, 7',
     'user_id': 'user_2',
     'user_status': 'disabled'},
])
class TestSyncStoreUsers(TestCase):
    def test_create(self, mocked_read_yt_table):
        sync_store_users()
        self.assertEqual(
            StoreUser.objects.get(
                user_id='user_1').email,
            'zadov@yandex-team.ru',
        )
        self.assertEqual(
            StoreUser.objects.get(
                user_id='user_2').email,
            'traktorenko@yandex.ru',
        )
        self.assertEqual(StoreUser.objects.count(), 2,
                         'Correct number of users')

    def test_create_and_update(self, mocked_read_yt_table):
        StoreUser.objects.create(
            user_id='user_0',
            email='old_email@yandex.ru'
        )
        sync_store_users()
        self.assertEqual(
            StoreUser.objects.get(
                user_id='user_1').email,
            'zadov@yandex-team.ru',
            'First user created',
        )
        self.assertEqual(
            StoreUser.objects.get(
                user_id='user_2').email,
            'traktorenko@yandex.ru',
            'Second user created',
        )
        self.assertEqual(StoreUser.objects.count(), 2,
                         'Correct number of users')


@patch('vehicles.sync.read_yt_table', return_value=[
    {'company_id': '2fda2738434434543543543543435434354444343430',
     'email': 'zadov@yandex-team.ru',
     'fullname': 'Василий Задов',
     'phone': '+78005553535',
     'provider': 'yandex-team',
     'role': 'vice_store_admin',
     'store_external_id': '111111',
     'store_id': '7746133713113135b286617f10e9a0cb010154545577',
     'stores_cluster': 'Москва',
     'stores_title': 'Красных молдавских партизан, 19',
     'user_id': 'user_1',
     'user_status': 'active'},

    {'company_id': '13137331713317170000000000000000000000005551',
     'email': 'traktorenko@yandex.ru',
     'fullname': 'Петр Тракторенко',
     'phone': None,
     'provider': 'yandex',
     'role': 'store_admin',
     'store_external_id': '202929',
     'store_id': '44453435435413310000000000000000000000111110',
     'stores_cluster': 'Москва',
     'stores_title': 'Цветочная улица, 7',
     'user_id': 'user_1',
     'user_status': 'disabled'},
])
class TestSyncStoreUsersNonUniqueIDs(TestCase):
    def test_equal_user_ids(self, mocked_read_yt_table):
        sync_store_users()
        self.assertEqual(
            StoreUser.objects.get(
                email='zadov@yandex-team.ru').stores_title,
            'Красных молдавских партизан, 19',
            'First user created',
        )
        self.assertEqual(
            StoreUser.objects.get(
                email='traktorenko@yandex.ru').stores_title,
            'Цветочная улица, 7',
            'Second user created',
        )
        self.assertEqual(StoreUser.objects.count(), 2,
                         'Correct number of users')


class TestRepairTask(TestCase):

    def setUp(self) -> None:
        user = User.objects.create_superuser('admin', 'foo@foo.com', 'admin')
        user.save()

        self.warehouse = Warehouse.objects.create(title='test_warehouse',
                                                  extermal_id='111',
                                                  store_id='111')
        self.task = create_repair_task(warehouse=self.warehouse)
        self.warehouse.save()
        self.client.login(
            request=HttpRequest(), username='admin', password='admin'
        )

    def test_get_by_id(self):
        req = self.client.post(f'/v/repairtask/{self.warehouse.store_id}/{self.task.pk}')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['id'], self.task.id)
