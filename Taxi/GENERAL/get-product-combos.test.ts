import {addDays, subDays} from 'date-fns';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import {ProductCombo} from '@/src/entities/product-combo/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {ProductComboStatus, ProductComboType} from 'types/product-combo';

import {getProductCombosHandler} from './get-product-combos';

describe('get product combos', () => {
    let user: User;
    let langs: [Lang, Lang];
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProducts: [Product, Product, Product];
    let realProducts: [Product, Product, Product];
    let productCombos: [ProductCombo, ProductCombo];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});

        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});

        attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME, isValueLocalizable: true}
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

        const metaProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        };

        metaProducts = await Promise.all([
            TestFactory.createProduct(metaProductParams),
            TestFactory.createProduct(metaProductParams),
            TestFactory.createProduct(metaProductParams)
        ]);

        await Promise.all(
            metaProducts.map((it) =>
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

        const realProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        };

        realProducts = await Promise.all([
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

        productCombos = await Promise.all([
            TestFactory.createProductCombo({
                userId: user.id,
                regionId: region.id,
                productCombo: {
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT,
                    nameTranslationMap: {[langs[0].isoCode]: 'product_combo_name_1'}
                }
            }),
            TestFactory.createProductCombo({
                userId: user.id,
                regionId: region.id,
                productCombo: {status: ProductComboStatus.DISABLED, type: ProductComboType.RECIPE}
            })
        ]);

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo: productCombos[0],
            productComboProductIds: [metaProducts[0].id]
        });

        await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {productComboId: productCombos[0].id, optionsToSelect: 1, isSelectUnique: true}
        }).then(({id: productComboGroupId}) =>
            Promise.all([
                TestFactory.createProductComboOption({
                    userId: user.id,
                    productComboOption: {productComboGroupId, productId: realProducts[0].id}
                }),
                TestFactory.createProductComboOption({
                    userId: user.id,
                    productComboOption: {productComboGroupId, productId: realProducts[1].id}
                })
            ])
        );

        await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {productComboId: productCombos[1].id, optionsToSelect: 1, isSelectUnique: true}
        }).then(({id: productComboGroupId}) =>
            Promise.all([
                TestFactory.createProductComboOption({
                    userId: user.id,
                    productComboOption: {productComboGroupId, productId: realProducts[1].id}
                }),
                TestFactory.createProductComboOption({
                    userId: user.id,
                    productComboOption: {productComboGroupId, productId: realProducts[2].id}
                })
            ])
        );

        const manager = await TestFactory.getManager();
        productCombos = (await manager.find(ProductCombo, {
            relations: ['products', 'historySubject', 'historySubject.author'],
            order: {id: 'ASC'}
        })) as never;
    });

    it('should find product combos', async () => {
        const combos = await getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0
                }
            }
        });

        expect(combos).toEqual({
            list: productCombos
                .slice()
                .sort((a, b) => a.id - b.id)
                .map((it) => ({
                    id: it.id,
                    uuid: it.prefixedUuid,
                    status: it.status,
                    type: it.type,
                    nameTranslations: it.nameTranslationMap,
                    updatedAt: it.historySubject.updatedAt,
                    products: it.products.map((it) => ({
                        id: it.id,
                        identifier: it.identifier,
                        name: {
                            [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                            [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                        },
                        images: []
                    })),
                    author: it.historySubject.author.formatAuthor()
                })),
            totalCount: 2
        });
    });

    it('should find product combos by status', async () => {
        const combos = await getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        status: [ProductComboStatus.ACTIVE]
                    }
                }
            }
        });
        expect(combos).toMatchObject({list: [{id: productCombos[0].id}], totalCount: 1});
    });

    it('should find product combos by type', async () => {
        const combos = await getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        type: [ProductComboType.RECIPE]
                    }
                }
            }
        });
        expect(combos).toMatchObject({list: [{id: productCombos[1].id}], totalCount: 1});
    });

    it('should find product combos by uuid', async () => {
        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        uuid: {action: 'equal', values: [productCombos[0].uuid.substring(0, 10)]}
                    }
                }
            }
        });

        await expect(combos1).resolves.toEqual({list: [], totalCount: 0});

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        uuid: {action: 'equal', values: [productCombos[0].uuid]}
                    }
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({list: [{id: productCombos[0].id}], totalCount: 1});

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        uuid: {action: 'not-equal', values: [productCombos[0].uuid]}
                    }
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({list: [{id: productCombos[1].id}], totalCount: 1});
    });

    it('should find product combos by created at', async () => {
        const manager = await TestFactory.getManager();
        const historySubject1 = productCombos[0].historySubject;
        historySubject1.createdAt = subDays(historySubject1.createdAt, 2);
        await manager.save(historySubject1);

        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        createdAt: [null, null]
                    }
                }
            }
        });

        await expect(combos1).resolves.toMatchObject({
            list: [{id: productCombos[0].id}, {id: productCombos[1].id}],
            totalCount: 2
        });

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        createdAt: [null, subDays(productCombos[1].historySubject.createdAt, 1).getTime()]
                    }
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        createdAt: [addDays(productCombos[0].historySubject.createdAt, 1).getTime(), null]
                    }
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });
    });

    it('should find product combos by updated at', async () => {
        const manager = await TestFactory.getManager();
        const historySubject1 = productCombos[0].historySubject;
        historySubject1.updatedAt = subDays(historySubject1.updatedAt, 2);
        await manager.save(historySubject1);

        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        updatedAt: [null, null]
                    }
                }
            }
        });

        await expect(combos1).resolves.toMatchObject({
            list: [{id: productCombos[0].id}, {id: productCombos[1].id}],
            totalCount: 2
        });

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        updatedAt: [null, subDays(productCombos[1].historySubject.updatedAt, 1).getTime()]
                    }
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        updatedAt: [addDays(productCombos[0].historySubject.updatedAt, 1).getTime(), null]
                    }
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });
    });

    it('should find product combos by linked meta product', async () => {
        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        metaProducts: {action: 'null', values: []}
                    }
                }
            }
        });

        await expect(combos1).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        metaProducts: {action: 'not-null', values: []}
                    }
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        metaProducts: {action: 'equal', values: [productCombos[0].products[0].id]}
                    }
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo: productCombos[1],
            productComboProductIds: [metaProducts[1].id]
        });

        const combos4 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        metaProducts: {action: 'not-equal', values: [productCombos[0].products[0].id]}
                    }
                }
            }
        });

        await expect(combos4).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });
    });

    it('should find product combos by product options', async () => {
        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        optionProducts: {action: 'equal', values: [realProducts[0].id, realProducts[1].id]}
                    }
                }
            }
        });

        await expect(combos1).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        optionProducts: {action: 'equal', values: [realProducts[1].id]}
                    }
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({
            list: [{id: productCombos[0].id}, {id: productCombos[1].id}],
            totalCount: 2
        });

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        optionProducts: {action: 'not-equal', values: [realProducts[1].id]}
                    }
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({
            list: [],
            totalCount: 0
        });

        const combos4 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    filters: {
                        optionProducts: {action: 'not-equal', values: [realProducts[2].id]}
                    }
                }
            }
        });

        await expect(combos4).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });
    });

    it('should find product combos by search string', async () => {
        const combos1 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    search: productCombos[0].nameTranslationMap[langs[0].isoCode].substring(5)
                }
            }
        });

        await expect(combos1).resolves.toMatchObject({
            list: [{id: productCombos[0].id}],
            totalCount: 1
        });

        const combos2 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    search: productCombos[1].uuid.substring(2)
                }
            }
        });

        await expect(combos2).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });

        const combos3 = getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    search: productCombos[1].uuid.substring(0, 8)
                }
            }
        });

        await expect(combos3).resolves.toMatchObject({
            list: [{id: productCombos[1].id}],
            totalCount: 1
        });
    });

    it('should respect limit and offset', async () => {
        await TestFactory.createProductCombo({userId: user.id, regionId: region.id});

        const combos = await getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 1,
                    offset: 1
                }
            }
        });

        expect(combos).toMatchObject({list: [{id: productCombos[1].id}], totalCount: 3});
    });

    it('should ignore combos from another region', async () => {
        const anotherRegion = await TestFactory.createRegion();
        await TestFactory.createProductCombo({userId: user.id, regionId: anotherRegion.id});

        const combos = await getProductCombosHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0
                }
            }
        });

        expect(combos).toMatchObject({totalCount: 2});
    });
});
