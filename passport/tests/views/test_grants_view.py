# coding: utf-8

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.models import TvmGrants
from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestTvmGrantsView(BaseTestClass):
    fill_database = True

    def test_ok(self):
        with self.app.app_context():
            with TimeMock():
                TvmGrants.grant(2000079, u'Тестовое приложение')

        r = self.client.get_tvm_grants()
        self.assertResponseOk(r)
        self.assertResponseEqual(
            r,
            {
                u'status': u'ok',
                u'tvm_grants': [
                    {
                        u'comment': u'Default external app',
                        u'created_at': 1445385600.0,
                        u'tvm_client_id': 1,
                    },
                    {
                        u'comment': u'\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
                        u'created_at': 1445385600.0,
                        u'tvm_app': {
                            u'abc_department': {
                                u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                u'id': 14,
                                u'unique_name': u'passp',
                            },
                            u'abc_state': u'granted',
                            u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                            u'name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442 [testing]',
                            u'tvm_client_id': 2000079,
                        },
                        u'tvm_client_id': 2000079,
                    },
                ],
            }
        )
