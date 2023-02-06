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
import {updateAttributeHandler} from 'server/routes/api/v1/attributes/update-attribute';
import {updateInfoModelHandler} from 'server/routes/api/v1/info-models/update-info-model';
import {createProductHandler} from 'server/routes/api/v1/products/create-product';
import {updateProductHandler} from 'server/routes/api/v1/products/update-product';
import {CommitHandler} from 'service/import/commit-handler';
import {ImportMode} from 'types/import';
import {Product, ProductStatus} from 'types/product';

import {processTaskQueue, pushTask, QUEUES, SOURCES} from '..';

describe('product confirmation', () => {
    let region: Region;
    let user: User;
    let context: ApiRequestContext;
    let langs: Lang[];

    beforeEach(async () => {
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        user = await TestFactory.createUser({
            rules: {
                product: {canEdit: true},
                masterCategory: {canEdit: true},
                infoModel: {canEdit: true},
                canConfirm: true,
                attribute: {canEdit: true}
            }
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
                {type: AttributeType.BOOLEAN, isConfirmable: true},
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.TEXT, isArray: true, isConfirmable: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.STRING, isValueLocalizable: true, isConfirmable: true}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id}],
                [{id: attributes[1].id}, {id: attributes[2].id}, {id: attributes[4].id}],
                [
                    // no attributes
                ],
                [{id: attributes[5].id}, {id: attributes[1].id}]
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
        });

        it('product confirmation with info-model with 0 attributes should be equal 100%', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc2.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
            expect(product.confirmation).toEqual(100);
        });

        it('product confirmation with info-model with 0 confirmable attributes should be equal 100%', async () => {
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
                                value: 'test',
                                isConfirmed: false
                            }
                        ]
                    }
                }
            });
            expect(product.confirmation).toEqual(100);
        });

        it('confirm more attributes should change confirmation', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc1.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[1].id,
                                value: false,
                                isConfirmed: true
                            }
                        ]
                    }
                }
            });
            expect(product.confirmation).toEqual(50);

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
                                attributeId: attributes[1].id,
                                value: false,
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 666,
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44,
                                isConfirmed: false
                            }
                        ]
                    }
                }
            });
            expect(updatedProduct.confirmation).toEqual(100);
        });

        it('confirmation when all confirmable attributes are non confirmed should equals 0', async () => {
            const product = await createProductHandler.handle({
                context,
                data: {
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc1.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attributes[1].id,
                                value: false,
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 666,
                                isConfirmed: false
                            }
                        ]
                    }
                }
            });
            expect(product.confirmation).toEqual(0);
        });

        it('localizable attribute is confirmed only when all locales are confirmed', async () => {
            const product = await TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                status: ProductStatus.ACTIVE,
                masterCategoryId: mc3.id
            });

            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: product.id,
                    attributeId: attributes[5].id,
                    langId: langs[0].id,
                    value: 'push',
                    isConfirmed: true
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: product.id,
                    attributeId: attributes[1].id,
                    value: false,
                    isConfirmed: true
                })
            ]);

            await pushTask({
                queue: QUEUES.PRODUCT_CONFIRMATION,
                source: SOURCES.PRODUCT,
                productIds: [product.id]
            });

            await processTaskQueue();

            const productConfirmationWithOneLocale = await TestFactory.getProductConfirmation(product.id);

            expect(productConfirmationWithOneLocale.confirmation).toEqual(50);

            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attributes[5].id,
                langId: langs[1].id,
                value: 'pop',
                isConfirmed: true
            });

            await pushTask({
                queue: QUEUES.PRODUCT_CONFIRMATION,
                source: SOURCES.PRODUCT,
                productIds: [product.id]
            });

            await processTaskQueue();

            const productConfirmationWithAllLocales = await TestFactory.getProductConfirmation(product.id);

            expect(productConfirmationWithAllLocales.confirmation).toEqual(100);
        });
    });

    describe('change info-model cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let product: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING},
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.TEXT, isArray: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER, isConfirmable: true}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id}, {id: attributes[1].id}],
                [{id: attributes[0].id}, {id: attributes[1].id}, {id: attributes[2].id}]
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
                                value: '00',
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11,
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[2].id,
                                value: ['22a'],
                                isConfirmed: false
                            }
                        ]
                    }
                }
            });
        });

        it('add one not confirmable attribute should not change confirmation', async () => {
            expect(product.confirmation).toEqual(100);

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
                                {id: attributes[0].id},
                                {id: attributes[1].id},
                                {id: attributes[2].id},
                                {id: attributes[3].id}
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
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(100);
        });

        it('add one confirmable attribute should change confirmation', async () => {
            expect(product.confirmation).toEqual(100);

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
                                {id: attributes[0].id},
                                {id: attributes[1].id},
                                {id: attributes[2].id},
                                {id: attributes[3].id},
                                {id: attributes[4].id}
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
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
        });

        it('remove confirmable from info-model change confirmation', async () => {
            expect(product.confirmation).toEqual(100);

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
                                {id: attributes[0].id},
                                {id: attributes[1].id},
                                {id: attributes[2].id},
                                {id: attributes[4].id}
                            ]
                        }
                    }
                }
            });
            await processTaskQueue();
            const p = await getProductByIdentifier(product.identifier);
            expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);

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
                            custom: [{id: attributes[0].id}, {id: attributes[1].id}, {id: attributes[2].id}]
                        }
                    }
                }
            });
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.INFO_MODEL,
                        infoModelIds: [product.infoModel.id]
                    }
                }
            ]);
            await processTaskQueue();
            expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(100);
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
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER, isConfirmable: true}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id}, {id: attributes[1].id}, {id: attributes[2].id}],
                [
                    {id: attributes[0].id},
                    {id: attributes[1].id},
                    {id: attributes[2].id},
                    {id: attributes[3].id},
                    {id: attributes[4].id}
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
                                value: '00',
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11,
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22,
                                isConfirmed: false
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
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
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
                                value: '00',
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11,
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22,
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[4].id,
                                value: 44,
                                isConfirmed: false
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
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(33);
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
                {type: AttributeType.STRING, isConfirmable: true},
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER},
                {type: AttributeType.NUMBER, isConfirmable: true}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id}, {id: attributes[1].id}, {id: attributes[2].id}],
                [
                    {id: attributes[0].id},
                    {id: attributes[1].id},
                    {id: attributes[2].id},
                    {id: attributes[3].id},
                    {id: attributes[4].id}
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
                                value: '00',
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11,
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22,
                                isConfirmed: false
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

        it('update confirmation of product attributes should change confirmation', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
            }

            const content = [
                [IDENTIFIER_HEADER, attributes[1].code],
                ['' + product.identifier, '33']
            ];
            const {importKey} = await TestFactory.createImportSpreadsheet({
                regionId: region.id,
                content,
                mode: ImportMode.CONFIRM
            });
            const commitHandler = new CommitHandler({importKey, authorId: user.id});
            expect(await commitHandler.handle()).toBeUndefined();
            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_FULLNESS,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product.identifier]
                    }
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(100);
            }
        });

        it('update product MC should change confirmation', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
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
                },
                {
                    info: {
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.IMPORT,
                        productIdentifiers: [product.identifier]
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(33);
            }
        });
    });

    describe('attribute cases', () => {
        let attributes: Attribute[];
        let infoModels: InfoModel[];
        let mc0: MasterCategory;
        let product: Product;

        beforeEach(async () => {
            attributes = await attributesFactory(user, [
                {type: AttributeType.STRING, isConfirmable: true},
                {type: AttributeType.NUMBER, isConfirmable: true},
                {type: AttributeType.NUMBER}
            ]);
            infoModels = await infoModelsFactory(user, region, [
                [{id: attributes[0].id}, {id: attributes[1].id}, {id: attributes[2].id}]
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
                                value: '00',
                                isConfirmed: true
                            },
                            {
                                attributeId: attributes[1].id,
                                value: 11,
                                isConfirmed: false
                            },
                            {
                                attributeId: attributes[2].id,
                                value: 22,
                                isConfirmed: false
                            }
                        ]
                    }
                }
            });

            await pushTask({
                queue: QUEUES.MASTER_CATEGORY_FULLNESS,
                source: SOURCES.MASTER_CATEGORY,
                masterCategoryIds: [mc0].map(({id}) => id)
            });
            await processTaskQueue();
        });

        it('Should recalc confirmation if attr from master category has been switched to unconfirmable', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
            }

            await updateAttributeHandler.handle({
                context,
                data: {
                    params: {id: attributes[1].id},
                    body: {
                        isConfirmable: false
                    }
                }
            });

            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.ATTRIBUTE,
                        attributeId: attributes[1].id
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(100);
            }
        });

        it('Should recalc confirmation if attr from master category has been switched to confirmable', async () => {
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(50);
            }

            await updateAttributeHandler.handle({
                context,
                data: {
                    params: {id: attributes[2].id},
                    body: {
                        isConfirmable: true
                    }
                }
            });

            expect(await TestFactory.getTaskQueue()).toMatchObject([
                {
                    info: {
                        queue: QUEUES.PRODUCT_CONFIRMATION,
                        source: SOURCES.ATTRIBUTE,
                        attributeId: attributes[2].id
                    }
                }
            ]);
            await processTaskQueue();
            {
                const p = await getProductByIdentifier(product.identifier);
                expect((await TestFactory.getProductConfirmation(p!.id)).confirmation).toEqual(33);
            }
        });
    });
});
