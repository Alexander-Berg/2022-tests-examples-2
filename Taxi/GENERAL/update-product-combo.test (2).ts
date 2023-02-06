import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import {ProductCombo} from '@/src/entities/product-combo/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {NonMetaProductForbidden} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {ProductComboStatus, ProductComboType} from 'types/product-combo';

import {updateProductComboHandler} from './update-product-combo';

describe('update product combo', () => {
    let user: User;
    let langs: [Lang, Lang];
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProduct: Product;
    let realProducts: [Product, Product, Product, Product];
    let productCombo: ProductCombo;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {comboProduct: {canEdit: true}}});
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});

        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});

        attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC, isValueLocalizable: true}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.BARCODE, isArray: true}
            })
        ]);

        infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: region.id, attributes});

        masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        metaProduct = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[0].id,
                value: `product_name_${metaProduct.id}_${langs[0].id}`,
                langId: langs[0].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[0].id,
                value: `product_name_${metaProduct.id}_${langs[1].id}`,
                langId: langs[1].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[1].id,
                value: [`product_barcode_${metaProduct.id}`]
            })
        ]);

        const realProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        };

        realProducts = await Promise.all([
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams)
        ]);

        await Promise.all(
            realProducts.map((it) =>
                Promise.all([
                    TestFactory.createProductAttributeValue({
                        userId: user.id,
                        productId: it.id,
                        attributeId: attributes[0].id,
                        value: `product_name_${it.id}_${langs[0].id}`,
                        langId: langs[0].id
                    }),
                    TestFactory.createProductAttributeValue({
                        userId: user.id,
                        productId: it.id,
                        attributeId: attributes[0].id,
                        value: `product_name_${it.id}_${langs[1].id}`,
                        langId: langs[1].id
                    }),
                    TestFactory.createProductAttributeValue({
                        userId: user.id,
                        productId: it.id,
                        attributeId: attributes[1].id,
                        value: [`product_barcode_${it.id}`]
                    })
                ])
            )
        );

        productCombo = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            productCombo: {
                status: ProductComboStatus.ACTIVE,
                type: ProductComboType.DISCOUNT,
                nameTranslationMap: {[langs[0].isoCode]: 'product_combo_name_1'},
                descriptionTranslationMap: {[langs[1].isoCode]: 'product_combo_description_1'}
            }
        });

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [metaProduct.id]
        });

        const productComboGroup = await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {
                productComboId: productCombo.id,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'group_name_1',
                    [langs[1].isoCode]: 'group_name_1'
                },
                optionsToSelect: 1,
                isSelectUnique: true
            }
        });

        await Promise.all([
            TestFactory.createProductComboOption({
                userId: user.id,
                productComboOption: {
                    productComboGroupId: productComboGroup.id,
                    productId: realProducts[0].id,
                    sortOrder: 0
                }
            }),
            TestFactory.createProductComboOption({
                userId: user.id,
                productComboOption: {
                    productComboGroupId: productComboGroup.id,
                    productId: realProducts[1].id,
                    sortOrder: 1
                }
            }),
            TestFactory.createProductComboOption({
                userId: user.id,
                productComboOption: {
                    productComboGroupId: productComboGroup.id,
                    productId: realProducts[2].id,
                    sortOrder: 2
                }
            })
        ]);

        const manager = await TestFactory.getManager();
        productCombo = await manager.findOneOrFail(ProductCombo, productCombo.id, {
            relations: ['products', 'groups', 'groups.options', 'historySubject']
        });
    });

    it('should update product combo', async () => {
        const updatedProductCombo = await updateProductComboHandler.handle({
            context,
            data: {
                params: {id: productCombo.id},
                body: {
                    productIds: [],
                    nameTranslations: {[langs[1].isoCode]: 'update_name'},
                    descriptionTranslations: {[langs[0].isoCode]: 'update_description'},
                    status: ProductComboStatus.DISABLED,
                    type: ProductComboType.RECIPE,
                    groups: [
                        {
                            id: productCombo.groups[0].id,
                            nameTranslations: {
                                [langs[0].isoCode]: 'updated_group_name_1',
                                [langs[1].isoCode]: 'updated_group_name_2'
                            },
                            optionsToSelect: 2,
                            isSelectUnique: true,
                            options: [
                                {productId: realProducts[1].id, id: productCombo.groups[0].options[1].id},
                                {productId: realProducts[2].id, id: productCombo.groups[0].options[2].id}
                            ]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'group_name_1',
                                [langs[1].isoCode]: 'group_name_2'
                            },
                            optionsToSelect: 5,
                            isSelectUnique: false,
                            options: [
                                {productId: realProducts[0].id, id: null},
                                {productId: realProducts[3].id, id: null}
                            ]
                        }
                    ]
                }
            }
        });

        expect(updatedProductCombo).toEqual({
            id: productCombo.id,
            status: ProductComboStatus.DISABLED,
            type: ProductComboType.RECIPE,
            nameTranslations: {[langs[1].isoCode]: 'update_name'},
            descriptionTranslations: {[langs[0].isoCode]: 'update_description'},
            uuid: productCombo.prefixedUuid,
            products: [],
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date),
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            groups: [
                {
                    id: productCombo.groups[0].id,
                    nameTranslations: {
                        [langs[0].isoCode]: 'updated_group_name_1',
                        [langs[1].isoCode]: 'updated_group_name_2'
                    },
                    optionsToSelect: 2,
                    isSelectUnique: true,
                    options: [realProducts[1], realProducts[2]].map((it) => ({
                        id: expect.any(Number),
                        product: {
                            id: it.id,
                            identifier: it.identifier,
                            name: {
                                [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                                [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                            },
                            images: []
                        }
                    }))
                },
                {
                    id: expect.any(Number),
                    nameTranslations: {
                        [langs[0].isoCode]: 'group_name_1',
                        [langs[1].isoCode]: 'group_name_2'
                    },
                    optionsToSelect: 5,
                    isSelectUnique: false,
                    options: [realProducts[0], realProducts[3]].map((it) => ({
                        id: expect.any(Number),
                        product: {
                            id: it.id,
                            identifier: it.identifier,
                            name: {
                                [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                                [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                            },
                            images: []
                        }
                    }))
                }
            ]
        });
    });

    it('update meta product', async () => {
        const anotherMetaProduct = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: anotherMetaProduct.id,
                attributeId: attributes[0].id,
                value: 'another_meta_product_name_1',
                langId: langs[0].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: anotherMetaProduct.id,
                attributeId: attributes[0].id,
                value: 'another_meta_product_name_2',
                langId: langs[1].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: anotherMetaProduct.id,
                attributeId: attributes[1].id,
                value: ['another_meta_product_barcode']
            })
        ]);

        const updatedProductCombo = await updateProductComboHandler.handle({
            context,
            data: {
                params: {id: productCombo.id},
                body: {
                    productIds: [anotherMetaProduct.id],
                    nameTranslations: productCombo.nameTranslationMap,
                    descriptionTranslations: productCombo.descriptionTranslationMap,
                    status: productCombo.status,
                    type: productCombo.type,
                    groups: [
                        {
                            id: productCombo.groups[0].id,
                            nameTranslations: {
                                [langs[0].isoCode]: 'group_name_1',
                                [langs[1].isoCode]: 'group_name_1'
                            },
                            optionsToSelect: productCombo.groups[0].optionsToSelect,
                            isSelectUnique: productCombo.groups[0].isSelectUnique,
                            options: [
                                {productId: realProducts[0].id, id: productCombo.groups[0].options[0].id},
                                {productId: realProducts[1].id, id: productCombo.groups[0].options[1].id},
                                {productId: realProducts[2].id, id: productCombo.groups[0].options[2].id}
                            ]
                        }
                    ]
                }
            }
        });

        expect(updatedProductCombo.products).toHaveLength(1);
        expect(updatedProductCombo).toMatchObject({
            products: [
                {
                    id: anotherMetaProduct.id,
                    identifier: anotherMetaProduct.identifier,
                    name: {
                        [langs[0].isoCode]: 'another_meta_product_name_1',
                        [langs[1].isoCode]: 'another_meta_product_name_2'
                    },
                    images: []
                }
            ]
        });
    });

    it('should throw if product combo linked to real product', async () => {
        const productComboPromise = updateProductComboHandler.handle({
            context,
            data: {
                params: {id: productCombo.id},
                body: {
                    productIds: [realProducts[3].id],
                    nameTranslations: productCombo.nameTranslationMap,
                    descriptionTranslations: productCombo.descriptionTranslationMap,
                    status: productCombo.status,
                    type: productCombo.type,
                    groups: [
                        {
                            id: productCombo.groups[0].id,
                            nameTranslations: productCombo.groups[0].nameTranslationMap,
                            optionsToSelect: productCombo.groups[0].optionsToSelect,
                            isSelectUnique: productCombo.groups[0].isSelectUnique,
                            options: [
                                {productId: realProducts[0].id, id: productCombo.groups[0].options[0].id},
                                {productId: realProducts[1].id, id: productCombo.groups[0].options[1].id},
                                {productId: realProducts[2].id, id: productCombo.groups[0].options[2].id}
                            ]
                        }
                    ]
                }
            }
        });

        await expect(productComboPromise).rejects.toThrow(NonMetaProductForbidden);
    });

    it('should create tanker export task for groups with changed translations', async () => {
        const baseData = {
            productIds: productCombo.products.map(({id}) => id),
            nameTranslations: productCombo.nameTranslationMap,
            descriptionTranslations: productCombo.descriptionTranslationMap,
            status: productCombo.status,
            type: productCombo.type,
            groups: productCombo.groups.map((group) => ({
                id: group.id,
                nameTranslations: group.nameTranslationMap,
                optionsToSelect: group.optionsToSelect,
                isSelectUnique: group.isSelectUnique,
                options: group.options.map((option) => ({
                    id: option.id,
                    productId: option.productId
                }))
            }))
        };

        const _updatedProductCombo1 = await updateProductComboHandler.handle({
            context,
            data: {
                params: {id: productCombo.id},
                body: {
                    ...baseData,
                    groups: baseData.groups.map((group) => ({
                        ...group,
                        isSelectUnique: !group.isSelectUnique,
                        optionsToSelect: group.optionsToSelect + 1
                    }))
                }
            }
        });

        const taskQueue1 = await TestFactory.getTaskQueue();
        expect(taskQueue1).toHaveLength(0);

        const updatedProductCombo2 = await updateProductComboHandler.handle({
            context,
            data: {
                params: {id: productCombo.id},
                body: {
                    ...baseData,
                    groups: [
                        ...baseData.groups.map((group) => ({
                            ...group,
                            nameTranslations: {
                                [langs[0].isoCode]: 'foo1',
                                [langs[1].isoCode]: 'foo2'
                            }
                        })),
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'bar1',
                                [langs[1].isoCode]: 'bar2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [
                                {productId: realProducts[0].id, id: null},
                                {productId: realProducts[1].id, id: null}
                            ]
                        }
                    ]
                }
            }
        });

        const taskQueue2 = await TestFactory.getTaskQueue();
        expect(taskQueue2).toHaveLength(1);

        expect(taskQueue2[0]).toMatchObject({
            info: {
                source: DbTable.PRODUCT_COMBO_GROUP,
                entityIds: updatedProductCombo2.groups.map(({id}) => Number(id))
            }
        });
    });
});
