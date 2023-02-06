from cron_scripts import check_create_walking_courier
from cron_scripts import create_or_update_tickets
from cron_scripts import export_yt_to_mongo
from cron_scripts import morpheus
from cron_scripts import selfreg_no_dft
from cron_scripts import send_events_to_replication
from cron_scripts import taxiparks2altay


from infranaim.utils.logs import util as log_utils

from infranaim.conftest import *


@pytest.fixture
def run_check_create_walking_courier():
    def run(db_mongo, *args):
        check_create_walking_courier.main(db=db_mongo)
        return 0
    return run


@pytest.fixture
def run_create_or_update():
    def run(db_mongo, *args):
        os.environ['ENVIRONMENT'] = 'PRODUCTION'
        create_or_update_tickets.main(
            db_=db_mongo,
            args=args
        )
        return 0
    return run


@pytest.fixture
def run_export_yt_to_mongo():
    def run(db_mongo):
        os.environ['ENVIRONMENT'] = 'PRODUCTION'
        export_yt_to_mongo.main(db=db_mongo)
        return 0
    return run


@pytest.fixture
def run_selfreg_no_dft():
    def run(db_mongo, *args):
        os.environ['ENVIRONMENT'] = 'PRODUCTION'
        selfreg_no_dft.main(
            db_=db_mongo,
            args=args
        )
        return 0
    return run


@pytest.fixture
def run_send_events_to_replication():
    def run(db_mongo, *args):
        os.environ['ENVIRONMENT'] = 'PRODUCTION'
        send_events_to_replication.main(
            db_=db_mongo,
            args=args
        )
        return 0
    return run


@pytest.fixture
def run_taxiparks2altay():
    def run(db_mongo, *args):
        os.environ['ENVIRONMENT'] = 'PRODUCTION'
        os.environ['YT_TABLE_ALTAY_PHONES'] = 'spravochnik_phones.json'
        os.environ['YT_TABLE_ALTAY_URLS'] = 'spravochnik_urls.json'
        taxiparks2altay.main(
            database=db_mongo,
            args=args
        )
        return 0
    return run


@pytest.fixture
def save_csv_in_project_dir():
    def _do_it(stream, file_name):
        with open('/app/cron_scripts/{}'.format(file_name), 'wb') as file:
            file.write(stream)
        return 0
    return _do_it


@pytest.fixture
def check_file_not_in_project_dir():
    def _do_it(file_name):
        if os.path.exists('/app/cron_scripts/{}'.format(file_name)):
            return 1
        return 0
    return _do_it


@pytest.fixture
def run_morpheus_cron():
    def run(db_mongo):
        _log_extra = log_utils.create_log_extra(task=__file__.replace('.py', ''))
        morpheus.take_red_pill(
            db=db_mongo,
            log_extra=_log_extra
        )
        return 0
    return run
