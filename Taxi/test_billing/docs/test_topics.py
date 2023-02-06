import datetime as dt

import pytest

from billing.docs import service
from billing.docs import topics
from billing.generated.models import topics as models
from billing.tests import mocks


def make_history(
        docs: service.Docs,
        start: dt.datetime = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
) -> topics.DocRefHistory:
    return topics.DocRefHistory(docs, 'key', start)


def make_doc(
        doc_id: int,
        external_ref: str,
        now: dt.datetime,
        data: dict,
        status: str = 'new',
) -> service.Doc:
    return service.Doc(
        id=doc_id,
        kind='doc_ref_history',
        topic='h/key',
        external_ref=external_ref,
        event_at=now,
        process_at=now,
        status=status,
        data=data,
        entry_ids=[],
        revision=None,
    )


def make_history_doc(
        doc_id: int,
        external_ref: str,
        now: dt.datetime,
        data: models.VersionedDocRef,
        status: str = 'new',
) -> topics.VersionedDocRefDoc:
    return topics.VersionedDocRefDoc(
        id=doc_id,
        kind='doc_ref_history',
        topic='h/key',
        external_ref=external_ref,
        event_at=now,
        process_at=now,
        status=status,
        data=data,
        entry_ids=[],
        revision=1,
    )


@pytest.fixture(name='ref_eq')
def _ref_eq(monkeypatch):
    def _cmp(self, other):
        return self.serialize() == other.serialize()

    monkeypatch.setattr(
        'billing.generated.models.topics.VersionedDocRef.__eq__', _cmp,
    )


async def test_empty_history_appended(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref = models.VersionedDocRef(doc_id=2, version=[1], tag='tag')

    append_result = await history.append(ref, now=now)
    assert append_result == topics.Doc(
        doc=make_history_doc(doc_id=1, external_ref='2:1', now=now, data=ref),
        is_ready=True,
    )


async def test_completed_history_appended(ref_eq):
    docs = mocks.TestDocs()
    history = make_history(docs)
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref_1 = models.VersionedDocRef(doc_id=2, version=[1], tag='tag1')
    ref_2 = models.VersionedDocRef(doc_id=3, version=[2], tag='tag2')
    await history.append(ref_1, now=now)
    await docs.finish_processing(1)

    append_result = await history.append(ref_2, now=now)
    assert append_result == topics.Doc(
        doc=make_history_doc(
            doc_id=2, external_ref='3:2', now=now, data=ref_2,
        ),
        is_ready=True,
    )


async def test_pending_history_appended(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref_1 = models.VersionedDocRef(doc_id=2, version=[1], tag='tag1')
    ref_2 = models.VersionedDocRef(doc_id=3, version=[2], tag='tag2')
    await history.append(ref_1, now=now)

    append_result = await history.append(ref_2, now=now)
    assert append_result == topics.Doc(
        doc=make_history_doc(
            doc_id=2, external_ref='3:2', now=now, data=ref_2, status='new',
        ),
        is_ready=False,
    )


async def test_empty_history_get(ref_eq):
    history = make_history(mocks.TestDocs())
    actual = await history.get(1, (1, 1))
    assert actual is None


async def test_history_get(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref = models.VersionedDocRef(doc_id=2, version=[1, 1], tag='tag')
    await history.append(ref, now=now)

    actual = await history.get(2, (1, 1))
    assert actual == topics.Doc(
        doc=make_history_doc(
            doc_id=1, external_ref='2:1.1', now=now, data=ref,
        ),
        is_ready=True,
    )


async def test_empty_history_get_or_append(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref = models.VersionedDocRef(doc_id=2, version=[1], tag='tag1')
    result = await history.get_or_append(ref, now=now)

    assert result == topics.Doc(
        doc=make_history_doc(doc_id=1, external_ref='2:1', now=now, data=ref),
        is_ready=True,
    )


async def test_history_get_or_append(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref = models.VersionedDocRef(doc_id=2, version=[1], tag='tag')
    await history.append(ref, now=now)
    result = await history.get_or_append(ref, now=now)

    assert result == topics.Doc(
        doc=make_history_doc(doc_id=1, external_ref='2:1', now=now, data=ref),
        is_ready=True,
    )


async def test_empty_history_load(ref_eq):
    history = make_history(mocks.TestDocs())
    refs = await history.load()
    assert refs.items() == []


async def test_history_load(ref_eq):
    history = make_history(mocks.TestDocs())
    now = dt.datetime(2021, 2, 1, tzinfo=dt.timezone.utc)
    ref = models.VersionedDocRef(doc_id=2, version=[1], tag='tag')
    await history.append(ref, now=now)
    refs = await history.load()
    assert refs.items() == [
        make_history_doc(doc_id=1, external_ref='2:1', now=now, data=ref),
    ]


@pytest.mark.parametrize(
    'typed_docs, doc_id, expected',
    [
        ([], 1, False),
        (
            [
                make_history_doc(
                    doc_id=1,
                    external_ref='0',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=3, version=[1], tag='tag1',
                    ),
                ),
                make_history_doc(
                    doc_id=2,
                    external_ref='5',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=4, version=[2], tag='tag2',
                    ),
                ),
            ],
            2,
            True,
        ),
    ],
)
def test_doc_ref_contains_doc_id(typed_docs, doc_id, expected):
    docs = [
        service.Doc.from_doc(doc, data=doc.data.serialize())
        for doc in typed_docs
    ]
    refs = topics.VersionedDocRefs.from_docs(docs)
    actual = refs.contains_doc_id(doc_id)
    assert actual == expected


@pytest.mark.parametrize(
    'typed_docs, index, expected',
    [
        (
            [
                make_history_doc(
                    doc_id=1,
                    external_ref='0',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=3, version=[1], tag='tag1',
                    ),
                    status='new',
                ),
                make_history_doc(
                    doc_id=2,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=4, version=[2], tag='tag2',
                    ),
                    status='new',
                ),
                make_history_doc(
                    doc_id=3,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=5, version=[3], tag='tag3',
                    ),
                    status='new',
                ),
            ],
            1,
            False,
        ),
        (
            [
                make_history_doc(
                    doc_id=1,
                    external_ref='0',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=3, version=[1], tag='tag1',
                    ),
                    status='complete',
                ),
                make_history_doc(
                    doc_id=2,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=4, version=[4], tag='tag2',
                    ),
                    status='complete',
                ),
                make_history_doc(
                    doc_id=3,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=5, version=[3], tag='tag3',
                    ),
                    status='new',
                ),
            ],
            2,
            True,
        ),
    ],
)
def test_doc_ref_has_newer_version_before(typed_docs, index, expected):
    docs = [
        service.Doc.from_doc(doc, data=doc.data.serialize())
        for doc in typed_docs
    ]
    refs = topics.VersionedDocRefs.from_docs(docs)
    assert refs.has_newer_version_before(refs.items()[index]) == expected


