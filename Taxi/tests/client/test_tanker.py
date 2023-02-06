from stall.client.tanker import TankerKeyset


async def test_from_db_groups(tap, dataset):
    with tap:
        groups = [
            await dataset.product_group(
                vars={
                    'locales': {
                        'name': {
                            'ru_RU': 'foo',
                            'en_US': 'foo',
                        },
                    },
                },
            ),
            await dataset.product_group(
                vars={
                    'locales': {
                        'name': {
                            'ru': 'bar',
                            'en': 'bar',
                        },
                    },
                },
            ),
            await dataset.product_group(
                vars={
                    'locales': {
                        'name': {
                            'he_XY': 'baz',
                        },
                    },
                },
            ),
        ]
        keyset = TankerKeyset.from_db(
            groups,
            'group_id',
            'project_id',
            'keyset_id',
            {'name'},
            {'ru', 'en'},
        )

        tap.eq(
            keyset.keys,
            {
                f'{groups[0].group_id}_name': {
                    'translations': {
                        'ru': {'form': 'foo'},
                        'en': {'form': 'foo'},
                    },
                    'info': {}
                },
                f'{groups[1].group_id}_name': {
                    'translations': {
                        'ru': {'form': 'bar'},
                        'en': {'form': 'bar'},
                    },
                    'info': {}
                },
            },
            'группы только на русском и английсокм',
        )


async def test_from_db_synonyms(tap, dataset):
    with tap:
        groups = [
            await dataset.product_group(
                vars={
                    'locales': {
                        'synonyms': {
                            'ru_RU': 'foo_ru',
                            'en_US': 'foo_en',
                        },
                        'description': {
                            'ru_RU': 'cool description'
                        }
                    },
                },
            ),
            await dataset.product_group(
                vars={
                    'locales': {
                        'synonyms': {
                            'en': 'bar_en',
                        },
                        'title': {
                            'en': 'title en'
                        }
                    },
                },
            ),
        ]
        keyset = TankerKeyset.from_db(
            groups,
            'group_id',
            'project_id',
            'keyset_id_2',
            {'synonyms'},
            {'ru', 'en', 'cz'},
        )

        tap.eq(
            keyset.keys,
            {
                f'{groups[0].group_id}_synonyms': {
                    'translations': {
                        'en': {'form': 'foo_en'},
                        'ru': {'form': 'foo_ru'}
                    },
                    'info': {}
                },
                f'{groups[1].group_id}_synonyms': {
                    'translations': {
                        'en': {'form': 'bar_en'},
                        'ru': {'form': ''}
                    },
                    'info': {}
                },
            },
            'синоним ключи правильные',
        )


async def test_from_db_new_tanker_logic(tap, dataset):
    with tap:
        groups = [
            # есть дефолт перевод
            await dataset.product_group(
                vars={
                    'locales': {
                        'name': {
                            'ru_RU': 'foo_ru',
                            'en_US': 'foo_en',
                        },
                    },
                },
            ),

            # недостающий дефолтный перевод
            await dataset.product_group(
                vars={
                    'locales': {
                        'name': {
                            'en': 'bar_en',
                        },
                    },
                },
            ),
        ]
        keyset = TankerKeyset.from_db(
            groups,
            'group_id',
            'project_id',
            'keyset_id',
            {'name'},
            {'ru', 'en', 'cz'},
        )

        tap.eq(
            keyset.keys,
            {
                f'{groups[0].group_id}_name': {
                    'translations': {
                        'en': {'form': 'foo_en'},
                        'ru': {'form': 'foo_ru'}
                    },
                    'info': {}
                },
                f'{groups[1].group_id}_name': {
                    'translations': {
                        'en': {'form': 'bar_en'},
                        'ru': {'form': ''}
                    },
                    'info': {}
                },
            },
            'работа фолбэк логики',
        )


