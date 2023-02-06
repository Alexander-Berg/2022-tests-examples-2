import {sortBy} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    DuplicatesValidationError,
    EntitiesFromDifferentRegionsError,
    EntityNotFoundError,
    ForbidMasterCategoryWithChildren,
    InvalidAttributeValues,
    NotLeafCategoryError,
    NotUniqueBarcodeError,
    UnknownAttributesError
} from '@/src/errors';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';
import {ProductStatus} from 'types/product';

import {updateProductHandler} from './update-product';

async function createFrontCategory(user: User, region: Region) {
    const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
    const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
    return TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});
}

async function createBaseProduct(user: User, region: Region) {
    const attribute = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            type: AttributeType.TEXT,
            isUnique: true
        }
    });

    const fc = await createFrontCategory(user, region);
    const im = await TestFactory.createInfoModel({
        userId: user.id,
        regionId: region.id,
        attributes: [
            {
                id: attribute.id
            }
        ]
    });

    const mc = await TestFactory.createMasterCategory({
        userId: user.id,
        regionId: region.id,
        infoModelId: im.id
    });

    const product = await TestFactory.createProduct({
        userId: user.id,
        regionId: region.id,
        masterCategoryId: mc.id
    });

    await TestFactory.createFrontCategoryProduct({
        userId: user.id,
        frontCategoryId: fc.id,
        productId: product.id
    });

    await TestFactory.createProductAttributeValue({
        userId: user.id,
        productId: product.id,
        attributeId: attribute.id,
        value: 'foobar'
    });

    return {mc, product, im, fc, attribute};
}

