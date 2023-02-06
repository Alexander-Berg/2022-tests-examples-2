import bson

from taxi.util import dates

from driver_lessons.generated.web import web_context as context_module

EXPECT_IDS_NOT_HIDDEN = [
    '5bca0c9e7bcecff318fef2bb',
    '5bca0c9e7bcecff318fef2aa',
]

EXPECT_IDS_BY_DATE = [
    '5bca0c9e7bcecff318fef2bb',
    '5bca0c9e7bcecff318fef2cc',
    '5bca0c9e7bcecff318fef2aa',
]

EXPECT_LESSON = {
    '_id': bson.ObjectId('5bca0c9e7bcecff318fef2bb'),
    'allowed_territories': {'rus': {'cities': ['Москва'], 'mode': 'include'}},
    'category': 'lesson2_category',
    'content': [],
    'icon': 'text',
    'is_hidden': False,
    'modified_date': dates.parse_timestring('2017-06-29T10:39:27.367Z'),
    'priority': 1,
    'tags': [],
    'title': 'lesson2_title',
}


async def test_lessons_cache(web_app, web_context: context_module.Context):
    lessons_cache = web_context.lessons_cache
    lessons_by_id = [
        str(lesson['_id']) for lesson in lessons_cache.get_not_hidden()
    ]  # pylint: disable=W0212
    assert len(lessons_by_id) == 2
    assert lessons_by_id == EXPECT_IDS_NOT_HIDDEN

    lessons_by_date = lessons_cache.get_all_sorted_by_date()
    lesson_ids_by_date = [str(lesson['_id']) for lesson in lessons_by_date]
    assert lesson_ids_by_date == EXPECT_IDS_BY_DATE

    latest_lesson = lessons_cache._get_latest_lesson()  # pylint: disable=W0212
    assert latest_lesson['_id'] == bson.ObjectId('5bca0c9e7bcecff318fef2aa')
    assert latest_lesson['modified_date'] == dates.parse_timestring(
        '2017-06-29T12:39:27.367Z',
    )

    assert (
        lessons_cache.get_not_hidden_by_id('5bca0c9e7bcecff318fef2bb')
        == EXPECT_LESSON
    )
    assert (
        lessons_cache.get_not_hidden_by_id('5bca0c9e7bcecff318fef2cc') is None
    )
