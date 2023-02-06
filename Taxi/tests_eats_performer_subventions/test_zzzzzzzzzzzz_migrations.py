# coding=utf-8
import os

import pytest

if os.path.basename(os.getcwd()) == 'uservices':
    SERVICE_PATH = 'services/eats-performer-subventions/'
    MIGRATIONS_PATH = SERVICE_PATH + 'postgresql/eats_performer_subventions'

    def find_migrations(folder):
        return [
            fname.path
            for fname in os.scandir(
                os.path.join(os.path.abspath(MIGRATIONS_PATH), folder),
            )
            if not fname.is_dir()
        ]

    ROLLBACKS = sorted(find_migrations('rollbacks'), reverse=True)
    MIGRATIONS = sorted(find_migrations('migrations'))

    @pytest.mark.pgsql(
        'eats_performer_subventions', files=ROLLBACKS + MIGRATIONS,
    )
    def test_rollback_migrations(pgsql):
        """
         Когда testsuite запускает тесты, он автоматически применяет все
         миграции базы. В этом тесте мы сначала их все откатываем,
         чтобы проверить, что они работают, а затем накатываем вновь,
         чтобы другие тесты видели самую свежую схему базы данных.
         """
        assert MIGRATIONS
        assert ROLLBACKS
        assert len(MIGRATIONS) == len(ROLLBACKS)