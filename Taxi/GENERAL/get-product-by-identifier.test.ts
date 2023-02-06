/* eslint-disable @typescript-eslint/no-explicit-any */
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {EntityNotFoundError} from '@/src/errors';
import {AttributeType} from '@/src/types/attribute';

import {getProductByIdentifierApiHandler} from './get-product-by-identifier';

interface ExecuteHandlerParams {
    identifier: string;
    region: string;
}

function executeHandler({identifier, region}: ExecuteHandlerParams): Promise<any> {
    return new Promise((resolve, reject) => {
        getProductByIdentifierApiHandler(
            {
                params: {identifier},
                header: (name: string): string | undefined => {
                    if (name === REGION_HEADER) {
                        return region;
                    }

                    return;
                }
            } as any,
            {json: resolve} as any,
            reject
        );
    });
}

describe('get product by identifier', () => {
    it('should return full product info', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER,
                isArray: false,
                isValueLocalizable: false
            }
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ],
            infoModel: {
                titleTranslationMap: {
                    [langs[0].isoCode]: 'foo_info_model'
                }
            }
        });

        const mc0 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            nameTranslationMap: {
                [langs[0].isoCode]: 'zxcqwe'
            }
        });

        const mc1 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mc0.id
        });

        const fc0 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc0.id,
            regionId: region.id
        });

        const fc2 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            nameTranslationMap: {
                [langs[0].isoCode]: 'fc'
            }
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc1.id,
            userId: user.id,
            regionId: region.id,
            isMeta: true
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: fc2.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            value: 1231
        });

        const productCombo = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            metaProductsIds: [product.id],
            productCombo: {
                code: 'product_combo_code',
                nameTranslationMap: {[langs[0].isoCode]: 'product_combo_name_1'}
            }
        });

        const response = await executeHandler({
            identifier: String(product.identifier),
            region: region.isoCode
        });

        expect(response).toEqual({
            id: product.id,
            code: product.code,
            identifier: product.identifier,
            status: product.status,
            isMeta: true,
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            infoModel: {
                id: infoModel.id,
                code: infoModel.code,
                titleTranslations: {
                    [langs[0].isoCode]: 'foo_info_model'
                }
            },
            masterCategory: {
                id: mc1.id,
                code: mc1.code,
                nameTranslations: {},
                breadcrumbs: [
                    {
                        id: mc0.id,
                        code: mc0.code,
                        nameTranslations: {
                            [langs[0].isoCode]: 'zxcqwe'
                        }
                    },
                    {
                        id: mc1.id,
                        code: mc1.code,
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
                    nameTranslations: {
                        [langs[0].isoCode]: 'fc'
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
            attributes: [
                {
                    attributeId: attribute.id,
                    value: 1231,
                    isConfirmed: false
                }
            ],
            fullness: 0,
            productCombos: [
                {
                    id: productCombo.id,
                    uuid: productCombo.prefixedUuid,
                    nameTranslations: {[langs[0].isoCode]: 'product_combo_name_1'}
                }
            ],
            confirmation: 0
        });
    });

    it('should return localized values', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                isArray: false,
                isValueLocalizable: true
            }
        });

        const infoModel = await TestFactory.createInfoModel({
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
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            langId: langs[0].id,
            value: 'foo',
            isConfirmed: true
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            langId: langs[1].id,
            value: 'bar',
            isConfirmed: false
        });

        const response = await executeHandler({
            identifier: String(product.identifier),
            region: region.isoCode
        });

        expect(response.attributes).toEqual([
            {
                attributeId: attribute.id,
                value: {
                    [langs[0].isoCode]: 'foo',
                    [langs[1].isoCode]: 'bar'
                },
                isConfirmed: {
                    [langs[0].isoCode]: true,
                    [langs[1].isoCode]: false
                }
            }
        ]);
    });

    it('should return primitive values', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();

        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.BOOLEAN,
                isArray: true,
                isValueLocalizable: false
            }
        });

        const infoModel = await TestFactory.createInfoModel({
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
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            value: [false, true]
        });

        const response = await executeHandler({
            identifier: String(product.identifier),
            region: region.isoCode
        });

        expect(response.attributes).toEqual([
            {
                attributeId: attribute.id,
                value: [false, true],
                isConfirmed: false
            }
        ]);
    });

    it('should return error if product from other region', async () => {
        let error = null;
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        try {
            await executeHandler({
                identifier: product.identifier.toString(),
                region: otherRegion.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Product'});
    });

    it('should return error if product does not exist', async () => {
        let error = null;
        const region = await TestFactory.createRegion();
        const unknownId = `${Number.MAX_SAFE_INTEGER}`;

        try {
            await executeHandler({
                identifier: unknownId,
                region: region.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Product'});
    });
});