async def test_from_db_products(tap, dataset):
    with tap:
        products = [
            await dataset.product(
                vars={
                    'locales': {
                        'title': {
                            'ru_RU': 'foo',
                            'en_US': 'foo',
                        },
                        'long_title': {
                            'ru_RU': 'foo',
                            'en_US': 'foo',
                        },
                        'description': {
                            'ru_RU': 'foo',
                            'en_US': 'foo',
                        },
                    },
                },
            ),
            await dataset.product(
                vars={
                    'locales': {
                        'title': {
                            'ru_RU': 'bar',
                        },
                        'long_title': {
                            'en_US': 'bar',
                        },
                        'description': {
                            'he': 'bar',
                        }
                    },
                },
            ),
            await dataset.product(
                vars={
                    'locales': {},
                },
            ),
        ]
        keyset = TankerKeyset.from_db(
            products,
            'product_id',
            'project_id',
            'keyset_id',
            {'title', 'long_title'},
            {'ru', 'en', 'he'}
        )

        tap.eq(
            keyset.keys,
            {
                f'{products[0].product_id}_title': {
                    'translations': {
                        'ru': {'form': 'foo'},
                        'en': {'form': 'foo'},
                    },
                    'info': {}
                },
                f'{products[0].product_id}_long_title': {
                    'translations': {
                        'ru': {'form': 'foo'},
                        'en': {'form': 'foo'},
                    },
                    'info': {}
                },
                f'{products[1].product_id}_title': {
                    'translations': {
                        'ru': {'form': 'bar'},
                    },
                    'info': {}
                },
                f'{products[1].product_id}_long_title': {
                    'translations': {
                        'en': {'form': 'bar'},
                        'ru': {'form': ''}
                    },
                    'info': {}
                },
            },
            'товары на трех языках',
        )


def test_keyset_diff_keys(tap):
    with tap.plan(4, 'сравнение кисетов'):
        keyset = TankerKeyset(
            {
                'foo': {
                    'translations': {
                        'ru': {'form': 'ru foo'},
                        'en': {'form': 'en foo'},
                    }
                },
                'bar': {
                    'translations': {
                        'ru': {'form': 'ru bar'},
                        'en': {'form': 'en bar'},
                        'he': {'form': 'he bar'},
                    }
                },
                'spam': {
                    'translations': {
                        'ru': {'form': 'ru spam'},
                        'en': {'form': 'en spam'},
                        'xx': {'form': 'xx spam'},
                    }
                },
            },
            'project_id',
            'keyset_id',
            {'ru', 'en'},
        )

        new, updated, removed, not_updated = keyset.diff_keys(
            {
                'foo': {
                    'translations': {
                        'ru': {'form': 'ru foo 2'},
                        'en': {'form': 'en foo'},
                    }
                },
                'spam': {
                    'translations': {
                        'ru': {'form': 'ru spam'},
                        'en': {'form': 'en spam'},
                        'xx': {'form': 'xx spam'},
                    }
                },
                'new': {
                    'translations': {
                        'ru': {'form': 'ru new'},
                        'en': {'form': 'en new'},
                    }
                },
            }
        )

        tap.eq(
            new,
            {
                'new': {
                    'translations': {
                        'ru': {'form': 'ru new'},
                        'en': {'form': 'en new'},
                    }
                }
            },
            'новые переводы',
        )
        tap.eq(
            updated,
            {
                'foo': {
                    'translations': {
                        'ru': {'form': 'ru foo 2'},
                        'en': {'form': 'en foo'},
                    }
                },
            },
            'измененные переводы',
        )
        tap.eq(
            removed,
            {
                'bar': {
                    'translations': {
                        'ru': {'form': 'ru bar'},
                        'en': {'form': 'en bar'},
                        'he': {'form': 'he bar'},
                    }
                },
            },
            'удаленные переводы',
        )
        tap.eq(
            not_updated,
            {
                'spam': {
                    'translations': {
                        'ru': {'form': 'ru spam'},
                        'en': {'form': 'en spam'},
                        'xx': {'form': 'xx spam'},
                    }
                }
            },
            'прочие переводы',
        )


def test_keyset_chunks(tap):
    with tap:
        keyset = TankerKeyset(
            {
                '1': {'translations': {'ru': {'form': 'ru'}}},
                '2': {'translations': {'ru': {'form': 'ru'}}},
                '3': {'translations': {'ru': {'form': 'ru'}}},
            },
            'project_id',
            'keyset_id',
            {'ru'},
        )

        chunks = list(keyset.chunks(2))

        tap.eq(len(chunks), 2, 'две пачки')
        tap.eq(
            chunks[0],
            {
                '1': {'translations': {'ru': {'form': 'ru'}}},
                '2': {'translations': {'ru': {'form': 'ru'}}},
            },
            'первая пачка',
        )
        tap.eq(
            chunks[1],
            {
                '3': {'translations': {'ru': {'form': 'ru'}}},
            },
            'вторая пачка',
        )
