import pytest

from dmp_suite.http.session_utils import SessionWithRetries
from dmp_suite.qolio import qolio_api


@pytest.mark.parametrize(
    'reviews, included, expected_result',
    [
        pytest.param(
            [
                {
                    "id": "review1",
                    "type": "reviews",
                    "attributes": {
                        "created-at": "2021-09-01T20:52:28.568Z"
                    },
                    "relationships": {
                        "checklist": {
                            "data": {
                                "id": "checklist1",
                                "type": "checklists"
                            }
                        },
                        "operator": {
                            "data": {
                                "id": "operator1",
                                "type": "users"
                            }
                        },
                        "client-interaction": {
                            "data": None
                        }
                    }
                },
                {
                    "id": "review2",
                    "type": "reviews",
                    "attributes": {
                        "created-at": "2021-09-01T19:50:23.993Z"
                    },
                    "relationships": {
                        "checklist": {
                            "data": {
                                "id": "checklist2",
                                "type": "checklists"
                            }
                        },
                        "operator": {
                            "data": {
                                "id": "operator2",
                                "type": "users"
                            }
                        },
                        "client-interaction": {
                            "data": {
                                "id": "interaction2",
                                "type": "client-interactions"
                            }
                        }
                    }
                }
            ],
            [
                {
                    "id": "checklist1",
                    "type": "checklists"
                },
                {
                    "id": "operator1",
                    "type": "users"
                },
                {
                    "id": "checklist2",
                    "type": "checklists"
                },
                {
                    "id": "operator2",
                    "type": "users"
                },
                {
                    "id": "interaction2",
                    "type": "client-interactions"
                }
            ],
            [
                {
                    "id": "review1",
                    "type": "reviews",
                    "attributes": {
                        "created-at": "2021-09-01T20:52:28.568Z"
                    },
                    "relationships": {
                        "checklist": {
                            "data": {
                                "id": "checklist1",
                                "type": "checklists"
                            }
                        },
                        "operator": {
                            "data": {
                                "id": "operator1",
                                "type": "users"
                            }
                        },
                        "client-interaction": {
                            "data": None
                        }
                    },
                    "checklist": {
                        "id": "checklist1",
                        "type": "checklists"
                    },
                    "operator": {
                        "id": "operator1",
                        "type": "users"
                    },
                    "client_interaction": None,
                    "created_at": "2021-09-01T20:52:28.568Z"
                },
                {
                    "id": "review2",
                    "type": "reviews",
                    "attributes": {
                        "created-at": "2021-09-01T19:50:23.993Z"
                    },
                    "relationships": {
                        "checklist": {
                            "data": {
                                "id": "checklist2",
                                "type": "checklists"
                            }
                        },
                        "operator": {
                            "data": {
                                "id": "operator2",
                                "type": "users"
                            }
                        },
                        "client-interaction": {
                            "data": {
                                "id": "interaction2",
                                "type": "client-interactions"
                            }
                        }
                    },
                    "checklist": {
                        "id": "checklist2",
                        "type": "checklists"
                    },
                    "operator": {
                        "id": "operator2",
                        "type": "users"
                    },
                    "client_interaction": {
                        "id": "interaction2",
                        "type": "client-interactions"
                    },
                    "created_at": "2021-09-01T19:50:23.993Z"
                }
            ],
            id='basic test'),
        ]
    )
def test_parse_client_interaction_review_response(reviews, included, expected_result):
    api = qolio_api.ApiWrapper(SessionWithRetries(), 'base_url', 'email', 'password')
    result = api.parse_client_interaction_review_response(reviews, included)

    assert result == expected_result
