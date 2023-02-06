import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {attributesFactory, TestFactory} from 'tests/unit/test-factory';

import {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {env} from 'service/cfg';
import {ensureConnection} from 'service/db';
import {AttributeType} from 'types/attribute';
import {ProductStatus} from 'types/product';

import {defaultClientAttributes} from './client-attributes';
import {getActualProducts} from './index';

async function createFrontCategory(user: User, region: Region) {
    const fc0 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id});
    const fc1 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc0.id});
    const fc2 = await TestFactory.createFrontCategory({userId: user.id, regionId: region.id, parentId: fc1.id});

    return fc2;
}

export async function createBase(user: User) {
    const attributeShortNameLoc = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'shortNameLoc',
            type: AttributeType.TEXT,
            isValueLocalizable: true
        }
    });

    const attributeLongName = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'longName',
            type: AttributeType.TEXT,
            isValueLocalizable: true
        }
    });

    const attributeLongNameLoc = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'longNameLoc',
            type: AttributeType.TEXT,
            isValueLocalizable: true
        }
    });

    const attributeMarkCount = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'markCount',
            type: AttributeType.NUMBER
        }
    });

    const attributeMarkAmountUnit = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'markCountUnit',
            type: AttributeType.TEXT
        }
    });

    const attribute = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'attribute_for_testing',
            type: AttributeType.TEXT
        }
    });

    const attributeLoc = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'attr_loc',
            type: AttributeType.TEXT,
            isValueLocalizable: true
        }
    });
    const baseAttributes = await attributesFactory(user, [
        {
            code: 'countryISO',
            type: AttributeType.MULTISELECT,
            properties: {
                options: [{code: 'ABC'}, {code: 'XXX'}]
            }
        }
    ]);
    const baseAttributesValues = [['ABC']];

    const region = await TestFactory.createRegion();
    const role = await TestFactory.createRole({product: {canEdit: true}});
    await TestFactory.createUserRole({
        userId: user.id,
        roleId: role.id,
        regionId: region.id
    });
    const lang = await TestFactory.createLang({isoCode: 'ru'});
    await TestFactory.createLocale({regionId: region.id, langIds: [lang.id]});
    const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});
    await TestFactory.linkAttributesToInfoModel({
        userId: user.id,
        infoModelId: im.id,
        attributes: [
            attributeMarkCount,
            attributeLoc,
            attributeLongName,
            attributeLongNameLoc,
            attributeShortNameLoc,
            attributeMarkAmountUnit,
            attribute,
            ...baseAttributes
        ]
    });

    const mc = await TestFactory.createMasterCategory({
        userId: user.id,
        regionId: region.id,
        infoModelId: im.id
    });

    const fc = await createFrontCategory(user, region);
    const product1 = await TestFactory.createProduct({userId: user.id, regionId: region.id, masterCategoryId: mc.id});
    const product2 = await TestFactory.createProduct({userId: user.id, regionId: region.id, masterCategoryId: mc.id});

    await Promise.all([
        TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product1.id,
            frontCategoryId: fc.id
        }),
        TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product2.id,
            frontCategoryId: fc.id
        })
    ]);

    await Promise.all(
        [
            attributeMarkCount,
            attributeLoc,
            attributeLongName,
            attributeLongNameLoc,
            attributeShortNameLoc,
            attributeMarkAmountUnit,
            attribute
        ].map(async (it, i) => {
            return TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product1.id,
                attributeId: it.id,
                langId: [1, 2, 3, 4].includes(i) ? lang.id : undefined,
                value: i === 0 ? 1.2 : [1, 2, 3, 4].includes(i) ? 'loc_foo' : 'foo'
            });
        })
    );

    await Promise.all(
        [
            attributeMarkCount,
            attributeShortNameLoc,
            attributeLongName,
            attributeLongNameLoc,
            attributeMarkAmountUnit,
            attribute
        ].map(async (it, i) => {
            return TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product2.id,
                attributeId: it.id,
                langId: [1, 2, 3].includes(i) ? lang.id : undefined,
                value: i === 0 ? 1.2 : 'foo'
            });
        })
    );

    const basePAVs = [product1, product2].map(async (p) => {
        const a = baseAttributes.map(async (a, j) => {
            return TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: p.id,
                attributeId: a.id,
                value: baseAttributesValues[j]
            });
        });
        return await Promise.all(a);
    });
    await Promise.all(basePAVs);

    return {region, role, lang, product1, product2, im, mc, fc, attribute};
}

