import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getProductsHandler} from './get-products';

const BASE_BODY = {
    limit: 10,
    offset: 0
};

async function createBase(region: Region, user: User) {
    const im = await TestFactory.createInfoModel({
        regionId: region.id,
        userId: user.id
    });

    const mc = await TestFactory.createMasterCategory({
        userId: user.id,
        regionId: region.id,
        infoModelId: im.id
    });

    return {im, mc};
}

describe('get products by search', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    async function createAttributeAndLink(params: DeepPartial<Attribute>, infoModelId?: number | null) {
        const attr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: params
        });

        if (infoModelId) {
            await TestFactory.linkAttributesToInfoModel({
                userId: user.id,
                attributes: [attr],
                infoModelId
            });
        }

        return attr;
    }

    it('should return products without filters', async () => {
        const {mc} = await createBase(region, user);

        const nameAttributeValue = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC},
            mc.infoModelId
        );

        const barcodeAttributeValue = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.BARCODE, isArray: true},
            mc.infoModelId
        );

        const products = await Promise.all(
            Array.from({length: 4}).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: nameAttributeValue.id,
                value: 'existing name'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: barcodeAttributeValue.id,
                value: ['existing barcode']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: nameAttributeValue.id,
                value: 'missed name'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: barcodeAttributeValue.id,
                value: ['missed barcode']
            })
        ]);

        const foundProducts = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    search: 'existing'
                }
            }
        });

        expect(foundProducts.totalCount).toBe(2);
        expect(foundProducts.list.map((p) => p.identifier).sort()).toEqual(
            products
                .slice(0, 2)
                .map((p) => p.identifier)
                .sort()
        );
    });

    it('should return products with filters', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC},
            mc.infoModelId
        );

        const products = await Promise.all(
            Array.from({length: 3}).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: 'common one'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: 'common two'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: 'missed one'
            })
        ]);

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {action: 'contain', values: ['common']}
                        }
                    },
                    search: 'common one'
                }
            }
        });

        expect(res.totalCount).toBe(1);
        expect(res.list.map((p) => p.identifier)).toEqual([products[0].identifier]);
    });

    it('should find products by barcode correctly', async () => {
        const {mc} = await createBase(region, user);

        const barcodeAttribute = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.BARCODE, isArray: true},
            mc.infoModelId
        );

        const products = await Promise.all(
            Array.from({length: 3}).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: barcodeAttribute.id,
                value: ['foobar']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: barcodeAttribute.id,
                value: ['abcabc', 'foobaz']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: barcodeAttribute.id,
                value: ['aaaaaa', 'bbbbbb']
            })
        ]);

        const foundProducts = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    search: 'foo'
                }
            }
        });

        expect(foundProducts.totalCount).toBe(2);
        expect(foundProducts.list.map((p) => p.identifier)).toEqual([products[0].identifier, products[1].identifier]);
    });

    it('should find products by part of identifier', async () => {
        const {mc} = await createBase(region, user);

        const barcodeAttribute = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.BARCODE, isArray: true},
            mc.infoModelId
        );

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id,
                identifier: 123
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id,
                identifier: 1234
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id,
                identifier: 456123
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: barcodeAttribute.id,
                value: ['aaaaaa']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: barcodeAttribute.id,
                value: ['bbbbbb']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: barcodeAttribute.id,
                value: ['cccccc']
            })
        ]);

        const foundProducts = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    search: '123'
                }
            }
        });

        expect(foundProducts.totalCount).toBe(2);
        expect(foundProducts.list.map((p) => p.identifier)).toEqual([products[0].identifier, products[1].identifier]);
    });

    it('should find products by name words ignoring other symbols', async () => {
        const {mc} = await createBase(region, user);

        const nameAttributeValue = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC},
            mc.infoModelId
        );

        const products = await Promise.all(
            Array.from({length: 4}).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: nameAttributeValue.id,
                value: '100% "awesome" product'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: nameAttributeValue.id,
                value: '"awesome" product, 100%'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: nameAttributeValue.id,
                value: 'not so "awesome" product'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: nameAttributeValue.id,
                value: '100% product but too "aaawesome"'
            })
        ]);

        const foundProducts = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    search: '100 awesome'
                }
            }
        });

        expect(foundProducts.totalCount).toBe(2);
        expect(foundProducts.list.map((p) => p.identifier)).toEqual([products[0].identifier, products[1].identifier]);
    });

    it('should return no products', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink(
            {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC},
            mc.infoModelId
        );

        const products = await Promise.all(
            Array.from({length: 3}).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: 'hello world'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: 'foo'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: 'bar'
            })
        ]);

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {action: 'contain', values: ['common']}
                        }
                    },
                    search: 'NOT FOUND'
                }
            }
        });

        expect(res.totalCount).toBe(0);
        expect(res.list).toHaveLength(0);
    });
});
