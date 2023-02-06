import json
import math

from dateutil import parser
import pytest
import pytz


async def test_tags(taxi_cctv_workers, pgsql):
    tag_table = dict()
    tag_ids = []

    # add tags
    for i in range(3):
        body = {'description': f'test_{i}'}
        response = await taxi_cctv_workers.post('/v1/tags/add', json=body)
        assert response.status_code == 200
        tag_id = response.json()['tag_id']
        assert tag_id is not None
        tag_table[tag_id] = f'test_{i}'
        tag_ids.append(tag_id)

    # no description
    response = await taxi_cctv_workers.post('/v1/tags/add', json={})
    assert response.status_code == 200
    tag_id = response.json()['tag_id']
    assert tag_id is not None
    tag_table[tag_id] = None
    tag_ids.append(tag_id)

    # check tags
    response = await taxi_cctv_workers.get('/v1/tags/list', json={})
    tags = response.json()['tags']
    assert len(tags) == 4
    for item in tags:
        assert item['id'] in tag_table
        if tag_table[item['id']] is None:
            assert 'description' not in item
        else:
            assert tag_table[item['id']] == item['description']

    person_tag_table = {
        'person_1': [tag_ids[0], tag_ids[1], tag_ids[2]],
        'person_2': [tag_ids[0]],
        'person_3': [tag_ids[1], tag_ids[2]],
    }
    tag_person_table = {
        tag_ids[0]: ['person_1', 'person_2'],
        tag_ids[1]: ['person_1', 'person_3'],
        tag_ids[2]: ['person_1', 'person_3'],
        tag_ids[3]: [],
    }
    # add persons for tags
    first = True
    for person, person_tags in person_tag_table.items():
        for item in person_tags:
            body = {'tag_id': item, 'person_id': person}
            response = await taxi_cctv_workers.post(
                '/v1/person/tag/add', json=body,
            )
            assert response.status_code == 200
            if first:
                # check that inserting existing binding doesn't break anything
                response = await taxi_cctv_workers.post(
                    '/v1/person/tag/add', json=body,
                )
                assert response.status_code == 200
                # incorrect requests
                body = {'tag_id': item}
                response = await taxi_cctv_workers.post(
                    '/v1/person/tag/add', json=body,
                )
                assert response.status_code == 400
                body = {'person_id': person}
                response = await taxi_cctv_workers.post(
                    '/v1/person/tag/add', json=body,
                )
                assert response.status_code == 400
                first = False

    # try to add unexistent tag to person
    body = {'tag_id': max(tag_ids) + 1, 'person_id': 'person_test'}
    response = await taxi_cctv_workers.post('/v1/person/tag/add', json=body)
    assert response.status_code == 404

    # check tags/persons
    for person, person_tags in person_tag_table.items():
        body = {'person_ids': [person]}
        response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
        assert response.status_code == 200
        tag_info = response.json()['tag_info']
        assert len(tag_info) == 1
        assert tag_info[0]['person_id'] == person
        tags = tag_info[0]['tags']
        tag_ids_for_person = []
        for item in tags:
            assert item['id'] in tag_table
            assert tag_table[item['id']] == item['description']
            tag_ids_for_person.append(item['id'])
        tag_ids_for_person.sort()
        assert tag_ids_for_person == person_tags

    for tag_id, tag_persons in tag_person_table.items():
        params = {'tag_id': tag_id}
        response = await taxi_cctv_workers.get(
            '/v1/tags/persons', params=params,
        )
        assert response.status_code == 200
        persons = response.json()['persons']
        persons.sort()
        assert persons == tag_persons

    # check for nonexistent person
    body = {'person_ids': ['person_10']}
    response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
    assert response.status_code == 200
    assert len(response.json()['tag_info']) == 1
    assert response.json()['tag_info'][0]['person_id'] == 'person_10'
    assert len(response.json()['tag_info'][0]['tags']) == 0

    # check for nonexistent tag
    params = {'tag_id': max(tag_ids) + 1}
    response = await taxi_cctv_workers.get('/v1/tags/persons', params=params)
    assert response.status_code == 200
    assert len(response.json()['persons']) == 0

    # incorrect requests

    response = await taxi_cctv_workers.get('/v1/tags/persons', params={})
    assert response.status_code == 400
    response = await taxi_cctv_workers.post('/v1/person/tags', json={})
    assert response.status_code == 400

    # remove tag
    params = {'tag_id': tag_ids[1]}
    response = await taxi_cctv_workers.post('/v1/tags/remove', params=params)
    assert response.status_code == 200
    tag_person_table.pop(tag_ids[1])
    for person, person_tags in person_tag_table.items():
        if tag_ids[1] in person_tags:
            person_tags.remove(tag_ids[1])

    params = {'tag_id': max(tag_ids) + 1}
    response = await taxi_cctv_workers.post('/v1/tags/remove', params=params)
    assert response.status_code == 404

    response = await taxi_cctv_workers.post('/v1/tags/remove', params={})
    assert response.status_code == 400

    # check tags/persons again
    for person, person_tags in person_tag_table.items():
        body = {'person_ids': [person]}
        response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
        assert response.status_code == 200
        tag_info = response.json()['tag_info']
        assert len(tag_info) == 1
        assert tag_info[0]['person_id'] == person
        tags = tag_info[0]['tags']
        tag_ids_for_person = []
        for item in tags:
            assert item['id'] in tag_table
            assert tag_table[item['id']] == item['description']
            tag_ids_for_person.append(item['id'])
        tag_ids_for_person.sort()
        assert tag_ids_for_person == person_tags

    for tag_id, tag_persons in tag_person_table.items():
        params = {'tag_id': tag_id}
        response = await taxi_cctv_workers.get(
            '/v1/tags/persons', params=params,
        )
        assert response.status_code == 200
        persons = response.json()['persons']
        persons.sort()
        assert persons == tag_persons

    # remove person from tag

    body = {'tag_id': tag_ids[2], 'person_id': 'person_1'}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 200
    tag_person_table[tag_ids[2]].remove('person_1')
    person_tag_table['person_1'].remove(tag_ids[2])

    body = {'tag_id': max(tag_ids) + 1, 'person_id': 'person_1'}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 404

    body = {'tag_id': tag_ids[2], 'person_id': 'person_10'}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 404

    body = {'tag_id': tag_ids[3], 'person_id': 'person_2'}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 404

    # incorrect requests
    body = {'tag_id': tag_ids[2]}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 400
    body = {'person_id': 'person_1'}
    response = await taxi_cctv_workers.post('/v1/person/tag/remove', json=body)
    assert response.status_code == 400

    # check tags/persons again
    for person, person_tags in person_tag_table.items():
        body = {'person_ids': [person]}
        response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
        assert response.status_code == 200
        tag_info = response.json()['tag_info']
        assert len(tag_info) == 1
        assert tag_info[0]['person_id'] == person
        tags = tag_info[0]['tags']
        tag_ids_for_person = []
        for item in tags:
            assert item['id'] in tag_table
            assert tag_table[item['id']] == item['description']
            tag_ids_for_person.append(item['id'])
        tag_ids_for_person.sort()
        assert tag_ids_for_person == person_tags

    for tag_id, tag_persons in tag_person_table.items():
        params = {'tag_id': tag_id}
        response = await taxi_cctv_workers.get(
            '/v1/tags/persons', params=params,
        )
        assert response.status_code == 200
        persons = response.json()['persons']
        persons.sort()
        assert persons == tag_persons

    # check cascade delete
    tag_ids.remove(tag_ids[1])
    for id in tag_ids:
        params = {'tag_id': id}
        response = await taxi_cctv_workers.post(
            '/v1/tags/remove', params=params,
        )
        assert response.status_code == 200

    cursor = pgsql['cctv_workers'].cursor()
    cursor.execute('SELECT * from cctv_workers.tags_persons')
    result = cursor.fetchall()
    assert len(result) == 0
    cursor.execute('SELECT * from cctv_workers.tags')
    result = cursor.fetchall()
    assert len(result) == 0
    cursor.execute('SELECT * from cctv_workers.actions_tags')
    result = cursor.fetchall()
    assert len(result) == 0


