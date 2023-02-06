import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {attributesFactory, infoModelsFactory, TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import {IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';
import {createProductHandler} from 'server/routes/api/v1/products/create-product';
import {updateProductHandler} from 'server/routes/api/v1/products/update-product';
import {env} from 'service/cfg';
import {CommitHandler} from 'service/import/commit-handler';
import TankerProvider from 'service/tanker-provider';
import {Product, ProductStatus} from 'types/product';

import {processTaskQueue} from '..';

const mockUpsertKeysetWithRetry = jest.fn();
jest.mock('service/tanker-provider', () => {
    return jest.fn().mockImplementation(() => {
        return {upsertKeysetWithRetry: mockUpsertKeysetWithRetry};
    });
});

describe('tanker export', () => {
    let region: Region;
    let user: User;
    let context: ApiRequestContext;
    let langs: Lang[];

    let attributes: Attribute[];
    let infoModels: InfoModel[];
    let mc0: MasterCategory;
    let product: Product;

    beforeEach(async () => {
        langs = await Promise.all([TestFactory.createLang({isoCode: 'ru'}), TestFactory.createLang({isoCode: 'en'})]);
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
        region = await TestFactory.createRegion();
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});
        context = await TestFactory.createApiContext({lang: langs[0], user, region});

        attributes = await attributesFactory(user, [
            {type: AttributeType.STRING},
            {
                code: ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS + '1',
                type: AttributeType.STRING,
                isValueLocalizable: true
            },
            {
                code: ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS + '2',
                type: AttributeType.STRING,
                isValueLocalizable: true
            },
            {
                code: ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS + '3',
                type: AttributeType.STRING,
                isValueLocalizable: true
            }
        ]);
        infoModels = await infoModelsFactory(user, region, [
            [
                {id: attributes[0].id, isImportant: false},
                {id: attributes[1].id, isImportant: false},
                {id: attributes[2].id, isImportant: false},
                {id: attributes[3].id, isImportant: false}
            ]
        ]);

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModels[0].id
        });
        mc0 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            infoModelId: infoModels[0].id
        });

        product = await createProductHandler.handle({
            context,
            data: {
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abcOLD',
                            isConfirmed: false
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'foo1OLD',
                                [langs[1].isoCode]: 'bar1OLD'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[2].id,
                            value: {
                                [langs[0].isoCode]: 'foo2OLD',
                                [langs[1].isoCode]: 'bar2OLD'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[3].id,
                            value: {
                                [langs[0].isoCode]: 'foo3OLD',
                                [langs[1].isoCode]: 'bar3OLD'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        (TankerProvider as jest.Mock).mockClear();
        mockUpsertKeysetWithRetry.mockClear();
    });

    it('create product should push localizable attribute into tanker', async () => {
        const product = await createProductHandler.handle({
            context,
            data: {
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abc',
                            isConfirmed: false
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'foo1',
                                [langs[1].isoCode]: 'bar1'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[2].id,
                            value: {
                                [langs[0].isoCode]: 'foo2',
                                [langs[1].isoCode]: 'bar2'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[3].id,
                            value: {
                                [langs[0].isoCode]: 'foo3',
                                [langs[1].isoCode]: 'bar3'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls).toEqual([
            [
                {
                    keyset: `product:${ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS}Generated:${env}`,
                    keys: [
                        {
                            name: '' + product.identifier + ':1',
                            translations: {
                                ru: 'foo1',
                                en: 'bar1'
                            }
                        },
                        {
                            name: '' + product.identifier + ':2',
                            translations: {
                                ru: 'foo2',
                                en: 'bar2'
                            }
                        },
                        {
                            name: '' + product.identifier + ':3',
                            translations: {
                                ru: 'foo3',
                                en: 'bar3'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[1].code}:${env}`,
                    keys: [
                        {
                            name: '' + product.identifier,
                            translations: {
                                ru: 'foo1',
                                en: 'bar1'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[2].code}:${env}`,
                    keys: [
                        {
                            name: '' + product.identifier,
                            translations: {
                                ru: 'foo2',
                                en: 'bar2'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[3].code}:${env}`,
                    keys: [
                        {
                            name: '' + product.identifier,
                            translations: {
                                ru: 'foo3',
                                en: 'bar3'
                            }
                        }
                    ]
                }
            ]
        ]);
    });

    it('update product should push localizable attribute into tanker', async () => {
        const updatedProduct = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abcNEW',
                            isConfirmed: false
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'foo1NEW',
                                [langs[1].isoCode]: 'bar1NEW'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[2].id,
                            value: {
                                [langs[0].isoCode]: 'foo2NEW',
                                [langs[1].isoCode]: 'bar2NEW'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        },
                        {
                            attributeId: attributes[3].id,
                            value: {
                                [langs[0].isoCode]: 'foo3NEW',
                                [langs[1].isoCode]: 'bar3NEW'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: false
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls).toEqual([
            [
                {
                    keyset: `product:${ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS}Generated:${env}`,
                    keys: [
                        {
                            name: '' + product.identifier + ':1',
                            translations: {
                                ru: 'foo1NEW',
                                en: 'bar1NEW'
                            }
                        },
                        {
                            name: '' + product.identifier + ':2',
                            translations: {
                                ru: 'foo2NEW',
                                en: 'bar2NEW'
                            }
                        },
                        {
                            name: '' + product.identifier + ':3',
                            translations: {
                                ru: 'foo3NEW',
                                en: 'bar3NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[1].code}:${env}`,
                    keys: [
                        {
                            name: '' + updatedProduct.identifier,
                            translations: {
                                ru: 'foo1NEW',
                                en: 'bar1NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[2].code}:${env}`,
                    keys: [
                        {
                            name: '' + updatedProduct.identifier,
                            translations: {
                                ru: 'foo2NEW',
                                en: 'bar2NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[3].code}:${env}`,
                    keys: [
                        {
                            name: '' + updatedProduct.identifier,
                            translations: {
                                ru: 'foo3NEW',
                                en: 'bar3NEW'
                            }
                        }
                    ]
                }
            ]
        ]);
    });

    it('create product via import should push localizable attribute into tanker', async () => {
        const content = [
            [
                MASTER_CATEGORY_HEADER,
                attributes[0].code,
                `${attributes[1].code}|${langs[0].isoCode}`,
                `${attributes[1].code}|${langs[1].isoCode}`,
                `${attributes[2].code}|${langs[0].isoCode}`,
                `${attributes[2].code}|${langs[1].isoCode}`,
                `${attributes[3].code}|${langs[0].isoCode}`,
                `${attributes[3].code}|${langs[1].isoCode}`
            ],
            [mc0.code, 'abc', 'foo1', 'bar1', 'foo2', 'bar2', 'foo3', 'bar3']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();
        const productIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(productIdentifiers).toHaveLength(1);
        const productIds = commitHandler.getNewProductIds();
        expect(productIds).toHaveLength(1);

        // на первой итерации считается полнота и в ней создается новая задача на экспорт в танкер
        // поэтому необходим два раза обработать очередь
        await processTaskQueue();
        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls).toEqual([
            [
                {
                    keyset: `product:${ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS}Generated:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0] + ':1',
                            translations: {
                                ru: 'foo1',
                                en: 'bar1'
                            }
                        },
                        {
                            name: '' + productIdentifiers[0] + ':2',
                            translations: {
                                ru: 'foo2',
                                en: 'bar2'
                            }
                        },
                        {
                            name: '' + productIdentifiers[0] + ':3',
                            translations: {
                                ru: 'foo3',
                                en: 'bar3'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[1].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo1',
                                en: 'bar1'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[2].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo2',
                                en: 'bar2'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[3].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo3',
                                en: 'bar3'
                            }
                        }
                    ]
                }
            ]
        ]);
    });

    it('update product via import should push localizable attribute into tanker', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                attributes[0].code,
                `${attributes[1].code}|${langs[0].isoCode}`,
                `${attributes[1].code}|${langs[1].isoCode}`,
                `${attributes[2].code}|${langs[0].isoCode}`,
                `${attributes[2].code}|${langs[1].isoCode}`,
                `${attributes[3].code}|${langs[0].isoCode}`,
                `${attributes[3].code}|${langs[1].isoCode}`
            ],
            ['' + product.identifier, 'abcNEW', 'foo1NEW', 'bar1NEW', 'foo2NEW', 'bar2NEW', 'foo3NEW', 'bar3NEW']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();
        const productIdentifiers = commitHandler.getUpdatedProductIdentifiers();
        expect(productIdentifiers).toHaveLength(1);

        await processTaskQueue();
        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls).toEqual([
            [
                {
                    keyset: `product:${ATTRIBUTES_CODES.TITLE_DETAILED_INGREDIENTS}Generated:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0] + ':1',
                            translations: {
                                ru: 'foo1NEW',
                                en: 'bar1NEW'
                            }
                        },
                        {
                            name: '' + productIdentifiers[0] + ':2',
                            translations: {
                                ru: 'foo2NEW',
                                en: 'bar2NEW'
                            }
                        },
                        {
                            name: '' + productIdentifiers[0] + ':3',
                            translations: {
                                ru: 'foo3NEW',
                                en: 'bar3NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[1].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo1NEW',
                                en: 'bar1NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[2].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo2NEW',
                                en: 'bar2NEW'
                            }
                        }
                    ]
                }
            ],
            [
                {
                    keyset: `product:${attributes[3].code}:${env}`,
                    keys: [
                        {
                            name: '' + productIdentifiers[0],
                            translations: {
                                ru: 'foo3NEW',
                                en: 'bar3NEW'
                            }
                        }
                    ]
                }
            ]
        ]);
    });
});
