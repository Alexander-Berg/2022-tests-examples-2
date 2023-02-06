import pytest


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['tags_topic_initial.sql'])
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': ['topic1', 'topic3'],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'tag_name, is_financial, is_audited, description',
    [
        (
            'tag0',
            True,
            True,
            {
                'author': 'author_tag0',
                'updated_at': '2021-11-24T16:38:59+0000',
                'text': 'description tag0',
            },
        ),
        (
            'tag1',
            False,
            False,
            {
                'author': 'author_tag1',
                'updated_at': '2021-11-24T16:39:59+0000',
                'text': 'description tag1',
                'ticket': 'TICKET-0001',
            },
        ),
        (
            'tag2',
            True,
            True,
            {
                'author': 'author_tag2',
                'updated_at': '2021-11-24T16:48:59+0000',
                'text': 'description tag2',
            },
        ),
        ('tag3', False, False, None),
        ('tag4', False, True, None),
        ('non-existing-tag', False, False, None),
    ],
)
async def test_admin_tag_info(
        taxi_tags, tag_name, is_financial, is_audited, description,
):
    response = await taxi_tags.get(f'v1/admin/tag/info?tag_name={tag_name}')
    assert response.status_code == 200

    expected = {'is_financial': is_financial, 'is_audited': is_audited}
    if description:
        expected['description'] = description
    assert response.json() == expected
