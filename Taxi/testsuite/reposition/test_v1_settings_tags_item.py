import pytest

from .reposition_select import select_table_named


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_empty(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/tags/list')
    assert response.status_code == 200
    assert response.json() == {'tags': []}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['tag_default.sql'])
def test_get(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/tags/list')
    assert response.status_code == 200
    assert response.json() == {'tags': [{'tag_id': 'default_tag'}]}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/item', json={'tag_id': 'new_tag'},
    )
    assert response.status_code == 200
    assert select_table_named(
        'config.tags', 'tag_id', pgsql['reposition'],
    ) == [{'tag_id': 1, 'tag_name': 'new_tag'}]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['tag_default.sql'])
def test_put_existent_tag(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/item', json={'tag_id': 'default_tag'},
    )
    assert response.status_code == 200
    assert select_table_named(
        'config.tags', 'tag_id', pgsql['reposition'],
    ) == [{'tag_id': 1, 'tag_name': 'default_tag'}]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['tag_default.sql'])
def test_delete(taxi_reposition, pgsql):
    response = taxi_reposition.delete(
        '/v1/settings/tags/item?tag_id=default_tag',
    )
    assert response.status_code == 200
    assert (
        select_table_named('config.tags', 'tag_id', pgsql['reposition']) == []
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_delete_non_existent(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/tags/item?tag_id=nonexistent_tag',
    )
    assert response.status_code == 200
