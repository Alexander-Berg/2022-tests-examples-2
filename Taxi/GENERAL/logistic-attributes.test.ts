import Ajv, {AnySchema} from 'ajv';
import ajvErrors from 'ajv-errors';
import casual from 'casual';
import fs from 'fs';
import jsYaml from 'js-yaml';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {User} from '@/src/entities/user/entity';
import {serviceResolve} from '@/src/lib/resolve';
import {AttributeType} from 'types/attribute';

import {getActualProducts} from './index';
import {createBase} from './index.test';
import {BOOLEAN_ATTRS_FOR_LOGISTIC_TAGS} from './logistic-attributes';

describe('get actual products with "logisticAttributes"', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return products with correct "logisticAttributes"', async () => {
        const {product1} = await createBase(user);

        const booleanAttrs: string[] = [];

        for (const code of BOOLEAN_ATTRS_FOR_LOGISTIC_TAGS) {
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

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect((product?.logisticAttributes.tags as string[]).sort()).toEqual(booleanAttrs.sort());
    });

    it('should add "productRestrictions" attribute to logistic tags', async () => {
        const {product1} = await createBase(user);

        const attr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                code: 'productRestrictions',
                type: AttributeType.SELECT
            }
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product1.id,
            attributeId: attr.id,
            value: 'foobarqwe'
        });

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.logisticAttributes.tags as string[]).toEqual(['foobarqwe']);
    });

    it('should return empty "logisticAttributes" in correct schema', async () => {
        const logisticAttributesSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/logistic-attributes.yaml'), 'utf-8')
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

        expect(product?.logisticAttributes.tags).toHaveLength(0);

        await ajv.validate(logisticAttributesSchema, product?.logisticAttributes);
        expect(ajv.errors).toEqual(null);
    });

    it('should return "logisticAttributes" in correct schema', async () => {
        const logisticAttributesSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/logistic-attributes.yaml'), 'utf-8')
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

        for (const code of BOOLEAN_ATTRS_FOR_LOGISTIC_TAGS) {
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

        const {items: products} = await getActualProducts({limit: 2, lastCursor: 0});
        const product = products.find((it) => it.skuId === product1.identifier.toString());

        expect(product?.logisticAttributes.tags.length).toBeGreaterThan(0);

        await ajv.validate(logisticAttributesSchema, product?.logisticAttributes);
        expect(ajv.errors).toEqual(null);
    });
});
