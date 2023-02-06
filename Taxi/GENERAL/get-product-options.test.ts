import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getProductOptionsHandler} from './get-product-options';

describe('get product combo options', () => {
    let user: User;
    let langs: [Lang, Lang];
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProducts: [Product, Product, Product];
    let realProducts: [Product, Product, Product];
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
    });

    it('should find real products', async () => {
        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    isMeta: false
                }
            }
        });

        await expect(products).toEqual({
            list: realProducts
                .slice()
                .sort((a, b) => a.id - b.id)
                .map((it) => ({
                    id: it.id,
                    identifier: it.identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                    },
                    images: []
                })),
            totalCount: 3
        });
    });

    it('should find meta products', async () => {
        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    isMeta: true
                }
            }
        });

        await expect(products).toEqual({
            list: metaProducts
                .slice()
                .sort((a, b) => a.id - b.id)
                .map((it) => ({
                    id: it.id,
                    identifier: it.identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                    },
                    images: []
                })),
            totalCount: 3
        });
    });

    it('should respect limit and offset', async () => {
        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 1,
                    offset: 1,
                    isMeta: false
                }
            }
        });

        await expect(products).toEqual({
            list: realProducts
                .slice()
                .sort((a, b) => b.id - a.id)
                .slice(1, 2)
                .map((it) => ({
                    id: it.id,
                    identifier: it.identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${it.id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${it.id}_${langs[1].id}`
                    },
                    images: []
                })),
            totalCount: 3
        });
    });

    it('should find products by identifier', async () => {
        const skuId = realProducts[1].identifier.toString();

        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    isMeta: false,
                    search: skuId
                }
            }
        });

        await expect(products).toEqual({
            list: [
                {
                    id: realProducts[1].id,
                    identifier: realProducts[1].identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${realProducts[1].id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${realProducts[1].id}_${langs[1].id}`
                    },
                    images: []
                }
            ],
            totalCount: 1
        });
    });

    it('should find products by barcode', async () => {
        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    isMeta: true,
                    search: `product_barcode_${metaProducts[1].id}`
                }
            }
        });

        await expect(products).toEqual({
            list: [
                {
                    id: metaProducts[1].id,
                    identifier: metaProducts[1].identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${metaProducts[1].id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${metaProducts[1].id}_${langs[1].id}`
                    },
                    images: []
                }
            ],
            totalCount: 1
        });
    });

    it('should find products by name', async () => {
        const products = await getProductOptionsHandler.handle({
            context,
            data: {
                body: {
                    limit: 20,
                    offset: 0,
                    isMeta: false,
                    search: `product_name_${realProducts[1].id}`
                }
            }
        });

        await expect(products).toEqual({
            list: [
                {
                    id: realProducts[1].id,
                    identifier: realProducts[1].identifier,
                    name: {
                        [langs[0].isoCode]: `product_name_${realProducts[1].id}_${langs[0].id}`,
                        [langs[1].isoCode]: `product_name_${realProducts[1].id}_${langs[1].id}`
                    },
                    images: []
                }
            ],
            totalCount: 1
        });
    });
});