describe('get actual products', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return actual products after cursor', async () => {
        const {product1, product2, region, fc, im, mc} = await createBase(user);
        const skuId = product1.identifier.toString();

        const data1 = await getActualProducts({limit: 1, lastCursor: 0});
        data1.items[0].clientAttributes.localizationAttributes.sort((a, b) => (a?.name > b?.name ? 1 : -1));
        expect(data1.items).toEqual([
            {
                amount: 1.2,
                amountUnit: 'foo',
                barcode: [],
                businessCluster: region.isoCode,
                masterCategory: `master:${region.isoCode}:${mc.code}`,
                frontCategories: [`front:${region.isoCode}:${fc.code}`],
                family: im.code,
                images: [],
                legalRestrictions: [],
                longTitle: {
                    ['ru_RU']: 'loc_foo, 1.2 foo'
                },
                order: 100,
                skuId,
                status: product1.status,
                isMeta: false,
                title: {
                    ['ru_RU']: 'loc_foo'
                },
                created: expect.any(Number),
                updated: expect.any(Number),
                attributes: {
                    markCount: 1.2,
                    markCountUnit: 'foo',
                    shortNameLoc: {
                        ru_RU: 'loc_foo'
                    },
                    longName: {
                        ru_RU: 'loc_foo'
                    },
                    longNameLoc: {
                        ru_RU: 'loc_foo'
                    },
                    attribute_for_testing: 'foo',
                    countryISO: ['ABC'],
                    attr_loc: {
                        ru_RU: 'loc_foo'
                    }
                },
                clientAttributes: {
                    ...defaultClientAttributes,
                    product_id: product1.identifier,
                    groups: [`front:${region.isoCode}:${fc.code}`],
                    status: product1.status,
                    order: 100,
                    short_title_tanker_key: {
                        keyset: `product:shortNameLoc:${env}`,
                        key: skuId
                    },
                    long_title_tanker_key: {
                        keyset: `product:longName:${env}`,
                        key: skuId
                    },
                    description_tanker_key: {
                        keyset: `product:descriptionLoc:${env}`,
                        key: skuId
                    },
                    ingredients_tanker_key: {
                        keyset: `product:ingredientsLoc:${env}`,
                        key: skuId
                    },
                    localizationAttributes: [
                        {
                            key: skuId,
                            keyset: `product:attr_loc:${env}`,
                            name: 'attr_loc',
                            value: 'loc_foo'
                        },
                        {
                            key: 'countryISO.ABC',
                            keyset: `AttributeOptions${env.charAt(0).toUpperCase() + env.slice(1)}`,
                            name: 'countryISO',
                            value: 'ABC'
                        },
                        {
                            key: skuId,
                            keyset: `product:longName:${env}`,
                            name: 'longName',
                            value: 'loc_foo'
                        },
                        {
                            key: skuId,
                            keyset: `product:longNameLoc:${env}`,
                            name: 'longNameLoc',
                            value: 'loc_foo'
                        },
                        {
                            key: skuId,
                            keyset: `product:shortNameLoc:${env}`,
                            name: 'shortNameLoc',
                            value: 'loc_foo'
                        }
                    ],
                    amount: 1.2,
                    amount_unit: 'foo',
                    barcode: [],
                    country_iso: ['ABC']
                },
                logisticAttributes: {
                    tags: []
                }
            }
        ]);

        const data2 = await getActualProducts({limit: 1, lastCursor: data1.lastCursor});
        expect(data2.items).toMatchObject([
            {
                skuId: product2.identifier.toString(),
                status: product2.status
            }
        ]);
    });

    it('should return products after updating in "product"', async () => {
        const {product1, product2} = await createBase(user);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        const connection = await ensureConnection();

        await connection
            .createQueryBuilder()
            .update(Product)
            .set({
                status: ProductStatus.ACTIVE
            })
            .where({id: product1.id})
            .execute();

        const after = await getActualProducts({limit: 2, lastCursor: 0});
        expect(after.items[1].skuId).toBe(product1.identifier.toString());
    });

    it('should return products after updating in "product_attribute_value"', async () => {
        const {product1, role, product2, attribute, region} = await createBase(user);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) =>
                    attrs.map((attr) => (attr.attributeId === attribute.id ? {...attr, value: 'foobar'} : attr))
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString(),
            attributes: {
                attribute_for_testing: 'foobar'
            }
        });
    });

    it('should return products after inserting in "product_attribute_value"', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                code: 'some_new_attribute',
                type: AttributeType.TEXT
            }
        });
        const {product1, role, product2, region, im} = await createBase(user);

        await TestFactory.linkAttributesToInfoModel({userId: user.id, infoModelId: im.id, attributes: [attribute]});

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) => [
                    ...attrs,
                    {attributeId: attribute.id, value: 'new_value', isConfirmed: false}
                ]
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString()
        });
    });

    it('should return products after deleting in "product_attribute_value"', async () => {
        const {product1, product2, role, attribute, region} = await createBase(user);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) => attrs.filter(({attributeId}) => attributeId !== attribute.id)
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString()
        });
    });

    it('should return products after updating in "front_category_product"', async () => {
        const {product1, product2, role, region} = await createBase(user);
        const newFc = await createFrontCategory(user, region);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeFrontCategories: () => [newFc.id]
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString()
        });
    });

    it('should return products after inserting in "front_category_product"', async () => {
        const {product1, product2, role, region} = await createBase(user);
        const newFc = await createFrontCategory(user, region);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeFrontCategories: (ids) => [...ids, newFc.id]
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString()
        });
    });

    it('should return products after deleting in "front_category_product"', async () => {
        const {product1, product2, role, fc, region} = await createBase(user);

        const before = await getActualProducts({limit: 2, lastCursor: 0});
        expect(before.items[0].skuId).toBe(product1.identifier.toString());
        expect(before.items[1].skuId).toBe(product2.identifier.toString());

        await TestFactory.updateProductViaUi(product1, {
            user,
            role,
            region,
            productData: {
                changeFrontCategories: (ids) => ids.filter((id) => id !== fc.id)
            }
        });

        const after = await getActualProducts({limit: 100, lastCursor: 0});
        expect(after.items[1]).toMatchObject({
            skuId: product1.identifier.toString()
        });
    });

    it('should return actual products after reseting cursor', async () => {
        const {product1, product2} = await createBase(user);

        const data1 = await getActualProducts({limit: 100, lastCursor: 0});
        expect(data1.items).toHaveLength(2);
        expect(data1.items[0]).toMatchObject({skuId: product1.identifier.toString()});
        expect(data1.items[1]).toMatchObject({skuId: product2.identifier.toString()});

        const data2 = await getActualProducts({limit: 100, lastCursor: data1.lastCursor});
        expect(data2.items).toHaveLength(0);

        const connection = await ensureConnection();
        await connection.query(`
            UPDATE history_subject
            SET revision = DEFAULT
            WHERE id IN (SELECT history_subject_id FROM product);
        `);

        const data3 = await getActualProducts({limit: 100, lastCursor: data2.lastCursor});
        expect(data3.items).toHaveLength(2);
        expect(data3.items.map((it) => it.skuId).sort()).toEqual(
            [product1.identifier.toString(), product2.identifier.toString()].sort()
        );
    });

    it('should return image as string and images as string[]', async () => {
        const {product1} = await createBase(user);

        const attributeImage = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                code: 'image',
                type: AttributeType.IMAGE,
                isArray: true
            }
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product1.id,
            attributeId: attributeImage.id,
            value: ['image1', 'image2']
        });

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.images).toEqual(['image1', 'image2']);
        expect(product?.attributes?.image).toEqual('image1');
    });
});