describe('update product', () => {
    let context: ApiRequestContext;
    let region: Region;
    let user: User;
    let lang: Lang;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang();
        await TestFactory.createLocale({regionId: region.id, langIds: [lang.id]});
        context = await TestFactory.createApiContext({lang, user, region});
    });

    it('should update product with correct input data', async () => {
        const {product, attribute, im, mc: mcParent} = await createBaseProduct(user, region);

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcParent.id
        });

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    // should ignore code in body
                    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                    // @ts-ignore
                    code: Math.random().toString(),
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc.id,
                    frontCategoryIds: [fc2.id],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: 'foo'
                        }
                    ]
                }
            }
        });

        expect(result).toEqual({
            id: product.id,
            identifier: product.identifier,
            code: product.identifier.toString(),
            status: ProductStatus.ACTIVE,
            isMeta: product.isMeta,
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            infoModel: {
                id: im.id,
                code: im.code,
                titleTranslations: {}
            },
            masterCategory: {
                id: mc.id,
                code: mc.code,
                nameTranslations: {},
                breadcrumbs: [
                    {
                        id: mcParent.id,
                        code: mcParent.code,
                        nameTranslations: {}
                    },
                    {
                        id: mc.id,
                        code: mc.code,
                        nameTranslations: {}
                    }
                ]
            },
            frontCategories: [
                {
                    id: fc2.id,
                    code: fc2.code,
                    status: fc2.status,
                    imageUrl: fc2.imageUrl,
                    nameTranslations: {}
                }
            ],
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date),
            author: user.formatAuthor(),
            attributes: [
                {
                    attributeId: attribute.id,
                    value: 'foo'
                }
            ],
            // отсутствие обязательных атрибутов - 100% заполненности товара
            fullness: 100,
            productCombos: []
        });
    });

    it('should throw error if product does not exists', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        const {mc} = await createBaseProduct(user, region);

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: unknownId
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Product'});
    });

    it('should throw error if master category does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        const {product, fc} = await createBaseProduct(user, region);

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: unknownId,
                        frontCategoryIds: [fc.id],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'MasterCategory'});
    });

    it('should throw error if there are duplicated attribute ids', async () => {
        let error = null;

        const {product, fc, mc} = await createBaseProduct(user, region);

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc.id],
                        attributes: [
                            {
                                attributeId: 1,
                                value: 1
                            },
                            {
                                attributeId: 1,
                                value: 2
                            }
                        ]
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(DuplicatesValidationError);
    });

    it('should throw error if master category is not leaf', async () => {
        let error = null;

        const {product, mc: baseMc} = await createBaseProduct(user, region);

        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            parentId: baseMc.id
        });
        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            parentId: mc.id
        });

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(ForbidMasterCategoryWithChildren);
    });

    it('should throw error if front categories are not leaf', async () => {
        let error = null;

        const {product, mc} = await createBaseProduct(user, region);

        const fc = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        status: ProductStatus.ACTIVE,
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc.id],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(NotLeafCategoryError);
    });

    it('should not throw error if there are not requested attributes in info model', async () => {
        let error = null;

        const {product, mc} = await createBaseProduct(user, region);

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER
            }
        });

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attribute.id,
                                value: 1
                            }
                        ]
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(UnknownAttributesError);
    });

    it('should throw error if attribute value invalid', async () => {
        let error = null;

        const {product, mc, attribute} = await createBaseProduct(user, region);

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attribute.id,
                                value: true
                            }
                        ]
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(InvalidAttributeValues);
    });

    it('should throw error if values are not uniq', async () => {
        let error = null;

        const {product, attribute, mc: mcParent} = await createBaseProduct(user, region);

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            parentId: mcParent.id
        });

        const p = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            code: String(Math.random()),
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: p.id,
            attributeId: attribute.id,
            value: 'newfoobar'
        });

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: attribute.id,
                                value: 'newfoobar'
                            }
                        ]
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(NotUniqueBarcodeError);
    });

    it('should ignore itself uniq value', async () => {
        const {product, mc, attribute} = await createBaseProduct(user, region);

        const data = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: 'foobar'
                        }
                    ]
                }
            }
        });

        expect(data.identifier).toBe(product.identifier);
    });

    it('should throw error if front categories from another region', async () => {
        let error = null;

        const otherRegion = await TestFactory.createRegion();
        const {product, mc} = await createBaseProduct(user, region);

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: otherRegion.id});
        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: otherRegion.id,
            parentId: fc0.id
        });
        const fc2 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: otherRegion.id,
            parentId: fc1.id
        });

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc2.id],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntitiesFromDifferentRegionsError);
    });

    it('should throw error if master category from another region', async () => {
        let error = null;

        const otherRegion = await TestFactory.createRegion();
        const {product, im} = await createBaseProduct(user, region);

        const otherIm = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: otherRegion.id,
            attributes: im.attributes
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: otherRegion.id,
            infoModelId: otherIm.id
        });

        try {
            await updateProductHandler.handle({
                context,
                data: {
                    params: {
                        identifier: product.identifier
                    },
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntitiesFromDifferentRegionsError);
    });

    it('should not insert empty value in db', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT
            }
        });

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: ''
                        }
                    ]
                }
            }
        });

        expect(result.attributes).toEqual([]);
    });

    it('should not insert empty localizable value in db', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT,
                isValueLocalizable: true
            }
        });
        const lang = await TestFactory.createLang({isoCode: 'ru'});

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: {
                                [lang.isoCode]: ''
                            }
                        }
                    ]
                }
            }
        });

        expect(result.attributes).toEqual([]);
    });

    it('should update only changed array value', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT,
                    isArray: true
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT,
                    isArray: true
                }
            })
        ]);

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                },
                {
                    id: attributes[1].id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            value: ['foo', 'bar']
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            value: ['qwe', 'zxc']
        });

        const historyBefore = await TestFactory.getHistory();

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: ['foo', 'bar']
                        },
                        {
                            attributeId: attributes[1].id,
                            value: ['ert', 'yui']
                        }
                    ]
                }
            }
        });

        expect(sortBy(result.attributes, 'attributeId')).toEqual(
            sortBy(
                [
                    {
                        attributeId: attributes[0].id,
                        value: ['foo', 'bar']
                    },
                    {
                        attributeId: attributes[1].id,
                        value: ['ert', 'yui']
                    }
                ],
                'attributeId'
            )
        );

        const historyAfter = await TestFactory.getHistory();
        expect(historyAfter.length - historyBefore.length).toBe(1);
    });

    it('should update only changed primitive value', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            })
        ]);

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                },
                {
                    id: attributes[1].id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            value: 'foo'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            value: 'qwe'
        });

        const historyBefore = await TestFactory.getHistory();

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'foo'
                        },
                        {
                            attributeId: attributes[1].id,
                            value: 'zxc'
                        }
                    ]
                }
            }
        });

        expect(sortBy(result.attributes, 'attributeId')).toEqual(
            sortBy(
                [
                    {
                        attributeId: attributes[0].id,
                        value: 'foo'
                    },
                    {
                        attributeId: attributes[1].id,
                        value: 'zxc'
                    }
                ],
                'attributeId'
            )
        );

        const historyAfter = await TestFactory.getHistory();
        expect(historyAfter.length - historyBefore.length).toBe(1);
    });

    it('should update only changed primitive value with lang', async () => {
        const langs = await Promise.all([
            TestFactory.createLang({isoCode: 'ru'}),
            TestFactory.createLang({isoCode: 'fr'})
        ]);

        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.STRING,
                    isValueLocalizable: true
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.STRING,
                    isValueLocalizable: true
                }
            })
        ]);

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                },
                {
                    id: attributes[1].id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            langId: langs[0].id,
            value: 'foo1'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            langId: langs[1].id,
            value: 'foo2'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            langId: langs[0].id,
            value: 'qwe1'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            langId: langs[1].id,
            value: 'qwe2'
        });

        const historyBefore = await TestFactory.getHistory();

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: {
                                [langs[0].isoCode]: 'foo1',
                                [langs[1].isoCode]: 'foo3'
                            }
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'qwe1',
                                [langs[1].isoCode]: 'qwe3'
                            }
                        }
                    ]
                }
            }
        });

        expect(sortBy(result.attributes, 'attributeId')).toEqual(
            sortBy(
                [
                    {
                        attributeId: attributes[0].id,
                        value: {
                            [langs[0].isoCode]: 'foo1',
                            [langs[1].isoCode]: 'foo3'
                        }
                    },
                    {
                        attributeId: attributes[1].id,
                        value: {
                            [langs[0].isoCode]: 'qwe1',
                            [langs[1].isoCode]: 'qwe3'
                        }
                    }
                ],
                'attributeId'
            )
        );

        const historyAfter = await TestFactory.getHistory();
        expect(historyAfter.length - historyBefore.length).toBe(2);
    });

    it('should not delete incompatible attributes when master category is not changed', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            })
        ]);

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                },
                {
                    id: attributes[1].id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            value: 'foo'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            value: 'bar'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[2].id,
            value: 'baz'
        });

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'foo'
                        }
                    ]
                }
            }
        });

        expect(sortBy(result.attributes, 'attributeId')).toEqual(
            sortBy(
                [
                    {
                        attributeId: attributes[0].id,
                        value: 'foo'
                    }
                ],
                'attributeId'
            )
        );

        const history = await TestFactory.getHistory();
        const deleteHistory = history.filter(({action}) => action === 'D');

        expect(deleteHistory).toHaveLength(2);
        expect(deleteHistory).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    oldRow: expect.objectContaining({attribute_id: String(attributes[1].id)})
                })
            ])
        );
    });

    it('should delete incompatible attributes when master category is changed', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            })
        ]);

        const rootIm = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });
        const im1 = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                },
                {
                    id: attributes[1].id
                }
            ]
        });
        const im2 = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[0].id
                }
            ]
        });

        const rootMc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootIm.id
        });
        const mc1 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMc.id,
            infoModelId: im1.id
        });
        const mc2 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMc.id,
            infoModelId: im2.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: mc1.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[0].id,
            value: 'foo'
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attributes[1].id,
            value: 'bar'
        });

        const result = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    masterCategoryId: mc2.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'foo'
                        }
                    ]
                }
            }
        });

        expect(sortBy(result.attributes, 'attributeId')).toEqual(
            sortBy(
                [
                    {
                        attributeId: attributes[0].id,
                        value: 'foo'
                    }
                ],
                'attributeId'
            )
        );

        const history = await TestFactory.getHistory();
        const deleteHistory = history.filter(({action}) => action === 'D');

        expect(deleteHistory).toHaveLength(1);
    });
});