@pytest.mark.parametrize(
    'typed_docs, index, expected',
    [
        (
            [
                make_history_doc(
                    doc_id=1,
                    external_ref='0',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=3, version=[1], tag='tag1',
                    ),
                    status='complete',
                ),
                make_history_doc(
                    doc_id=2,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=4, version=[3], tag='tag3',
                    ),
                    status='complete',
                ),
                make_history_doc(
                    doc_id=3,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=5, version=[2], tag='tag2',
                    ),
                    status='complete',
                ),
                make_history_doc(
                    doc_id=4,
                    external_ref='3',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(
                        doc_id=6, version=[4], tag='tag4',
                    ),
                    status='new',
                ),
            ],
            3,
            make_history_doc(
                doc_id=2,
                external_ref='1',
                now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                data=models.VersionedDocRef(doc_id=4, version=[3], tag='tag3'),
                status='complete',
            ),
        ),
    ],
)
def test_doc_ref_find_prev_version(ref_eq, *, typed_docs, index, expected):
    docs = [
        service.Doc.from_doc(doc, data=doc.data.serialize())
        for doc in typed_docs
    ]
    refs = topics.VersionedDocRefs.from_docs(docs)
    assert refs.find_prev_version(refs.items()[index]) == expected


@pytest.mark.now('2021-01-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'existing_docs, index, expected_decision',
    [
        pytest.param(
            [
                make_doc(
                    doc_id=6,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [1], 'tag1').serialize(),
                    status='complete',
                ),
                make_doc(
                    doc_id=28,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [2], 'tag1').serialize(),
                    status='new',
                ),
            ],
            1,
            False,
            id='Everything is in order',
        ),
        pytest.param(
            [
                make_doc(
                    doc_id=6,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [1], 'tag1').serialize(),
                    status='new',
                ),
                make_doc(
                    doc_id=28,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [2], 'tag1').serialize(),
                    status='new',
                ),
            ],
            0,
            False,
            id='Newer docs are ignored',
        ),
        pytest.param(
            [
                make_doc(
                    doc_id=5,
                    external_ref='1',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [2], 'tag1').serialize(),
                    status='new',
                ),
                make_doc(
                    doc_id=6,
                    external_ref='2',
                    now=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
                    data=models.VersionedDocRef(6, [1], 'tag1').serialize(),
                    status='new',
                ),
            ],
            1,
            True,
            id='Is outdated',
        ),
    ],
)
async def test_is_outdated(existing_docs, index, expected_decision):
    now = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
    docs_mock = mocks.TestDocs()
    docs_mock.items = existing_docs
    history = topics.DocRefHistory(docs_mock, 'key', now)
    history_items = await history.load()
    history_item = history_items.items()[index]
    assert expected_decision == history_items.is_outdated(history_item)
