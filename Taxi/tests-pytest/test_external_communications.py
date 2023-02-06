import datetime

import pytest

from taxi.external import communications


@pytest.inline_callbacks
@pytest.mark.config(COMMUNICATIONS_DRIVER_NOTIFY_SERVICE='communications_wall')
def test_notify_drivers_communications(patch):
    publish_newsletter = _patch_publish_newsletter(patch)
    send_spam = _patch_send_spam(patch)

    yield communications.notify_drivers(
        request_id='request_id',
        title='Hi, drivers',
        drivers=[('db1', 'uu1'), ('db2', 'uu2')],
        texts=('test', 'me'),
        alert=True,
        important=True,
        expires_at=datetime.datetime(2010, 10, 1),
        tvm_src_service='pytest')
    assert len(publish_newsletter.calls) == 1
    assert len(send_spam.calls) == 0


@pytest.inline_callbacks
@pytest.mark.config(COMMUNICATIONS_DRIVER_NOTIFY_SERVICE='taximeter_wall')
def test_notify_drivers_taximeter(patch):
    publish_newsletter = _patch_publish_newsletter(patch)
    send_spam = _patch_send_spam(patch)

    yield communications.notify_drivers(
        request_id='request_id',
        title='Hi, drivers',
        drivers=[('db1', 'uu1'), ('db2', 'uu2')],
        texts=('test', 'me'),
        alert=True,
        important=True,
        expires_at=datetime.datetime(2010, 10, 1))
    assert len(publish_newsletter.calls) == 0
    assert len(send_spam.calls) == 1


def _patch_publish_newsletter(patch):
    @patch('taxi.external.communications.publish_newsletter')
    @pytest.inline_callbacks
    def publish_newsletter(json, tvm_src_service, log_extra=None):
        assert tvm_src_service == 'pytest'
        assert json['id'] == 'request_id'
        assert json['expire'] == '2010-10-01T00:00:00Z'
        assert json['template']['title'] == 'Hi, drivers'
        assert json['template']['alert']
        assert json['template']['important']
        assert json['drivers'] == [{'driver': 'db1_uu1', 'text': 'test'},
                                   {'driver': 'db2_uu2', 'text': 'me'}]
        yield

    return publish_newsletter


def _patch_send_spam(patch):
    @patch('taxi.external.taximeter.send_spam')
    @pytest.inline_callbacks
    def send_spam(spam_id, title, expires_at, data,
                  alert, important, log_extra=None):
        assert spam_id == 'request_id'
        assert title == 'Hi, drivers'
        assert data == [('db1', 'uu1', 'test'), ('db2', 'uu2', 'me')]
        assert alert
        assert important
        assert expires_at == datetime.datetime(2010, 10, 1)
        yield

    return send_spam
