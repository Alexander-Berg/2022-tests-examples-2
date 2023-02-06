/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {attributesFactory, infoModelsFactory, TestFactory} from 'tests/unit/test-factory';

import {IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import {getProductByIdentifier} from '@/src/entities/product/api/get-product-by-identifier';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';
import {updateInfoModelHandler} from 'server/routes/api/v1/info-models/update-info-model';
import {updateMasterCategoryHandler} from 'server/routes/api/v1/master-categories/update-master-category';
import {createProductHandler} from 'server/routes/api/v1/products/create-product';
import {updateProductHandler} from 'server/routes/api/v1/products/update-product';
import {CommitHandler} from 'service/import/commit-handler';
import {Product, ProductStatus} from 'types/product';

import {processTaskQueue, pushTask, QUEUES, SOURCES} from '..';

describe('product fullness', () => {
    let region: Region;
    let user: User;
    let context: ApiRequestContext;
    let langs: Lang[];

    beforeEach(async () => {
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        user = await TestFactory.createUser({
            rules: {product: {canEdit: true}, masterCategory: {canEdit: true}, infoModel: {canEdit: true}}
        });
        region = await TestFactory.createRegion();
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});
        context = await TestFactory.createApiContext({lang: langs[0], user, region});
    });

    describe('base cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let mc2: MasterCategory;
        let mc3: MasterCategory;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.BOOLEAN},
                {type: AttributeType.NUMBER},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id, isImportant: false}],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
                ],
                [
                    // no attributes
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
            mc1 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[1].id
            });
            mc2 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[2].id
            });
            mc3 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[3].id
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1, mc2, mc3].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('product fullness with info-model with 0 attributes should be equal 100%', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
            expect(product.fullness).toEqual(100);
        });

        it('product fullness with info-model with 0 important attributes should be equal 100%', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc0.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
            expect(product.fullness).toEqual(100);
        });

        it('fill more important attributes should change fullness', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc2.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            }
                        ]
                    }
                }
            });
            expect(product.fullness).toEqual(25);

            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc2.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22
                            },
                            {
                                attributeId: attributes[3].id,
                                value: ['33a', '33b']
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            expect(updatedProduct.fullness).toEqual(100);
        });

        it('boolean attribute should affect fullness', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc1.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            }
                        ]
                    }
                }
            });
            expect(product.fullness).toEqual(33);

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc1.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[0].id,
                                    value: '00'
                                },
                                {
                                    attributeId: attributes[1].id,
                                    value: true
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(67);
            }

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc1.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[0].id,
                                    value: '00'
                                },
                                {
                                    attributeId: attributes[2].id,
                                    value: 22
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(67);
            }
        });

        it('array attribute items should count once', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc2.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22
                            },
                            {
                                attributeId: attributes[3].id,
                                value: ['33a', '33b']
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            expect(product.fullness).toEqual(100);

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc2.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[0].id,
                                    value: '00'
                                },
                                {
                                    attributeId: attributes[2].id,
                                    value: 22
                                },
                                {
                                    attributeId: attributes[3].id,
                                    value: ['33a']
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(75);
            }

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc2.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[0].id,
                                    value: '00'
                                },
                                {
                                    attributeId: attributes[2].id,
                                    value: 22
                                },
                                {
                                    attributeId: attributes[3].id,
                                    value: []
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(50);
            }

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc2.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[0].id,
                                    value: '00'
                                },
                                {
                                    attributeId: attributes[3].id,
                                    value: []
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(25);
            }

            {
                const updatedProduct = await updateProductHandler.handle({
                    context,
                    data: {
                        params: {
                            identifier: product.identifier
                        },
                        body: {
                            status: ProductStatus.ACTIVE,
                            masterCategoryId: mc2.id,
                            frontCategoryIds: [],
                            attributes: [
                                {
                                    attributeId: attributes[3].id,
                                    value: []
                                }
                            ]
                        }
                    }
                });
                expect(updatedProduct.fullness).toEqual(0);
            }
        });
    });

    describe('change info-model cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let product: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.NUMBER},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true}
                ]
            ]);

            const mcRoot = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                infoModelId: infoModels[0].id
            });
            const mc = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[1].id
            });

            product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11
                            },
                            {
                                attributeId: attributes[2].id,
                                value: ['22a']
                            }
                        ]
                    }
                }
            });
        });

        it('add one not important attribute should not change fullness', async () => {
            expect(product.fullness).toEqual(75);

            await updateInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: infoModels[1].id
                    },
                    body: {
                        titleTranslations: {},
                        descriptionTranslations: {},
                        attributes: {
                            custom: [
                                {id: attributes[0].id, isImportant: true},
                                {id: attributes[1].id, isImportant: true},
                                {id: attributes[2].id, isImportant: true},
                                {id: attributes[3].id, isImportant: true},
                                {id: attributes[4].id, isImportant: false}
                            ]
                        }
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [product.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(75);
        });

        it('add one important attribute should change fullness', async () => {
            expect(product.fullness).toEqual(75);

            await updateInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: infoModels[1].id
                    },
                    body: {
                        titleTranslations: {},
                        descriptionTranslations: {},
                        attributes: {
                            custom: [
                                {id: attributes[0].id, isImportant: true},
                                {id: attributes[1].id, isImportant: true},
                                {id: attributes[2].id, isImportant: true},
                                {id: attributes[3].id, isImportant: true},
                                {id: attributes[4].id, isImportant: true}
                            ]
                        }
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [product.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(60);
        });

        it('switch importance of some attributes should change fullness', async () => {
            expect(product.fullness).toEqual(75);

            await updateInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: infoModels[1].id
                    },
                    body: {
                        titleTranslations: {},
                        descriptionTranslations: {},
                        attributes: {
                            custom: [
                                {id: attributes[0].id, isImportant: true},
                                {id: attributes[1].id, isImportant: false},
                                {id: attributes[2].id, isImportant: false},
                                {id: attributes[3].id, isImportant: true}
                            ]
                        }
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [product.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [product.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(50);
        });
    });

    describe('change master-category cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let product: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[2].id, isImportant: false},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
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
            mc1 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[1].id
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
                                value: '00'
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('change to another MC should change fullness', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(75);
            }
            const oldMasterCategoryId = product.masterCategory.id;

            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc1.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            const newMasterCategoryId = updatedProduct.masterCategory.id;
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [product.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [newMasterCategoryId, oldMasterCategoryId]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [newMasterCategoryId, oldMasterCategoryId]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(50);
            }
        });
    });

    describe('change via import cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let product: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[2].id, isImportant: false},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
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
            mc1 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[1].id
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
                                value: '00'
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('create product with important attributes should calculate fullness', async () => {
            const content = [
                [MASTER_CATEGORY_HEADER, attributes[0].code],
                ['' + mc0.code, '00']
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
            expect(newProductIdentifiers).toHaveLength(1);
            const newProductIds = commitHandler.getNewProductIds();
            expect(newProductIds).toHaveLength(1);
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [...newProductIdentifiers]
                    }
                }
            ]);
            await processTaskQueue();
            expect((await TestFactory.getProductFullness(newProductIds[0])).fullness).toEqual(25);
        });

        it('update product important attributes should change fullness', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(75);
            }

            const content = [
                [IDENTIFIER_HEADER, attributes[3].code],
                ['' + product.identifier, '33']
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(100);
            }
        });

        it('update product MC should change fullness', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(75);
            }
            const oldMasterCategoryCode = product.masterCategory.code;

            const content = [
                [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
                ['' + product.identifier, mc1.code]
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY_CODE,
                        masterCategoryCodes: [oldMasterCategoryCode]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY_CODE,
                        masterCategoryCodes: [oldMasterCategoryCode]
                    }
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductFullness(p!.id)).fullness).toEqual(50);
            }
        });
    });

    describe('localization', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let mc2: MasterCategory;
        let mc3: MasterCategory;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.TEXT, isValueLocalizable: true},
                {type: AttributeType.STRING, isValueLocalizable: true}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    // no attributes
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[1].id, isImportant: false}
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
            mc1 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[1].id
            });
            mc2 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[2].id
            });
            mc3 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id,
                infoModelId: infoModels[3].id
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1, mc2].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('product localization with info-model with 0 attributes should be equal 100%', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc0.id
            });

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness = await TestFactory.getProductFullness(p.id);

            expect(fullness).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 0,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });
        });

        it('product localization with info-model with 0 important attributes should be equal 100%', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc1.id
            });

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness = await TestFactory.getProductFullness(p.id);

            expect(fullness).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 0,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });
        });

        it('fill more important attributes should change localization', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc2.id
            });

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness1 = await TestFactory.getProductFullness(p.id);

            expect(fullness1).toMatchObject({
                langTotalFullness: 0,
                langFullness: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[1].id,
                    value: '00'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness2 = await TestFactory.getProductFullness(p.id);

            expect(fullness2).toMatchObject({
                langTotalFullness: 50,
                langFullness: {
                    [langs[0].isoCode]: 50,
                    [langs[1].isoCode]: 50
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 1,
                    [langs[1].isoCode]: 1
                }
            });
        });

        it('product localization without completely filled locales should be equal 0%', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc2.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[1].id,
                    value: '11'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness = await TestFactory.getProductFullness(p.id);

            expect(fullness).toMatchObject({
                langTotalFullness: 0,
                langFullness: {
                    [langs[0].isoCode]: 50,
                    [langs[1].isoCode]: 50
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 1,
                    [langs[1].isoCode]: 1
                }
            });
        });

        it('delete one important attribute from info-model should change fullness', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc2.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[0].id,
                    value: '11'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[1].id,
                    value: '11'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness1 = await TestFactory.getProductFullness(p.id);

            expect(fullness1).toMatchObject({
                langTotalFullness: 50,
                langFullness: {
                    [langs[0].isoCode]: 50,
                    [langs[1].isoCode]: 50
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 1,
                    [langs[1].isoCode]: 1
                }
            });

            await updateInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: infoModels[2].id
                    },
                    body: {
                        titleTranslations: {},
                        descriptionTranslations: {},
                        attributes: {
                            custom: [{id: attributes[0].id, isImportant: true}]
                        }
                    }
                }
            });

            await processTaskQueue();

            const fullness2 = await TestFactory.getProductFullness(p.id);

            expect(fullness2).toMatchObject({
                langTotalFullness: 0,
                langFullness: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                },
                langTotalAttributes: 1,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });
        });

        it('add one important attribute to info-model should change fullness', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc1.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[1].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[0].id,
                    value: '11'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[1].id,
                    value: '11'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness1 = await TestFactory.getProductFullness(p.id);

            expect(fullness1).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 0,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });

            await updateInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: infoModels[1].id
                    },
                    body: {
                        titleTranslations: {},
                        descriptionTranslations: {},
                        attributes: {
                            custom: [
                                {id: attributes[0].id, isImportant: true},
                                {id: attributes[1].id, isImportant: false}
                            ]
                        }
                    }
                }
            });

            await processTaskQueue();

            const fullness2 = await TestFactory.getProductFullness(p.id);

            expect(fullness2).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 1,
                langFilledAttributes: {
                    [langs[0].isoCode]: 1,
                    [langs[1].isoCode]: 1
                }
            });
        });

        it('change info-model should change product fullness', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc1.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[1].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[0].id,
                    value: '11'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[1].id,
                    value: '11'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness1 = await TestFactory.getProductFullness(p.id);

            expect(fullness1).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 0,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });

            await updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: mc1.id
                    },
                    body: {
                        infoModelId: infoModels[2].id
                    }
                }
            });

            await processTaskQueue();

            const fullness2 = await TestFactory.getProductFullness(p.id);

            expect(fullness2).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 2,
                    [langs[1].isoCode]: 2
                }
            });
        });

        it('change master-category should change product fullness', async () => {
            const p = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc1.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[0].id,
                    langId: langs[1].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[0].id,
                    value: '11'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p.id,
                    attributeId: attributes[1].id,
                    langId: langs[1].id,
                    value: '11'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness1 = await TestFactory.getProductFullness(p.id);

            expect(fullness1).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 0,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 0
                }
            });

            await TestFactory.updateProduct(p.id, {
                userId: user.id,
                product: {
                    masterCategoryId: mc2.id
                }
            });

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p.id]
            });

            await processTaskQueue();

            const fullness2 = await TestFactory.getProductFullness(p.id);

            expect(fullness2).toMatchObject({
                langTotalFullness: 100,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 2,
                langFilledAttributes: {
                    [langs[0].isoCode]: 2,
                    [langs[1].isoCode]: 2
                }
            });
        });

        it('product localization with 1 attribute with 1 filled locale should be equal 0%', async () => {
            const [p1, p2] = await Promise.all([
                TestFactory.createProduct({
                    userId: user.id,
                    regionId: region.id,
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc3.id
                }),
                TestFactory.createProduct({
                    userId: user.id,
                    regionId: region.id,
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc3.id
                })
            ]);

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p1.id,
                    attributeId: attributes[0].id,
                    langId: langs[0].id,
                    value: '00'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: p2.id,
                    attributeId: attributes[0].id,
                    langId: langs[1].id,
                    value: '00'
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_FULLNESS,
                source: SOURCES.PRODUCT,
                productIds: [p1.id, p2.id]
            });

            await processTaskQueue();

            const [fullness1, fullness2] = await Promise.all([
                TestFactory.getProductFullness(p1.id),
                TestFactory.getProductFullness(p2.id)
            ]);

            expect(fullness1).toMatchObject({
                langTotalFullness: 0,
                langFullness: {
                    [langs[0].isoCode]: 100,
                    [langs[1].isoCode]: 0
                },
                langTotalAttributes: 1,
                langFilledAttributes: {
                    [langs[0].isoCode]: 1,
                    [langs[1].isoCode]: 0
                }
            });

            expect(fullness2).toMatchObject({
                langTotalFullness: 0,
                langFullness: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 100
                },
                langTotalAttributes: 1,
                langFilledAttributes: {
                    [langs[0].isoCode]: 0,
                    [langs[1].isoCode]: 1
                }
            });
        });
    });
});
