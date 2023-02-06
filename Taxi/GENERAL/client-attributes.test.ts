import Ajv, {AnySchema} from 'ajv';
import ajvErrors from 'ajv-errors';
import fs from 'fs';
import jsYaml from 'js-yaml';
import {random} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Product} from '@/src/entities/product/entity';
import type {User} from '@/src/entities/user/entity';
import {serviceResolve} from '@/src/lib/resolve';
import {env} from 'service/cfg';
import casual from 'service/seed-db/utils/localized-casual';
import {AttributeType} from 'types/attribute';

import {
    BOOLEAN_ATTRS_FOR_CLIENT_CUSTOM_TAGS,
    defaultClientAttributes,
    MULTISELECT_ATTRS_FOR_CLIENT_CUSTOM_TAGS
} from './client-attributes';
import {getActualProducts} from './index';
import {createBase} from './index.test';

async function createProductWithClientAttributes(user: User) {
    const {product1, lang, region, fc, im, mc} = await createBase(user);

    const attribute1 = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'client_attribute_1',
            isValueLocalizable: true,
            type: AttributeType.TEXT
        }
    });

    const attribute2 = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code: 'client_attribute_2',
            type: AttributeType.TEXT
        }
    });

    await TestFactory.createProductAttributeValue({
        userId: user.id,
        productId: product1.id,
        attributeId: attribute1.id,
        langId: lang.id,
        value: 'foo'
    });

    await TestFactory.createProductAttributeValue({
        userId: user.id,
        productId: product1.id,
        attributeId: attribute2.id,
        value: 'bar'
    });

    return {product1, region, fc, im, mc};
}

async function createMultiSelectAttributeWithValue(code: string, user: User, product: Product) {
    const attr = await TestFactory.createAttribute({
        userId: user.id,
        attribute: {
            code,
            type: AttributeType.MULTISELECT
        }
    });

    const value = casual.array_of_words(random(2, 5));

    await TestFactory.createProductAttributeValue({
        userId: user.id,
        productId: product.id,
        attributeId: attr.id,
        value
    });

    return {value};
}

