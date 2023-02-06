/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    DuplicatesValidationError,
    EntitiesFromDifferentRegionsError,
    EntityConflictError,
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

import {createProductHandler} from './create-product';

describe('create product', () => {
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

    it('should create product with correct input data', async () => {
        const attribute1 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER
            }
        });
        const attribute2 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });
        const attribute3 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT
            }
        });

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});
        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute1.id
                },
                {
                    id: attribute2.id,
                    isImportant: true
                },
                {
                    id: attribute3.id,
                    isImportant: true
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

        const result = await createProductHandler.handle({
            context,
            data: {
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc.id,
                    frontCategoryIds: [fc2.id],
                    attributes: [
                        {
                            attributeId: attribute1.id,
                            value: 100,
                            isConfirmed: true
                        },
                        {
                            attributeId: attribute2.id,
                            value: 'abc',
                            isConfirmed: false
                        }
                    ]
                }
            }
        });

        const expectedCode = String(result.identifier);

        expect(result).toEqual({
            id: expect.any(Number),
            identifier: expect.any(Number),
            code: expectedCode,
            status: ProductStatus.ACTIVE,
            isMeta: false,
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
                    attributeId: attribute1.id,
                    value: 100,
                    isConfirmed: true
                },
                {
                    attributeId: attribute2.id,
                    value: 'abc',
                    isConfirmed: false
                }
            ],
            fullness: 50,
            productCombos: [],
            confirmation: 100
        });
    });

    it('should throw error if master category does not a leaf', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        // masterCategory
        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: infoModel.id
        });

        let error = null;

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: rootMasterCategory.id,
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

    it('should throw error if master category does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: unknownId,
                        frontCategoryIds: [],
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

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: 1,
                        frontCategoryIds: [],
                        attributes: [
                            {
                                attributeId: 1,
                                value: 1,
                                isConfirmed: false
                            },
                            {
                                attributeId: 1,
                                value: 2,
                                isConfirmed: false
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

        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});
        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});
        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            parentId: mc.id
        });

        try {
            await createProductHandler.handle({
                context,
                data: {
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

        expect(error).toBeInstanceOf(ForbidMasterCategoryWithChildren);
    });

    it('should throw error if front categories are not leaf', async () => {
        let error = null;

        const fc = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});
        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
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

    it('should throw error if there are not requested attributes in info model', async () => {
        let error = null;

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER
            }
        });

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});
        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });
        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc2.id],
                        attributes: [
                            {
                                attributeId: Number.MAX_SAFE_INTEGER,
                                value: 1,
                                isConfirmed: false
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

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                isArray: true
            }
        });

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });

        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc2.id],
                        attributes: [
                            {
                                attributeId: attribute.id,
                                value: [1],
                                isConfirmed: false
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

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                isArray: true,
                isUnique: true
            }
        });

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });

        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

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
            value: ['foobar']
        });

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc2.id],
                        attributes: [
                            {
                                attributeId: attribute.id,
                                value: ['foobar'],
                                isConfirmed: false
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

    it('should throw error if front categories from another region', async () => {
        let error = null;

        const otherRegion = await TestFactory.createRegion();

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

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});

        try {
            await createProductHandler.handle({
                context,
                data: {
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

    it('should throw error if code already exists in region', async () => {
        let error = null;

        const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
        const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
        const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});
        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const mc = await TestFactory.createMasterCategory({userId: user.id, regionId: region.id, infoModelId: im.id});
        const p = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: mc.id,
            code: String(Math.random()),
            regionId: region.id
        });

        try {
            await createProductHandler.handle({
                context,
                data: {
                    body: {
                        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                        //@ts-ignore
                        code: p.code,
                        masterCategoryId: mc.id,
                        frontCategoryIds: [fc2.id],
                        attributes: []
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityConflictError);
    });

    it('should throw error if master category from another region', async () => {
        let error = null;

        const otherRegion = await TestFactory.createRegion();

        const im = await TestFactory.createInfoModel({userId: user.id, regionId: otherRegion.id});
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: otherRegion.id,
            infoModelId: im.id
        });

        try {
            await createProductHandler.handle({
                context,
                data: {
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

        const result = await createProductHandler.handle({
            context,
            data: {
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: '',
                            isConfirmed: true
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

        const result = await createProductHandler.handle({
            context,
            data: {
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: {
                                [lang.isoCode]: ''
                            },
                            isConfirmed: {
                                [lang.isoCode]: false
                            }
                        }
                    ]
                }
            }
        });

        expect(result.attributes).toEqual([]);
    });

    it('should insert confirmation for only exists localization at localizable value in db', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT,
                isValueLocalizable: true
            }
        });

        const langs = await Promise.all([
            await TestFactory.createLang({isoCode: 'ru'}),
            await TestFactory.createLang({isoCode: 'en'})
        ]);

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

        const result = await createProductHandler.handle({
            context,
            data: {
                body: {
                    masterCategoryId: mc.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attribute.id,
                            value: {
                                [langs[0].isoCode]: '',
                                [langs[1].isoCode]: 'test'
                            },
                            isConfirmed: {
                                [langs[0].isoCode]: false,
                                [langs[1].isoCode]: true
                            }
                        }
                    ]
                }
            }
        });

        expect(result.attributes).toEqual([
            {
                attributeId: attribute.id,
                value: {
                    [langs[1].isoCode]: 'test'
                },
                isConfirmed: {
                    [langs[1].isoCode]: true
                }
            }
        ]);
    });
});
