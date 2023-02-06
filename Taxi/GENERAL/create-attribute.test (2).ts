/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {DbTable} from '@/src/entities/const';
import type {Lang} from '@/src/entities/lang/entity';
import type {User} from '@/src/entities/user/entity';
import {AccessForbidden} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType, NewAttribute} from 'types/attribute';

import {createAttributeHandler} from './create-attribute';

describe('create attribute', () => {
    let user: User;
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attribute: {canEdit: true}}});
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);

        context = await TestFactory.createApiContext({lang: langs[0], user});
    });

    it('should create attribute with translations', async () => {
        const attribute: NewAttribute = {
            type: AttributeType.NUMBER,
            code: 'new_attribute',
            isArray: false,
            isClient: true,
            isImmutable: false,
            isValueLocalizable: false,
            nameTranslations: {
                [langCodes[0]]: 'некий атрибут',
                [langCodes[1]]: 'some attribute'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание атрибута',
                [langCodes[1]]: 'some attribute description'
            },
            ticket: 'https://st.yandex-team.ru/LAVKACONTENT-123',
            properties: {
                isInteger: true,
                isNonNegative: false,
                min: 0,
                max: 10,
                maxArraySize: undefined
            }
        };

        const createdAttribute = await createAttributeHandler.handle({
            context,
            data: {
                body: attribute
            }
        });

        const foundAttribute = (await TestFactory.getAttributes()).find(({code}) => code === attribute.code)!;
        const history = (await TestFactory.getHistory()).filter((it) => it.tableName === DbTable.ATTRIBUTE);
        const firstHistoryItem = history[0];

        expect(foundAttribute).toBeTruthy();
        expect(createdAttribute).toEqual({
            ...attribute,
            id: foundAttribute.id,
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: firstHistoryItem.createdAt,
            updatedAt: firstHistoryItem.createdAt,
            usedInProducts: false,
            attributeGroupId: null,
            attributeGroupSortOrder: null
        });
    });

    it('should create attribute with falsy "isClient" by default', async () => {
        const attribute: NewAttribute = {
            type: AttributeType.NUMBER,
            code: 'new_attribute',
            isArray: false,
            isValueLocalizable: false,
            nameTranslations: {},
            descriptionTranslations: {},
            ticket: 'https://st.yandex-team.ru/LAVKACONTENT-123',
            properties: {}
        };

        const createdAttribute = await createAttributeHandler.handle({
            context,
            data: {
                body: attribute
            }
        });

        const foundAttribute = (await TestFactory.getAttributes()).find(({code}) => code === attribute.code)!;
        const history = (await TestFactory.getHistory()).filter((it) => it.tableName === DbTable.ATTRIBUTE);
        const firstHistoryItem = history[0];

        expect(foundAttribute).toBeTruthy();
        expect(createdAttribute).toEqual({
            ...attribute,
            id: foundAttribute.id,
            isClient: false,
            isImmutable: false,
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: firstHistoryItem.createdAt,
            updatedAt: firstHistoryItem.createdAt,
            usedInProducts: false,
            attributeGroupId: null,
            attributeGroupSortOrder: null
        });
    });

    it('should create attribute with ordered options', async () => {
        const attribute: NewAttribute = {
            type: AttributeType.SELECT,
            code: 'new_attribute',
            isArray: false,
            isValueLocalizable: false,
            nameTranslations: {},
            descriptionTranslations: {},
            properties: {
                options: [
                    {
                        code: 'new_attribute_option_1',
                        translations: {
                            [langCodes[0]]: 'первая опция атрибута',
                            [langCodes[1]]: 'first attribute option'
                        }
                    },
                    {
                        code: 'new_attribute_option_2',
                        translations: {
                            [langCodes[0]]: 'вторая опция атрибута',
                            [langCodes[1]]: 'second attribute option'
                        }
                    }
                ]
            }
        };

        const createdAttribute = await createAttributeHandler.handle({
            context,
            data: {
                body: attribute
            }
        });

        const foundOptions = await TestFactory.getAttributeOptions(createdAttribute.id);

        expect(foundOptions.map(({code}) => code)).toEqual(attribute.properties.options.map(({code}) => code));

        const optionsTranslations = foundOptions.map(({nameTranslationMap}) => nameTranslationMap);

        expect(optionsTranslations).toEqual(attribute.properties.options.map(({translations}) => translations));
    });

    it('should create history', async () => {
        const attribute: NewAttribute = {
            type: AttributeType.SELECT,
            code: 'new_attribute',
            isArray: false,
            isValueLocalizable: false,
            nameTranslations: {},
            descriptionTranslations: {},
            properties: {
                options: [
                    {
                        code: 'new_attribute_option',
                        translations: {}
                    }
                ]
            }
        };

        await createAttributeHandler.handle({
            context,
            data: {
                body: attribute
            }
        });

        const foundAttribute = (await TestFactory.getAttributes()).find(({code}) => code === attribute.code)!;
        const attributeHistory = (await TestFactory.getHistory()).filter((it) => it.tableName === DbTable.ATTRIBUTE);

        expect(attributeHistory).toHaveLength(1);
        expect(attributeHistory[0].action).toEqual('I');
        expect(attributeHistory[0].newRowMatchEntity(foundAttribute)).toBeTruthy();

        const foundOption = (await TestFactory.getAttributeOptions(foundAttribute.id))[0];
        const optionHistory = (await TestFactory.getHistory()).filter(
            (it) => it.tableName === DbTable.ATTRIBUTE_OPTION
        );

        expect(optionHistory).toHaveLength(1);
        expect(optionHistory[0].action).toEqual('I');
        expect(optionHistory[0].newRowMatchEntity(foundOption)).toBeTruthy();
    });

    it('should throw when user has not permission', async () => {
        const user = await TestFactory.createUser();
        const context = await TestFactory.createApiContext({lang: langs[0], user});

        const attribute: NewAttribute = {
            type: AttributeType.NUMBER,
            code: 'new_attribute',
            isArray: false,
            isClient: true,
            isImmutable: false,
            isValueLocalizable: false,
            nameTranslations: {
                [langCodes[0]]: 'некий атрибут',
                [langCodes[1]]: 'some attribute'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание атрибута',
                [langCodes[1]]: 'some attribute description'
            },
            ticket: 'https://st.yandex-team.ru/LAVKACONTENT-123',
            properties: {
                isInteger: true,
                isNonNegative: false,
                min: 0,
                max: 10,
                maxArraySize: undefined
            }
        };

        await expect(
            createAttributeHandler.handle({
                context,
                data: {
                    body: attribute
                }
            })
        ).rejects.toThrow(AccessForbidden);
    });
});
