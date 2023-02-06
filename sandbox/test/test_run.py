import logging
import pytest
from threading import Thread, Event
from yt.wrapper import YtClient

from sandbox.projects.yabs.qa.bases.sample_tables.run import try_lock, TRANSACTION_TITLE_TEMPLATE


class TestTryLock(object):
    def test_successful(self, input_prefix, yt_client):
        with yt_client.Transaction() as tx:
            success, winning_task = try_lock(input_prefix, tx, yt_client)

        assert success
        assert winning_task is None

    @pytest.mark.parametrize(
        'winning_transaction_attributes',
        (
            {'task_id': 1, 'title': TRANSACTION_TITLE_TEMPLATE.format(1)},
            {'task_id': 1, 'title': 'Unknown tx'},
            {'task_id': 1},
            {'title': TRANSACTION_TITLE_TEMPLATE.format(1)},
        ),
        ids=('matching_tx_attributes', 'incorrect_tx_title', 'no_tx_title', 'no_task_id')
    )
    def test_unsuccessful(self, input_prefix, yt_stuff, yt_client, winning_transaction_attributes):
        winning_yt_client = YtClient(proxy=yt_stuff.get_server())
        stop_event = Event()
        lock_is_taken_event = Event()

        def lock_path(path, lock_yt_client):
            with lock_yt_client.Transaction(attributes=winning_transaction_attributes):
                lock_yt_client.lock(path, mode='exclusive')
                lock_is_taken_event.set()
                logging.debug('Lock is taken')
                stop_event.wait(30)
                logging.debug('Releasing lock, stop_event is set: %s', stop_event.is_set())
                lock_yt_client.unlock(path)

        winning_thread = Thread(target=lock_path, args=(input_prefix, winning_yt_client))
        winning_thread.daemon = True
        winning_thread.start()

        lock_is_taken_event.wait()

        with yt_client.Transaction() as tx:
            success, winning_task = try_lock(input_prefix, tx, yt_client)

        stop_event.set()

        assert not success
        assert winning_task == 1
