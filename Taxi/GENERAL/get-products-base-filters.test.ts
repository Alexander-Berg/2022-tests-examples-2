/* eslint-disable @typescript-eslint/no-explicit-any */
import {cloneDeep} from 'lodash';
import moment from 'moment';
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {ProductStatus} from 'types/product';

import {getProductsHandler} from './get-products';

const BASE_BODY = {
    limit: 10,
    offset: 0
};

describe('get products by base filters', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return products in correct schema', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id,
            isMeta: true
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const productCombo = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            metaProductsIds: [product.id],
            productCombo: {
                code: 'product_combo_code',
                nameTranslationMap: {[lang.isoCode]: 'product_combo_name_1'}
            }
        });

        const {list, totalCount} = await getProductsHandler.handle({
            context,
            data: {
                body: BASE_BODY
            }
        });

        expect(totalCount).toBe(1);
        expect(list).toEqual([
            {
                identifier: product.identifier,
                code: product.code,
                status: product.status,
                isMeta: product.isMeta,
                infoModel: {
                    id: im.id,
                    code: im.code,
                    titleTranslations: {
                        [lang.isoCode]: 'info_model'
                    }
                },
                masterCategory: {
                    id: mc.id,
                    code: mc.code,
                    nameTranslations: {
                        [lang.isoCode]: 'master_category'
                    }
                },
                frontCategories: [
                    {
                        id: fc.id,
                        code: fc.code,
                        nameTranslations: {
                            [lang.isoCode]: 'front_category'
                        }
                    }
                ],
                createdAt: expect.any(Date),
                updatedAt: expect.any(Date),
                author: {
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last,
                    login: user.login
                },
                attributes: {},
                fullness: 0,
                langFilledAttributes: {},
                langFullness: {},
                langTotalAttributes: 0,
                langTotalFullness: 0,
                productCombos: [
                    {
                        id: productCombo.id,
                        uuid: productCombo.prefixedUuid,
                        nameTranslations: {[lang.isoCode]: 'product_combo_name_1'}
                    }
                ],
                attributesConfirmation: {},
                confirmation: 0,
                attributesMeta: {}
            }
        ]);
    });

    it('should return products with attributes when selectAttributeCodes has one attribute', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const notUsedAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}, {id: notUsedAttribute.id}]
        });

        const productAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: attribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: notUsedAttribute.id,
            productId: product.id,
            value: 'My Attribute Value Not Used'
        });

        const {list, totalCount} = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    selectAttributeCodes: [attribute.code] // skip notUsedAttribute.code
                }
            }
        });

        expect(totalCount).toBe(1);
        expect(list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {
                    [attribute.code]: productAttributeValue.value
                }
            }
        ]);
    });

    it('should return products with attributes when selectAttributeCodes is undefined', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}]
        });

        const productAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: attribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        const {list, totalCount} = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY
                    // selectAttributeCodes: [attribute.code] should return all
                }
            }
        });

        expect(totalCount).toBe(1);
        expect(list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {
                    [attribute.code]: productAttributeValue.value
                }
            }
        ]);
    });

    it('should return products without attributes when selectAttributeCodes is empty', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}]
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: attribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        const {list, totalCount} = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    selectAttributeCodes: []
                }
            }
        });

        expect(totalCount).toBe(1);
        expect(list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {}
            }
        ]);
    });

    it('should filter returned attributes by info models', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const notUsedAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}]
        });

        const productAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: attribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: notUsedAttribute.id,
            productId: product.id,
            value: 'My Attribute Value Not Used'
        });

        const {list, totalCount} = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    selectAttributeCodes: [attribute.code, notUsedAttribute.code]
                }
            }
        });

        expect(totalCount).toBe(1);
        expect(list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {
                    [attribute.code]: productAttributeValue.value
                }
            }
        ]);
    });

    it('should return products in correct region', async () => {
        const otherRegion = await TestFactory.createRegion();

        const [imRegion, imOtherRegion] = await Promise.all([
            TestFactory.createInfoModel({
                regionId: region.id,
                userId: user.id
            }),
            TestFactory.createInfoModel({
                regionId: otherRegion.id,
                userId: user.id
            })
        ]);

        const [mcRegion, mcOtherRegion] = await Promise.all([
            TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                infoModelId: imRegion.id
            }),
            TestFactory.createMasterCategory({
                userId: user.id,
                regionId: otherRegion.id,
                infoModelId: imOtherRegion.id
            })
        ]);

        const [productRegion, productOtherRegion] = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mcRegion.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mcOtherRegion.id,
                regionId: otherRegion.id
            })
        ]);

        const resRegion = await getProductsHandler.handle({
            context,
            data: {
                body: BASE_BODY
            }
        });

        expect(resRegion.totalCount).toBe(1);
        expect(resRegion.list).toMatchObject([{identifier: productRegion.identifier}]);

        const resOtherRegion = await getProductsHandler.handle({
            context: await TestFactory.createApiContext({region: otherRegion, user}),
            data: {
                body: BASE_BODY
            }
        });

        expect(resOtherRegion.totalCount).toBe(1);
        expect(resOtherRegion.list).toMatchObject([{identifier: productOtherRegion.identifier}]);
    });

    it('should return products by identifier', async () => {
        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const identifiers = (
            await Promise.all([
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                }),
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                }),
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            ])
        )
            .map((it) => it.identifier)
            .sort();

        const actionSuites = {
            range: [
                {
                    values: [null, identifiers[2]],
                    expectedIds: [identifiers[0], identifiers[1]]
                },
                {
                    values: [identifiers[1], null],
                    expectedIds: [identifiers[1], identifiers[2]]
                },
                {
                    values: [identifiers[1], identifiers[2]],
                    expectedIds: [identifiers[1]]
                }
            ],
            equal: [
                {
                    values: [identifiers[2]],
                    expectedIds: [identifiers[2]]
                }
            ],
            'not-equal': [
                {
                    values: [identifiers[2]],
                    expectedIds: [identifiers[0], identifiers[1]]
                }
            ]
        };

        for (const [action, suites] of Object.entries(actionSuites)) {
            for (const suite of suites) {
                const res = await getProductsHandler.handle({
                    context,
                    data: {
                        body: {
                            ...BASE_BODY,
                            filters: {
                                identifier: {
                                    action: action as any,
                                    values: suite.values
                                }
                            }
                        }
                    }
                });

                expect(res.totalCount).toBe(suite.expectedIds.length);
                expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
            }
        }
    });

    it('should return products by status', async () => {
        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const productActive = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            status: ProductStatus.ACTIVE,
            regionId: region.id
        });

        const productDisabled = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            status: ProductStatus.DISABLED,
            regionId: region.id
        });

        const suites = [
            {
                values: [ProductStatus.ACTIVE],
                expectedIds: [productActive.identifier]
            },
            {
                values: [ProductStatus.DISABLED],
                expectedIds: [productDisabled.identifier]
            },
            {
                values: [ProductStatus.ACTIVE, ProductStatus.DISABLED],
                expectedIds: [productActive.identifier, productDisabled.identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            status: suite.values
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
        }
    });

    it('should return products by master categories', async () => {
        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id
        });

        const products = await pMap(
            [mcRoot.id, mc.id],
            async (mcId) => {
                return TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mcId,
                    regionId: region.id
                });
            },
            {concurrency: 1}
        );

        const suites = [
            {
                values: [mc.id],
                expectedIds: [products[1].identifier]
            },
            {
                values: [mcRoot.id],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                values: [mcRoot.id, mc.id],
                expectedIds: [products[0].identifier, products[1].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            masterCategoryIds: suite.values
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
        }
    });

    it('should return products by front categories', async () => {
        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const fcRoot = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fcLevel1 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fcRoot.id,
            regionId: region.id
        });

        const fcsLevel2 = await Promise.all([
            TestFactory.createFrontCategory({
                userId: user.id,
                parentId: fcLevel1.id,
                regionId: region.id
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                parentId: fcLevel1.id,
                regionId: region.id
            })
        ]);

        const products = await pMap(
            [0, 1, 2],
            async () => {
                return TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                });
            },
            {concurrency: 1}
        );

        await Promise.all([
            TestFactory.createFrontCategoryProduct({
                userId: user.id,
                productId: products[0].id,
                frontCategoryId: fcsLevel2[0].id
            }),
            TestFactory.createFrontCategoryProduct({
                userId: user.id,
                productId: products[1].id,
                frontCategoryId: fcsLevel2[1].id
            }),
            TestFactory.createFrontCategoryProduct({
                userId: user.id,
                productId: products[2].id,
                frontCategoryId: fcsLevel2[0].id
            }),
            TestFactory.createFrontCategoryProduct({
                userId: user.id,
                productId: products[2].id,
                frontCategoryId: fcsLevel2[1].id
            })
        ]);

        const suites = [
            {
                values: [fcRoot.id],
                expectedIds: [products[0].identifier, products[1].identifier, products[2].identifier]
            },
            {
                values: [fcLevel1.id],
                expectedIds: [products[0].identifier, products[1].identifier, products[2].identifier]
            },
            {
                values: [fcsLevel2[0].id],
                expectedIds: [products[0].identifier, products[2].identifier]
            },
            {
                values: [fcsLevel2[1].id],
                expectedIds: [products[1].identifier, products[2].identifier]
            },
            {
                values: [fcLevel1.id, fcsLevel2[0].id],
                expectedIds: [products[0].identifier, products[1].identifier, products[2].identifier]
            },
            {
                values: [fcsLevel2[0].id, fcsLevel2[1].id],
                expectedIds: [products[0].identifier, products[1].identifier, products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            frontCategories: suite.values
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
        }
    });

    it('should return products by info models', async () => {
        const ims = await Promise.all([
            TestFactory.createInfoModel({
                regionId: region.id,
                userId: user.id
            }),
            TestFactory.createInfoModel({
                regionId: region.id,
                userId: user.id
            })
        ]);

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: ims[0].id
        });

        const mcInherited = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id
        });

        const mcWithOwnIm = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcInherited.id,
            infoModelId: ims[1].id
        });

        const products = await pMap(
            [mcRoot.id, mcInherited.id, mcWithOwnIm.id],
            async (mcId) => {
                return TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mcId,
                    regionId: region.id
                });
            },
            {concurrency: 1}
        );

        const suites = [
            {
                values: [ims[0].id],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                values: [ims[1].id],
                expectedIds: [products[2].identifier]
            },
            {
                values: [ims[0].id, ims[1].id],
                expectedIds: [products[0].identifier, products[1].identifier, products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            infoModelIds: suite.values
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
        }
    });

    it('should return products by created at, updated at', async () => {
        jest.setTimeout(20000);

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const products = await pMap(
            [1, 2],
            async () => {
                await new Promise((resolve) => setTimeout(resolve, 2500));

                return TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                });
            },
            {concurrency: 1}
        );

        const productsDb = await TestFactory.getProducts();

        const keys = ['createdAt', 'updatedAt'];

        for (const key of keys) {
            const min = moment((productsDb[0].historySubject as any)[key]);
            const max = moment((productsDb[1].historySubject as any)[key]);

            const suites = [
                {
                    values: [null, cloneDeep(min).subtract(10, 'seconds').unix()],
                    expectedIds: []
                },
                {
                    values: [null, cloneDeep(min).add(1, 'seconds').unix()],
                    expectedIds: [products[0].identifier]
                },
                {
                    values: [min.unix(), null],
                    expectedIds: [products[0].identifier, products[1].identifier]
                },
                {
                    values: [cloneDeep(min).add(1, 'seconds').unix(), null],
                    expectedIds: [products[1].identifier]
                },
                {
                    values: [min.unix(), max.unix()],
                    expectedIds: [products[0].identifier]
                },
                {
                    values: [min.unix(), cloneDeep(max).add(1, 'seconds').unix()],
                    expectedIds: [products[0].identifier, products[1].identifier]
                },
                {
                    values: [cloneDeep(min).add(1, 'seconds').unix(), cloneDeep(max).add(1, 'seconds').unix()],
                    expectedIds: [products[1].identifier]
                }
            ];

            for (const suite of suites) {
                const res = await getProductsHandler.handle({
                    context,
                    data: {
                        body: {
                            ...BASE_BODY,
                            filters: {
                                [`${key}Seconds`]: suite.values
                            }
                        }
                    }
                });

                expect(res.totalCount).toBe(suite.expectedIds.length);
                expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
            }
        }
    });

    it('should return products with unused attributed', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                [lang.isoCode]: 'front_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc.id
        });

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}]
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: attribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        const res1 = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        unused: {action: 'not-null', values: []}
                    }
                }
            }
        });

        expect(res1.totalCount).toBe(0);
        expect(res1.list).toMatchObject([]);

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attribute.id}]
        });

        const res2 = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        unused: {action: 'not-null', values: []}
                    }
                }
            }
        });

        expect(res2.totalCount).toBe(1);
        expect(res2.list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {}
            }
        ]);
    });

    // eslint-disable-next-line max-len
    it('should return product all attributes when withUnusedAttributes is true', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        const stringAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const booleanAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.BOOLEAN
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: stringAttribute.id}]
        });

        const stringAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: stringAttribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        const booleanAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: booleanAttribute.id,
            productId: product.id,
            value: true
        });

        const res1 = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    withUnusedAttributes: true,
                    selectAttributeCodes: [stringAttribute.code, booleanAttribute.code]
                }
            }
        });

        expect(res1.totalCount).toBe(1);
        expect(res1.list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {
                    [stringAttribute.code]: stringAttributeValue.value,
                    [booleanAttribute.code]: booleanAttributeValue.value
                }
            }
        ]);
    });

    // eslint-disable-next-line max-len
    it('should return product with info-model attributed when withUnusedAttributes is false', async () => {
        const lang = await TestFactory.createLang();

        const im = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            infoModel: {
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model'
                }
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                [lang.isoCode]: 'master_category'
            }
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            regionId: region.id
        });

        const stringAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const booleanAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.BOOLEAN
            }
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: stringAttribute.id}]
        });

        const stringAttributeValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: stringAttribute.id,
            productId: product.id,
            value: 'My Attribute Value'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            attributeId: booleanAttribute.id,
            productId: product.id,
            value: true
        });

        const res1 = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    withUnusedAttributes: false,
                    selectAttributeCodes: [stringAttribute.code, booleanAttribute.code]
                }
            }
        });

        expect(res1.totalCount).toBe(1);
        expect(res1.list).toMatchObject([
            {
                identifier: product.identifier,
                attributes: {
                    [stringAttribute.code]: stringAttributeValue.value
                }
            }
        ]);
    });
});
