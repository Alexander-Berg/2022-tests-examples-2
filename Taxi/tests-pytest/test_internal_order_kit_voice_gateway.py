import datetime
import json

import pytest

from taxi.core import async
from taxi.internal.order_kit import voice_gateway


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('json_path,talks_expected', [
    ('get_all_talks.json',
     [('forwarding-0', ['talk-0', 'talk-2']),
      ('forwarding-1', ['talk-1'])]),
])
@pytest.inline_callbacks
def test_syncronize(monkeypatch, load, json_path, talks_expected):
    @async.inline_callbacks
    def get_all_talks(start, end):
        yield
        async.return_value(
            json.loads(load(json_path)))

    @classmethod
    @async.inline_callbacks
    def add_talks(cls, forwarding_id, talk_docs):
        yield
        talks_added.append((forwarding_id, [i['talk_id'] for i in talk_docs]))
        async.return_value(True)

    talks_added = []
    monkeypatch.setattr('taxi.internal.voice_gateway.get_all_talks',
                        get_all_talks)
    monkeypatch.setattr('taxi.internal.dbh.order_talks.Doc.add_talks',
                        add_talks)

    start = datetime.datetime.utcnow()
    end = start + datetime.timedelta(minutes=20)

    yield voice_gateway.syncronize(start, end)

    talks_added.sort()
    assert talks_added == talks_expected
