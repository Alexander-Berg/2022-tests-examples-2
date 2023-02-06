import {groupBy} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {NonMetaProductForbidden} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {ProductComboStatus, ProductComboType} from 'types/product-combo';

import {createProductComboHandler} from './create-product-combo';

describe('create product combos', () => {
    let user: User;
    let langs: [Lang, Lang];
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProduct: Product;
    let metaProductAttributeValues: ProductAttributeValue[];
    let realProducts: [Product, Product, Product];
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
                attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME, isValueLocalizable: true}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.IMAGE, code: ATTRIBUTES_CODES.IMAGE, isArray: true}
            }),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}})
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

        metaProductAttributeValues = await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[0].id,
                value: 'Product name 1',
                langId: langs[0].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[0].id,
                value: 'Product name 2',
                langId: langs[1].id
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[1].id,
                value: ['https://product-image/1/%s', 'https://product-image/2/%s']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: metaProduct.id,
                attributeId: attributes[2].id,
                value: 666
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
            TestFactory.createProduct(realProductParams)
        ]);
    });

    it('should create product combo without linked meta product', async () => {
        const productCombo = await createProductComboHandler.handle({
            context,
            data: {
                body: {
                    productIds: [],
                    nameTranslations: {},
                    descriptionTranslations: {},
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT,
                    groups: [
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_1',
                                [langs[1].isoCode]: 'name_1'
                            },
                            optionsToSelect: 3,
                            isSelectUnique: false,
                            options: [
                                {productId: realProducts[0].id, id: null},
                                {productId: realProducts[1].id, id: null},
                                {productId: realProducts[2].id, id: null}
                            ]
                        }
                    ]
                }
            }
        });

        expect(productCombo).toEqual({
            id: expect.any(Number),
            status: ProductComboStatus.ACTIVE,
            type: ProductComboType.DISCOUNT,
            nameTranslations: {},
            descriptionTranslations: {},
            uuid: expect.stringMatching(
                new RegExp(/^pigeon_combo_[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i)
            ),
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
                    id: expect.any(Number),
                    optionsToSelect: 3,
                    isSelectUnique: false,
                    nameTranslations: {
                        [langs[0].isoCode]: 'name_1',
                        [langs[1].isoCode]: 'name_1'
                    },
                    options: realProducts.map((it) => ({
                        id: expect.any(Number),
                        product: {
                            id: it.id,
                            identifier: it.identifier,
                            name: {},
                            images: []
                        }
                    }))
                }
            ]
        });
    });

    it('should create product combo with linked meta product', async () => {
        const productCombo = await createProductComboHandler.handle({
            context,
            data: {
                body: {
                    productIds: [metaProduct.id],
                    nameTranslations: {
                        [langs[0].isoCode]: 'product combo name 1',
                        [langs[1].isoCode]: ''
                    },
                    descriptionTranslations: {
                        [langs[0].isoCode]: '',
                        [langs[1].isoCode]: 'product combo description 1'
                    },
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.RECIPE,
                    groups: [
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_1_1',
                                [langs[1].isoCode]: 'name_1_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[0].id, id: null}]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_2_1',
                                [langs[1].isoCode]: 'name_2_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[1].id, id: null}]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_3_1',
                                [langs[1].isoCode]: 'name_3_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[2].id, id: null}]
                        }
                    ]
                }
            }
        });

        expect(productCombo).toEqual({
            id: expect.any(Number),
            status: ProductComboStatus.ACTIVE,
            type: ProductComboType.RECIPE,
            nameTranslations: {
                [langs[0].isoCode]: 'product combo name 1'
            },
            descriptionTranslations: {
                [langs[1].isoCode]: 'product combo description 1'
            },
            uuid: expect.stringMatching(
                new RegExp(/^pigeon_combo_[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i)
            ),
            products: [
                {
                    id: metaProduct.id,
                    identifier: metaProduct.identifier,
                    name: {
                        [langs[0].isoCode]: metaProductAttributeValues[0].value,
                        [langs[1].isoCode]: metaProductAttributeValues[1].value
                    },
                    images: metaProductAttributeValues[2].value
                }
            ],
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
                    id: expect.any(Number),
                    nameTranslations: {
                        [langs[0].isoCode]: 'name_1_1',
                        [langs[1].isoCode]: 'name_1_2'
                    },
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [
                        {
                            id: expect.any(Number),
                            product: {
                                id: realProducts[0].id,
                                identifier: realProducts[0].identifier,
                                name: {},
                                images: []
                            }
                        }
                    ]
                },
                {
                    id: expect.any(Number),
                    nameTranslations: {
                        [langs[0].isoCode]: 'name_2_1',
                        [langs[1].isoCode]: 'name_2_2'
                    },
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [
                        {
                            id: expect.any(Number),
                            product: {
                                id: realProducts[1].id,
                                identifier: realProducts[1].identifier,
                                name: {},
                                images: []
                            }
                        }
                    ]
                },
                {
                    id: expect.any(Number),
                    nameTranslations: {
                        [langs[0].isoCode]: 'name_3_1',
                        [langs[1].isoCode]: 'name_3_2'
                    },
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [
                        {
                            id: expect.any(Number),
                            product: {
                                id: realProducts[2].id,
                                identifier: realProducts[2].identifier,
                                name: {},
                                images: []
                            }
                        }
                    ]
                }
            ]
        });
    });

    it('should form correct history records', async () => {
        await TestFactory.flushHistory();

        await createProductComboHandler.handle({
            context,
            data: {
                body: {
                    productIds: [metaProduct.id],
                    nameTranslations: {},
                    descriptionTranslations: {},
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT,
                    groups: [
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_1_1',
                                [langs[1].isoCode]: 'name_1_2'
                            },
                            optionsToSelect: 3,
                            isSelectUnique: false,
                            options: [
                                {productId: realProducts[0].id, id: null},
                                {productId: realProducts[1].id, id: null},
                                {productId: realProducts[2].id, id: null}
                            ]
                        }
                    ]
                }
            }
        });

        const history = await TestFactory.dispatchHistory();
        history.sort((a, b) => a.id - b.id);

        expect(history).toHaveLength(6);
        const groupedHistory = groupBy(history, ({tableName}) => tableName);

        expect(groupedHistory['product_combo']).toHaveLength(1);
        expect(groupedHistory['product_combo_product']).toHaveLength(1);
        expect(groupedHistory['product_combo_group']).toHaveLength(1);
        expect(groupedHistory['product_combo_option']).toHaveLength(3);
    });

    it('should throw if product combo linked to real product', async () => {
        const productComboPromise = createProductComboHandler.handle({
            context,
            data: {
                body: {
                    productIds: [realProducts[0].id],
                    nameTranslations: {},
                    descriptionTranslations: {},
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT,
                    groups: [
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_1_1',
                                [langs[1].isoCode]: 'name_1_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[1].id, id: null}]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_2_1',
                                [langs[1].isoCode]: 'name_2_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[2].id, id: null}]
                        }
                    ]
                }
            }
        });

        await expect(productComboPromise).rejects.toThrow(NonMetaProductForbidden);
    });

    it('should create tanker export tasks', async () => {
        const productCombo = await createProductComboHandler.handle({
            context,
            data: {
                body: {
                    productIds: [],
                    nameTranslations: {},
                    descriptionTranslations: {},
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT,
                    groups: [
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_1',
                                [langs[1].isoCode]: 'name_1'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[0].id, id: null}]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_2',
                                [langs[1].isoCode]: 'name_2'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[1].id, id: null}]
                        },
                        {
                            id: null,
                            nameTranslations: {
                                [langs[0].isoCode]: 'name_3',
                                [langs[1].isoCode]: 'name_3'
                            },
                            optionsToSelect: 1,
                            isSelectUnique: true,
                            options: [{productId: realProducts[2].id, id: null}]
                        }
                    ]
                }
            }
        });

        const taskQueue = await TestFactory.getTaskQueue();
        expect(taskQueue).toHaveLength(2);
        taskQueue.sort((a, b) => a.info.source.localeCompare(b.info.source));
        expect(taskQueue[0]).toMatchObject({
            info: {
                source: DbTable.PRODUCT_COMBO,
                entityIds: [Number(productCombo.id)]
            }
        });
        expect(taskQueue[1]).toMatchObject({
            info: {
                source: DbTable.PRODUCT_COMBO_GROUP,
                entityIds: productCombo.groups.map(({id}) => Number(id))
            }
        });
    });
});
