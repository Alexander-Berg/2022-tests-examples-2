import mock
import yatest.common as yc


class ArcadiaMock(object):
    def start(self):
        self.get_migrations_dir_mock = mock.patch(
            'passport.backend.vault.api.db.get_migrations_dir',
            return_value=yc.source_path() + '/passport/backend/vault/api/migrations',
        )
        self.get_migrations_dir_mock.start()

    def stop(self):
        self.get_migrations_dir_mock.stop()
