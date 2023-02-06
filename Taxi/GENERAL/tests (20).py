from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase

from goods.models import ExContractor, Ex_task, Subject
from vehicles.models import Warehouse


# Create your tests here.

class Test_st_status(TestCase):
    c = Client()

    def get_task(self):
        task = Ex_task.objects.get(startrack_key='EXPLOITLAVKATES-1')
        return task

    def setUp(self):
        user = User.objects.create(username='test_user')
        user.save()
        warehouse = Warehouse.objects.create(title='test_warehouse',
                                             extermal_id='111')
        warehouse.save()
        subject = Subject.objects.create(title='test_s',
                                         queue='shvedlavka',
                                         yandex='viktor-shved',
                                         telegram_ids='11111,2222')
        subject.save()
        contractor = ExContractor.objects.create(title='Test contractor',
                                                 subject=subject,
                                                 email='test@test.ru',
                                                 yandex='ya, be')
        contractor.save()

        ex = Ex_task.objects.create(startrack_key='EXPLOITLAVKATES-1',
                                    subject=subject,
                                    priority='minor',
                                    contractor=contractor,
                                    comment='test_comment',
                                    user=user,
                                    warehouse=warehouse,
                                    startrack='minor')
        ex.save()

    def test_ex_status_not_allowed(self):
        resp = self.c.get('/goods/explotation/ex_status/',
                          {"task": "EXPLOITLAVKATES-1",
                           "status": "Требуется информация2"
                           }
                          )
        self.assertEqual(resp.status_code, 405)

    def test_ex_status_not_assert(self):
        resp = self.c.post('/goods/explotation/ex_status/')
        self.assertEqual(resp.status_code, 400)

    def test_ex_status_not_attrs(self):
        resp = self.c.post('/goods/explotation/ex_status/', {
            "status": "Требуется информация2"
        }
                           )
        self.assertEqual(resp.status_code, 400)

    def test_ex_status_happy(self):
        resp = self.c.post('/goods/explotation/ex_status/',
                           {"task": "EXPLOITLAVKATES-1",
                            "status": "Новый статус"
                            }
                           )
        self.assertEqual(resp.status_code, 200)
        task = self.get_task()
        self.assertEqual(task.startrack, 'Новый статус')
