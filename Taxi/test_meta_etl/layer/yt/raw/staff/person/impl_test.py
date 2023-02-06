import unittest.mock

import pytest

import meta_etl.layer.yt.raw.staff.person.impl


@pytest.mark.parametrize(
    'persons,expected', [
        ([{
            'doc': {
                'id': 1,
                'phones': [{
                    'number': '+79991234567',
                }]
            }
        }],
         [{
             'phone': {
                 'number': '+79991234567',
                 'phone_normalized': '+79991234567',
             },
             'person': {
                 'doc': {
                     'id': 1,
                 }
             }
         }]),
        ([{
            'doc': {
                'id': 1,
                'phones': [{
                    'number': '+79991234567',
                }, {
                    'number': '+79901234567',
                }],
            }
        }],
         [{
             'phone': {
                 'number': '+79991234567',
                 'phone_normalized': '+79991234567',
             },
             'person': {
                 'doc': {
                     'id': 1,
                 }
             }
         }, {
             'phone': {
                 'number': '+79901234567',
                 'phone_normalized': '+79901234567',
             },
             'person': {
                 'doc': {
                     'id': 1,
                 }
             }
         }]),
        ([{
            'doc': {
                'id': 1,
                'phones': []
            }
        }],
         [{
             'phone': {
                 'number': None,
                 'phone_normalized': None,
             },
             'person': {
                 'doc': {
                     'id': 1,
                 }
             }
         }]),
        ([{
            'doc': {
                'id': 1,
                'phones': [{
                    'number': '+79991234567',
                }]
            }
        }, {
            'doc': {
                'id': 2,
                'phones': [{
                    'number': '+79901234567',
                }]
            }
        }],
         [{
             'phone': {
                 'number': '+79991234567',
                 'phone_normalized': '+79991234567',
             },
             'person': {
                 'doc': {
                     'id': 1,
                 }
             }
         }, {
             'phone': {
                 'number': '+79901234567',
                 'phone_normalized': '+79901234567',
             },
             'person': {
                 'doc': {
                     'id': 2,
                 }
             }
         }]),
    ]
)
def test_extract_phones(persons, expected):
    actual = list(meta_etl.layer.yt.raw.staff.person.impl.extract_phones(persons))
    assert actual == expected


@pytest.mark.parametrize(
    'persons,expected', [
        ([{
            'phone': {
                'number': '+79991234567',
                'phone_normalized': '+79991234567',
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }], [{
            'phone': {
                'number': '+79991234567',
                'phone_normalized': '+79991234567',
                'phone_pd_id': 'pd_id_1',
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }]),
        ([{
            'phone': {
                'number': 'some rubbish phone',
                'phone_normalized': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }], [{
            'phone': {
                'number': 'some rubbish phone',
                'phone_normalized': None,
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }]),
        ([{
            'phone': {
                'number': '+70991234567',
                'phone_normalized': '+70991234567',
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }], [{
            'phone': {
                'number': '+70991234567',
                'phone_normalized': '+70991234567',
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }]),
    ]
)
def test_enrich_pd_id(mock_get_pd_id_mapping, persons, expected):
    actual = list(meta_etl.layer.yt.raw.staff.person.impl.enrich_pd_id(
        persons,
        unittest.mock.MagicMock,
    ))
    assert actual == expected


@pytest.mark.parametrize(
    'persons,expected', [
        ([{
            'phone': {
                'number': '+79991234567',
                'phone_normalized': '+79991234567',
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }, {
            'phone': {
                'number': '+70991234567',
                'phone_normalized': '+70991234567',
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 2,
                }
            }
        }], [{
            'doc': {
                'id': 1,
                'phones': [{
                    'number': '+79991234567',
                    'phone_normalized': '+79991234567',
                    'phone_pd_id': None,
                }],
            }
        }, {
            'doc': {
                'id': 2,
                'phones': [{
                    'number': '+70991234567',
                    'phone_normalized': '+70991234567',
                    'phone_pd_id': None,
                }],
            }
        }]),
        ([{
            'phone': {
                'number': None,
                'phone_normalized': None,
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }], [{
            'doc': {
                'id': 1,
                'phones': [],
            }
        }]),
        ([{
            'phone': {
                'number': '+79991234567',
                'phone_normalized': '+79991234567',
                'phone_pd_id': 'pd_id',
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }, {
            'phone': {
                'number': '+70991234567',
                'phone_normalized': '+70991234567',
                'phone_pd_id': None,
            },
            'person': {
                'doc': {
                    'id': 1,
                }
            }
        }], [{
            'doc': {
                'id': 1,
                'phones': [{
                    'number': '+79991234567',
                    'phone_normalized': '+79991234567',
                    'phone_pd_id': 'pd_id',
                }, {
                    'number': '+70991234567',
                    'phone_normalized': '+70991234567',
                    'phone_pd_id': None,
                }],
            }
        }]),
    ]
)
def test_merge_person_by_phone(persons, expected):
    actual = list(meta_etl.layer.yt.raw.staff.person.impl.merge_person_by_phone(persons))
    assert actual == expected
