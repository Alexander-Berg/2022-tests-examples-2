import json

import pytest


def validate_candidate(cand):
    req_fields = {
        'ml_score': float,
        'exact': bool,
        'full_text': (str, unicode),
        'point': list
    }
    for field_name, field_type in req_fields.items():
        assert field_name in cand
        assert isinstance(cand[field_name], field_type)


@pytest.mark.skip(reason="should be fixed in TAXIML-850")
def test_empty_request(taxi_pyml):
    response = taxi_pyml.get('expected_source', json={})
    assert response.status_code == 400


def test_2_candidates(taxi_pyml, load_json):
    response = taxi_pyml.get('expected_source', json=load_json('request.json'))
    assert response.status_code == 200
    data = json.loads(response.data)
    candidates = data.get('candidates', [])
    assert len(data.get('candidates', [])) == 2
    for cand in candidates:
        validate_candidate(cand)