describe('get actual products with "clientAttributes"', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return products with correct "clientAttributes"', async () => {
        const {product1} = await createBase(user);

        const booleanAttrs: string[] = [];

        for (const code of BOOLEAN_ATTRS_FOR_CLIENT_CUSTOM_TAGS) {
            const attr = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    code,
                    type: AttributeType.BOOLEAN
                }
            });

            const value = casual.boolean;

            if (value) {
                booleanAttrs.push(code);
            }

            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product1.id,
                attributeId: attr.id,
                value
            });
        }

        const {value: mainAllergens} = await createMultiSelectAttributeWithValue('mainAllergens', user, product1);
        const {value: photoStickers} = await createMultiSelectAttributeWithValue('photoStickers', user, product1);

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect((product?.clientAttributes.custom_tags as string[]).sort()).toEqual(booleanAttrs.sort());
        expect((product?.clientAttributes.main_allergens as string[]).sort()).toEqual(mainAllergens.sort());
        expect((product?.clientAttributes.photo_stickers as string[]).sort()).toEqual(photoStickers.sort());
    });

    it('should return empty "clientAttributes" in correct schema', async () => {
        const clientAttributesSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/client-attributes.yaml'), 'utf8')
        ) as AnySchema;
        const tankerNameSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/tanker-name.yaml'), 'utf8')
        ) as AnySchema;

        const ajv = new Ajv({
            allErrors: true
        });
        ajv.addKeyword('example');
        ajv.addSchema(tankerNameSchema, 'tanker-name.yaml');
        ajvErrors(ajv);

        const {product1} = await createBase(user);

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.clientAttributes.custom_tags).toBeUndefined();
        expect(product?.clientAttributes.main_allergens).toBeUndefined();
        expect(product?.clientAttributes.photo_stickers).toBeUndefined();

        await ajv.validate(clientAttributesSchema, product?.clientAttributes);
        expect(ajv.errors).toEqual(null);
    });

    it('should return "clientAttributes" in correct schema', async () => {
        const clientAttributesSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/client-attributes.yaml'), 'utf8')
        ) as AnySchema;
        const tankerNameSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/tanker-name.yaml'), 'utf8')
        ) as AnySchema;

        const ajv = new Ajv({
            allErrors: true
        });
        ajv.addKeyword('example');
        ajv.addSchema(tankerNameSchema, 'tanker-name.yaml');
        ajvErrors(ajv);

        const {product1} = await createBase(user);

        for (const code of BOOLEAN_ATTRS_FOR_CLIENT_CUSTOM_TAGS) {
            const attr = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    code,
                    type: AttributeType.BOOLEAN
                }
            });

            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product1.id,
                attributeId: attr.id,
                value: true
            });
        }

        await createMultiSelectAttributeWithValue('mainAllergens', user, product1);
        await createMultiSelectAttributeWithValue('photoStickers', user, product1);

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.clientAttributes.custom_tags?.length).toBeGreaterThan(0);
        expect(product?.clientAttributes.main_allergens?.length).toBeGreaterThan(0);
        expect(product?.clientAttributes.photo_stickers?.length).toBeGreaterThan(0);

        await ajv.validate(clientAttributesSchema, product?.clientAttributes);
        expect(ajv.errors).toEqual(null);
    });

    it('should add attribute in "clientAttributes" if it specified', async () => {
        const {product1, region, fc} = await createProductWithClientAttributes(user);
        const skuId = product1.identifier.toString();

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());
        product?.clientAttributes.localizationAttributes.sort((a, b) => (a?.name > b?.name ? 1 : -1));

        expect(product?.clientAttributes).toEqual({
            ...defaultClientAttributes,
            product_id: product1.identifier,
            groups: [`front:${region.isoCode}:${fc.code}`],
            status: product1.status,
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
                    key: skuId,
                    keyset: `product:client_attribute_1:${env}`,
                    name: 'client_attribute_1',
                    value: 'foo'
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
            country_iso: ['ABC']
        });

        expect(product?.attributes).toEqual({
            markCount: 1.2,
            attr_loc: {ru_RU: 'loc_foo'},
            longName: {ru_RU: 'loc_foo'},
            longNameLoc: {ru_RU: 'loc_foo'},
            shortNameLoc: {ru_RU: 'loc_foo'},
            markCountUnit: 'foo',
            attribute_for_testing: 'foo',
            client_attribute_1: {ru_RU: 'foo'},
            client_attribute_2: 'bar',
            countryISO: ['ABC'],
            image: undefined
        });
    });

    it('should add in custom tags multiselect attributes', async () => {
        const {product1} = await createBase(user);

        const tags: string[] = [];

        for (const code of MULTISELECT_ATTRS_FOR_CLIENT_CUSTOM_TAGS) {
            const {value} = await createMultiSelectAttributeWithValue(code, user, product1);

            tags.push(...value);
        }

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect((product?.clientAttributes.custom_tags as string[]).sort()).toEqual(tags.sort());
    });

    it('should add in custom tags only array', async () => {
        const {product1} = await createBase(user);

        for (const code of MULTISELECT_ATTRS_FOR_CLIENT_CUSTOM_TAGS) {
            const attr = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    code,
                    type: AttributeType.SELECT
                }
            });

            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product1.id,
                attributeId: attr.id,
                value: 'foobar'
            });
        }

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.clientAttributes.custom_tags).toBeUndefined();
    });

    it('should add in custom tags only string array', async () => {
        const {product1} = await createBase(user);

        for (const code of MULTISELECT_ATTRS_FOR_CLIENT_CUSTOM_TAGS) {
            const attr = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    code,
                    type: AttributeType.NUMBER,
                    isArray: true
                }
            });

            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product1.id,
                attributeId: attr.id,
                value: [1, 2, 3]
            });
        }

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.clientAttributes.custom_tags).toBeUndefined();
    });
});