async def test_person_tags_bulk(taxi_cctv_workers):
    tag_table = dict()
    tag_ids = []

    # add tags
    for i in range(4):
        body = {'description': f'test_{i}'}
        response = await taxi_cctv_workers.post('/v1/tags/add', json=body)
        assert response.status_code == 200
        tag_id = response.json()['tag_id']
        assert tag_id is not None
        tag_table[tag_id] = f'test_{i}'
        tag_ids.append(tag_id)
    # no description
    response = await taxi_cctv_workers.post('/v1/tags/add', json={})
    assert response.status_code == 200
    tag_id = response.json()['tag_id']
    assert tag_id is not None
    tag_table[tag_id] = None
    tag_ids.append(tag_id)

    person_tag_table = {
        'person_1': [tag_ids[0], tag_ids[1], tag_ids[2], tag_ids[3]],
        'person_2': [tag_ids[0]],
        'person_3': [tag_ids[1], tag_ids[4], tag_ids[2]],
        'person_4': [],
    }

    # add persons for tags
    for person, person_tags in person_tag_table.items():
        for item in person_tags:
            body = {'tag_id': item, 'person_id': person}
            response = await taxi_cctv_workers.post(
                '/v1/person/tag/add', json=body,
            )
            assert response.status_code == 200

    # make bulk request
    body = {'person_ids': ['person_1', 'person_2', 'person_3', 'person_4']}
    response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
    assert response.status_code == 200
    tag_info = response.json()['tag_info']
    assert len(tag_info) == 4
    for item in tag_info:
        person_id = item['person_id']
        # check that person exists
        assert person_id in person_tag_table
        # check that it was requested
        assert person_id in body['person_ids']
        person_tags = person_tag_table[person_id]
        for tag in item['tags']:
            tag_id = tag['id']
            # check that tag exists
            assert tag_id in tag_table
            # check that person has this tag
            assert tag_id in person_tags
            # check that tag has correct description
            maybe_description = tag.get('description')
            if maybe_description is None:
                assert tag_table[tag_id] is None
            else:
                assert tag_table[tag_id] == maybe_description
    # too long list
    body = {'person_ids': []}
    for i in range(1001):
        body['person_ids'].append(f'person_{i}')
    response = await taxi_cctv_workers.post('/v1/person/tags', json=body)
    assert response.status_code == 400
