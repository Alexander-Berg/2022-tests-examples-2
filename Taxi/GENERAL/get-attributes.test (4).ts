import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributesHandler} from './get-attributes';

describe('get attributes', () => {
    let user: User;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createApiContext();
    });

    it('should return attributes [text, string, image, number, boolean]', async () => {
        const stringAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                nameTranslationMap: {
                    ru: 'name'
                },
                descriptionTranslationMap: {
                    ru: 'description'
                },
                isArray: true,
                isImmutable: true,
                isValueLocalizable: true,
                isValueRequired: true,
                properties: {maxArraySize: 2}
            }
        });

        const textAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT,
                isUnique: true
            }
        });

        const imageAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.IMAGE}
        });

        const numberAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER}
        });

        const booleanAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.BOOLEAN}
        });

        const attributes1 = await getAttributesHandler.handle({
            context,
            data: {
                query: {
                    limit: 3,
                    offset: 0
                }
            }
        });

        expect(attributes1.totalCount).toBe(5);
        expect(attributes1.list).toEqual([
            {
                code: stringAttr.code,
                type: 'string',
                name: {
                    ru: 'name'
                },
                description: {
                    ru: 'description'
                },
                isArray: true,
                isImmutable: true,
                isUnique: false,
                isValueLocalizable: true,
                isValueRequired: true,
                properties: {maxArraySize: 2},
                options: undefined
            },
            {
                code: textAttr.code,
                type: 'text',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: true,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: undefined
            },
            {
                code: imageAttr.code,
                type: 'image',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: false,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: undefined
            }
        ]);

        const attributes2 = await getAttributesHandler.handle({
            context,
            data: {
                query: {
                    limit: 3,
                    offset: 3
                }
            }
        });

        expect(attributes2.list).toEqual([
            {
                code: numberAttr.code,
                type: 'number',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: false,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: undefined
            },
            {
                code: booleanAttr.code,
                type: 'boolean',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: false,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: undefined
            }
        ]);
    });

    it('should return attributes [select, multiselect]', async () => {
        const selectAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.SELECT}
        });

        const multiselectAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.MULTISELECT}
        });

        const selectAttrOptions = await Promise.all(
            range(2).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: selectAttr.id,
                        sortOrder: i
                    }
                })
            )
        );

        const multiselectAttrOptions = await Promise.all(
            range(1).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: multiselectAttr.id,
                        sortOrder: i
                    }
                })
            )
        );

        const attributes = await getAttributesHandler.handle({
            context,
            data: {
                query: {
                    limit: 2,
                    offset: 0
                }
            }
        });

        expect(attributes.totalCount).toBe(2);
        expect(attributes.list).toEqual([
            {
                code: selectAttr.code,
                type: 'select',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: false,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: selectAttrOptions.map((it) => ({
                    code: it.code,
                    name: it.nameTranslationMap
                }))
            },
            {
                code: multiselectAttr.code,
                type: 'multiselect',
                name: {},
                description: {},
                isArray: false,
                isImmutable: false,
                isUnique: false,
                isValueLocalizable: false,
                isValueRequired: false,
                properties: {},
                options: multiselectAttrOptions.map((it) => ({
                    code: it.code,
                    name: it.nameTranslationMap
                }))
            }
        ]);
    });
});
