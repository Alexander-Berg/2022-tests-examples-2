import datetime

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_select


_NOW = datetime.datetime.now()


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('tags', files=['tags_initial.sql'])
@pytest.mark.parametrize(
    'tag_name, text, ticket',
    [
        ('tag0', 'description tag0', 'TICKET-0002'),
        ('tag1', 'updated tag1 description', 'TICKET-0002'),
        ('tag2', 'updated tag2 description', None),
        ('tag_new', 'new tag description', 'TICKET-0002'),
    ],
)
async def test_admin_tag_description(taxi_tags, pgsql, tag_name, text, ticket):
    data = {'text': text}
    if ticket:
        data['ticket'] = ticket

    response = await taxi_tags.put(
        f'v1/admin/tag/description?tag_name={tag_name}',
        data,
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    tag_names = tags_select.select_table_named(
        'meta.tag_names', 'id', pgsql['tags'],
    )
    tag_name_id = next(
        row['id'] for row in tag_names if row['name'] == tag_name
    )
    tag_descriptions = tags_select.select_table_named(
        'meta.tag_descriptions', 'tag_name_id', pgsql['tags'],
    )
    description = next(
        {
            'text': row['text'],
            'author': row['author'],
            'updated_at': row['updated_at'],
            'ticket': row['ticket'],
        }
        for row in tag_descriptions
        if row['tag_name_id'] == tag_name_id
    )
    assert description == {
        'text': text,
        'author': constants.TEST_LOGIN,
        'updated_at': _NOW,
        'ticket': ticket,
    }
