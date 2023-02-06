import pytest

from document_templator import repositories


@pytest.mark.parametrize(
    'parent_id, expected_descendant_ids',
    (
        (
            '000000000000000000000001',
            {
                '000000000000000000000002',
                '000000000000000000000003',
                '000000000000000000000004',
            },
        ),
        (
            '000000000000000000000002',
            {'000000000000000000000003', '000000000000000000000004'},
        ),
        ('000000000000000000000004', set()),
    ),
)
async def test_get_descendant_ids(
        api_context, parent_id, expected_descendant_ids,
):
    repository = repositories.TemplateGroupRepository(api_context, None)
    descendant_ids = await repository.get_descendant_ids(parent_id)
    assert descendant_ids == expected_descendant_ids
