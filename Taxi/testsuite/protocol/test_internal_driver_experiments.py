# -*- coding: utf-8 -*-
import pytest


@pytest.mark.config(TVM_ENABLED=False)
def test_empty(taxi_protocol):
    response = taxi_protocol.get(
        'internal/driver_experiments', params={'show_only_active': 'true'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'experiments': []}


@pytest.mark.driver_experiments('exp1')
@pytest.mark.driver_experiments('exp2')
@pytest.mark.driver_experiments(exp3={'active': False})
@pytest.mark.config(TVM_ENABLED=False)
def test_only_active_exps(taxi_protocol):
    response = taxi_protocol.get(
        'internal/driver_experiments', params={'show_only_active': 'true'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'experiments': ['exp1', 'exp2']}


@pytest.mark.driver_experiments('exp1')
@pytest.mark.driver_experiments('exp2')
@pytest.mark.driver_experiments(exp3={'active': False})
@pytest.mark.config(TVM_ENABLED=False)
def test_non_active_exps(taxi_protocol):
    response = taxi_protocol.get(
        'internal/driver_experiments', params={'show_only_active': 'false'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'experiments': ['exp1', 'exp2', 'exp3']}
