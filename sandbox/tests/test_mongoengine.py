import mongoengine as me
from mongoengine.queryset import base


# test for changes in REVIEW:884951 (https://a.yandex-team.ru/arc/commit/5323150)
def test_patched_queryset():
    class TestDocument(me.Document):
        pass

    query = base.BaseQuerySet(TestDocument(), None)
    query._comment = "My comment"
    assert query._cursor_args.get("comment") == query._comment
    assert query._query.get("$comment") == query._comment
