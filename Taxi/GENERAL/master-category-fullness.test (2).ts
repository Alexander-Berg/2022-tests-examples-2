import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {attributesFactory, infoModelsFactory, TestFactory} from 'tests/unit/test-factory';

import {IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';
import {createMasterCategoryHandler} from 'server/routes/api/v1/master-categories/create-master-category';
import {updateMasterCategoryHandler} from 'server/routes/api/v1/master-categories/update-master-category';
import {createProductHandler} from 'server/routes/api/v1/products/create-product';
import {updateProductHandler} from 'server/routes/api/v1/products/update-product';
import {CommitHandler} from 'service/import/commit-handler';
import {MasterCategoryStatus, NewMasterCategory} from 'types/master-category';
import {Product, ProductStatus} from 'types/product';

import {processTaskQueue, pushTask, QUEUES, SOURCES} from '..';

describe('master-category fullness', () => {
    let region: Region;
    let user: User;
    let context: ApiRequestContext;

    beforeEach(async () => {
        const lang = await TestFactory.createLang();
        user = await TestFactory.createUser({rules: {product: {canEdit: true}, masterCategory: {canEdit: true}}});
        region = await TestFactory.createRegion();
        await TestFactory.createLocale({regionId: region.id, langIds: [lang.id]});
        context = await TestFactory.createApiContext({lang, user, region});
    });

    describe('base cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mcRoot: MasterCategory;
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let mc2: MasterCategory;
        let mc3: MasterCategory;
        let mc3a: MasterCategory;
        let mc3b: MasterCategory;
        let product1: Product;
        let product2: Product;
        let product3: Product;
        let product4: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.BOOLEAN},
                {type: AttributeType.NUMBER},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false},
                    {id: attributes[5].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[4].id, isImportant: false},
                    {id: attributes[5].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[3].id, isImportant: false},
                    {id: attributes[4].id, isImportant: true},
                    {id: attributes[5].id, isImportant: false}
                ]
            ]);

            mcRoot = await TestFactory.createMasterCategory({
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
                parentId: mcRoot.id
                // infoModel inherited
            });
            mc3a = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id,
                infoModelId: infoModels[3].id
            });
            mc3b = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id,
                infoModelId: infoModels[3].id
            });

            product1 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            product2 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.DISABLED,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            product3 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            product4 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1, mc2, mc3, mc3a, mc3b].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('empty master-category (without products) fullness should equal 100%', async () => {
            expect(await TestFactory.getTaskQueue()).toMatchObject([]);
            const masterCategoryData: NewMasterCategory = {
                code: 'master_category',
                parentId: mcRoot.id,
                status: MasterCategoryStatus.ACTIVE,
                nameTranslations: {},
                descriptionTranslations: {}
            };
            const createdMasterCategory = await createMasterCategoryHandler.handle({
                context,
                data: {
                    body: masterCategoryData
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdMasterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdMasterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(createdMasterCategory.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('add product to master-category should affect fullness', async () => {
            const createdProduct = await createProductHandler.handle({
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
                            }
                        ]
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [createdProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdProduct.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdProduct.masterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc0.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('update product in master-category should affect fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product3.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [updatedProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('move product from master-category should affect fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc2.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const oldMasterCategoryId = product1.masterCategory.id;
            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product1.identifier
                    },
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
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [updatedProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id, oldMasterCategoryId]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id, oldMasterCategoryId]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc2.id)).toMatchObject({
                fullness: 0,
                averageFullness: 25
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 50,
                averageFullness: 50
            });

            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product4.identifier
                    },
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
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 0,
                averageFullness: 0
            });

            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product3.identifier
                    },
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
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });

            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product2.identifier
                    },
                    body: {
                        status: ProductStatus.DISABLED,
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
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('enable product should affect master-category fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product2.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [updatedProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const masterCategoryFullness = await TestFactory.getMasterCategoryFullness(mc3a.id);
                expect(masterCategoryFullness).toMatchObject({
                    fullness: 75,
                    averageFullness: 75
                });
                expect(masterCategoryFullness.total).toEqual(4);
            }
        });

        it('disable product should affect master-category fullness', async () => {
            const updatedProduct = await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product1.identifier
                    },
                    body: {
                        status: ProductStatus.DISABLED,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [updatedProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedProduct.masterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const masterCategoryFullness = await TestFactory.getMasterCategoryFullness(mc3a.id);
                expect(masterCategoryFullness).toMatchObject({
                    fullness: 50,
                    averageFullness: 50
                });
                expect(masterCategoryFullness.total).toEqual(2);
            }
        });

        it('parent master-category fullness should calculated correctly', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3b.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const createdProduct = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3b.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.TANKER_EXPORT,
                        source: DbTable.PRODUCT,
                        entityIds: [createdProduct.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdProduct.masterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [createdProduct.masterCategory.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3b.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3.id)).toMatchObject({
                fullness: 75,
                averageFullness: 75
            });
        });
    });

    describe('change info-model cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc3: MasterCategory;
        let mc3a: MasterCategory;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.BOOLEAN},
                {type: AttributeType.NUMBER},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false},
                    {id: attributes[5].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[4].id, isImportant: false},
                    {id: attributes[5].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[3].id, isImportant: false},
                    {id: attributes[4].id, isImportant: true},
                    {id: attributes[5].id, isImportant: false}
                ]
            ]);

            const mcRoot = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                infoModelId: infoModels[0].id
            });
            mc3 = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mcRoot.id
                // infoModel inherited
            });
            mc3a = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id,
                infoModelId: infoModels[3].id
            });

            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.DISABLED,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc3, mc3a].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('change to another IM should change fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const updatedMasterCategory = await updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: mc3a.id
                    },
                    body: {
                        infoModelId: infoModels[4].id
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [infoModels[3].id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 33,
                averageFullness: 33
            });
        });

        it('change MC to inherited should change fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const updatedMasterCategory = await updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: mc3a.id
                    },
                    body: {
                        infoModelId: null
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [infoModels[3].id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 33,
                averageFullness: 33
            });
        });

        it('change patent MC to inherited should change fullness', async () => {
            const mc3c = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id
                // infoModel inherited
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3c.id,
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
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3c.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });

            const updatedMasterCategory = await updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: mc3.id
                    },
                    body: {
                        infoModelId: infoModels[2].id
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id, mc3c.id]
                    }
                },
                {
                    info: {
                        queue: QUEUES.INFO_MODEL_FULLNESS,
                        source: SOURCES.MASTER_CATEGORY,
                        masterCategoryIds: [updatedMasterCategory.id, mc3c.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3c.id)).toMatchObject({
                fullness: 0,
                averageFullness: 25
            });
        });
    });

    describe('change via import cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mcRoot: MasterCategory;
        let mc0: MasterCategory;
        let mc1: MasterCategory;
        let mc2: MasterCategory;
        let mc3: MasterCategory;
        let mc3a: MasterCategory;
        let mc3b: MasterCategory;
        let product1: Product;
        let product3: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.BOOLEAN},
                {type: AttributeType.NUMBER},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false},
                    {id: attributes[5].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: true},
                    {id: attributes[2].id, isImportant: false}
                ],
                [
                    {id: attributes[0].id, isImportant: true},
                    {id: attributes[2].id, isImportant: true},
                    {id: attributes[3].id, isImportant: true},
                    {id: attributes[4].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[4].id, isImportant: false},
                    {id: attributes[5].id, isImportant: true}
                ],
                [
                    {id: attributes[0].id, isImportant: false},
                    {id: attributes[1].id, isImportant: false},
                    {id: attributes[3].id, isImportant: false},
                    {id: attributes[4].id, isImportant: true},
                    {id: attributes[5].id, isImportant: false}
                ]
            ]);

            mcRoot = await TestFactory.createMasterCategory({
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
                parentId: mcRoot.id
                // infoModel inherited
            });
            mc3a = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id,
                infoModelId: infoModels[3].id
            });
            mc3b = await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: mc3.id,
                infoModelId: infoModels[3].id
            });

            product1 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[0].id,
                                value: '00'
                            },
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.DISABLED,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });
            product3 = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[4].id,
                                value: 44
                            }
                        ]
                    }
                }
            });
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc3a.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[5].id,
                                value: 55
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0, mc1, mc2, mc3, mc3a, mc3b].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('add product to master-category should affect fullness', async () => {
            const content = [
                [MASTER_CATEGORY_HEADER, attributes[0].code],
                ['' + mc0.code, '00']
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
            expect(newProductIdentifiers).toHaveLength(1);
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
            expect(await TestFactory.getMasterCategoryFullness(mc0.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('update product in master-category should affect fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const content = [
                [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, attributes[5].code],
                ['' + product3.identifier, mc3a.code, '55']
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product3.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
        });

        it('move product from master-category should affect fullness', async () => {
            expect(await TestFactory.getMasterCategoryFullness(mc2.id)).toMatchObject({
                fullness: 100,
                averageFullness: 100
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 66,
                averageFullness: 66
            });

            const oldMasterCategoryCode = product1.masterCategory.code;
            const content = [
                [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
                ['' + product1.identifier, mc2.code]
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
                        productIdentifiers: [product1.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            expect(await TestFactory.getMasterCategoryFullness(mc2.id)).toMatchObject({
                fullness: 0,
                averageFullness: 25
            });
            expect(await TestFactory.getMasterCategoryFullness(mc3a.id)).toMatchObject({
                fullness: 50,
                averageFullness: 50
            });
        });
    });
});
