# -*- coding: utf-8 -*-

from mock import (
    Mock,
    patch,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.core.tvm.tvm_credentials_manager import TvmCredentialsManager
from passport.backend.social.common.exception import GrantsMissingError
from passport.backend.social.common.grants import (
    check_any_of_grants,
    GrantsConfig,
    GrantsContext,
)
from passport.backend.social.common.test.consts import (
    TICKET_BODY1,
    TVM_CLIENT_ID1,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import TestCase


class TestGrantsConfig(TestCase):
    def setUp(self):
        super(TestGrantsConfig, self).setUp()
        self._fake_grants_config = FakeGrantsConfig().start()
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.start()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())

    def tearDown(self):
        self._fake_tvm_credentials_manager.stop()
        self._fake_grants_config.stop()
        super(TestGrantsConfig, self).tearDown()

    def build_grants_config(self, consumer, networks, grants, tvm_client_id=None):
        return {
            consumer: {
                'networks': networks,
                'grants': grants,
                'tvm_client_id': tvm_client_id,
            },
        }

    def get_grants_config(self, configs):
        grants_config = dict()
        for consumer_config in configs:
            grants_config.update(consumer_config)

        for consumer in grants_config:
            self._fake_grants_config.add_consumer(
                consumer,
                networks=grants_config[consumer]['networks'],
                grants=grants_config[consumer]['grants'],
                tvm_client_id=grants_config[consumer].get('tvm_client_id'),
            )

        tvm_credentials_manager = TvmCredentialsManager(
            keyring_config_name='keyring_config-name',
            cache_time=1,
        )

        return GrantsConfig(
            'hello_project',
            tvm_credentials_manager=tvm_credentials_manager,
        )

    def test_network_is_address(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4'),
            ['hello'],
        )

    def test_network_is_mask(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.0/24'],
                grants=['hello'],
            ),
        ])
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4'),
            ['hello'],
        )

    def test_no_grant(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])
        with self.assertRaises(GrantsMissingError):
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='1.2.3.4'),
                ['foo'],
            )

    def test_unlisted_address(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.0/24'],
                grants=['hello'],
            ),
        ])
        with self.assertRaises(GrantsMissingError):
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='4.3.2.1'),
                ['hello'],
            )

    def test_subset_of_grants(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello', 'world'],
            ),
        ])
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4'),
            ['world'],
        )

    def test_networks_intersection(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='morda1',
                networks=['77.88.54.64/27'],
                grants=['foo'],
            ),
            self.build_grants_config(
                consumer='morda2',
                networks=['77.88.54.64/28'],
                grants=['bar'],
            ),
        ])

        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='77.88.54.64'),
            ['foo', 'bar'],
        )
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='77.88.54.80'),
            ['foo'],
        )
        with self.assertRaises(GrantsMissingError):
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='77.88.54.80'),
                ['bar'],
            )
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='77.88.54.72'),
            ['bar', 'foo'],
        )

    def test_consumer(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])
        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4', consumer='foo'),
            ['hello'],
        )

    def test_consumer_from_forbidden_network(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['4.3.2.1'],
                grants=['hello'],
            ),
            self.build_grants_config(
                consumer='bar',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])

        with self.assertRaises(GrantsMissingError):
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='1.2.3.4', consumer='foo'),
                ['hello'],
            )

    def test_no_consumer_with_tvm_client_id(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])

        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4', ticket_body=TICKET_BODY1),
            ['hello'],
        )

    def test_tvm_client_id_assigned_to_consumer_but_no_ticket(self):
        # Важный тестовый случай, когда с потребителем уже связан tvm client id
        # в Грантушке, но потребитель не носит тикеты.
        # Проверка тикета даёт возможность пускать потребителей из
        # облачных систем, где на одном IP-адресе находятся несколько
        # пользователей. Но пускать потребителя из такой сети без тикета
        # опасно.
        # Такая логика влечёт правило, что с потребителем можно связать tvm
        # client id в Грантушке, только после того как потребитель начнёт
        # носить тикеты.
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
                tvm_client_id=TVM_CLIENT_ID1,
            ),
        ])

        with self.assertRaises(GrantsMissingError) as assertion:
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='1.2.3.4', consumer='foo'),
                ['hello'],
            )
        self.assertEqual(
            assertion.exception.args[0],
            'Grants hello are missing for Consumer(ip = 1.2.3.4, name = foo)',
        )

    def test_tvm_client_id_assigned_to_consumer(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
                tvm_client_id=TVM_CLIENT_ID1,
            ),
        ])

        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4', ticket_body=TICKET_BODY1),
            ['hello'],
        )

    def test_tvm_no_grants(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
                tvm_client_id=TVM_CLIENT_ID1,
            ),
        ])

        with self.assertRaises(GrantsMissingError) as assertion:
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='1.2.3.4', ticket_body=TICKET_BODY1),
                ['foo'],
            )
        self.assertEqual(
            assertion.exception.args[0],
            'Grants foo are missing for Consumer(ip = 1.2.3.4, matching_consumers = foo, name_from_tvm = foo, tvm_client_id = 229)',
        )

    def test_invalid_tvm_ticket(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
            ),
        ])

        with self.assertRaises(GrantsMissingError) as assertion:
            check_any_of_grants(
                config,
                GrantsContext(consumer_ip='1.2.3.4', ticket_body='invalid'),
                ['hello'],
            )
        self.assertEqual(assertion.exception.args[0], 'Failed to parse TVM ticket')

    def test_consumer_and_tvm_client_id_not_match(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
                tvm_client_id=TVM_CLIENT_ID1,
            ),
            self.build_grants_config(
                consumer='bar',
                networks=['4.3.2.1'],
                grants=['bye'],
            ),
        ])

        check_any_of_grants(
            config,
            GrantsContext(consumer_ip='1.2.3.4', consumer='bar', ticket_body=TICKET_BODY1),
            ['hello'],
        )

    def test_load_consumer_from_tvm_ticket(self):
        config = self.get_grants_config([
            self.build_grants_config(
                consumer='foo',
                networks=['1.2.3.4'],
                grants=['hello'],
                tvm_client_id=TVM_CLIENT_ID1,
            ),
        ])
        fake_check_tvm_ticket = Mock(wraps=config.check_tvm_ticket)
        context = GrantsContext(consumer_ip='1.2.3.4', ticket_body=TICKET_BODY1)

        with patch.object(
            config,
            'check_tvm_ticket',
            fake_check_tvm_ticket,
        ):
            context.load_consumer_from_tvm_ticket(config)

            self.assertEqual(context.consumer_from_tvm, 'foo')
            self.assertEqual(fake_check_tvm_ticket.call_count, 1)

            context.load_consumer_from_tvm_ticket(config)

            self.assertEqual(context.consumer_from_tvm, 'foo')
            # Использовано закешированное в объекте значение и второй раз тикет
            # не проверяется.
            self.assertEqual(fake_check_tvm_ticket.call_count, 1)
