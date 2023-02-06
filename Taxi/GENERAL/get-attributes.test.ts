/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {seed, uuid} from 'casual';
import {maxBy, minBy, range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributesHandler} from './get-attributes';

seed(3);

describe('get attributes', () => {
    let user: User;
    let region: Region;
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        langs = await Promise.all(range(2).map(() => TestFactory.createLang()));
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user, region});
        await TestFactory.createLocale({regionId: region.id, langIds: [langs[0].id]});
    });

    it('should return existing attributes', async () => {
        const attributes: Attribute[] = [];

        attributes[0] = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });
        attributes[1] = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const firstAttributeOptions = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: attributes[0].id,
                        sortOrder: i,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    }
                })
            )
        );

        const updatedTickets = attributes.map(() => uuid);

        await Promise.all(
            attributes.map(({id}, i) =>
                TestFactory.updateAttribute(id, {
                    userId: user.id,
                    attribute: {ticket: updatedTickets[i]}
                })
            )
        );

        const history = (await TestFactory.getHistory()).filter((it) => it.tableName === DbTable.ATTRIBUTE);
        const allHistory = attributes.map((attribute) => history.filter((it) => it.newRowMatchEntity(attribute)));

        const firstHistoryItems = allHistory.map((history) => minBy(history, ({createdAt}) => createdAt)!);
        const lastHistoryItems = allHistory.map((history) => maxBy(history, ({createdAt}) => createdAt)!);

        const {list, totalCount} = await getAttributesHandler.handle({
            context,
            data: {
                body: {
                    limit: 10,
                    offset: 0
                }
            }
        });

        expect(totalCount).toEqual(2);
        expect(list).toEqual([
            {
                id: attributes[1].id,
                type: AttributeType.NUMBER,
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last
                },
                createdAt: firstHistoryItems[1].createdAt,
                updatedAt: lastHistoryItems[1].createdAt,
                isArray: attributes[1].isArray,
                isValueLocalizable: attributes[1].isValueLocalizable,
                isImmutable: attributes[1].isImmutable,
                code: attributes[1].code,
                ticket: updatedTickets[1],
                nameTranslations: attributes[1].nameTranslationMap,
                descriptionTranslations: attributes[1].descriptionTranslationMap,
                usedInProducts: false,
                properties: {
                    isInteger: undefined,
                    isNonNegative: undefined,
                    min: undefined,
                    max: undefined,
                    maxArraySize: undefined
                },
                attributeGroupId: null,
                attributeGroupSortOrder: null,
                isConfirmable: false,
                hasConfirmedValues: false
            },
            {
                id: attributes[0].id,
                type: AttributeType.SELECT,
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last
                },
                createdAt: firstHistoryItems[0].createdAt,
                updatedAt: lastHistoryItems[0].createdAt,
                isArray: attributes[0].isArray,
                isValueLocalizable: attributes[0].isValueLocalizable,
                isImmutable: attributes[0].isImmutable,
                code: attributes[0].code,
                ticket: updatedTickets[0],
                nameTranslations: attributes[0].nameTranslationMap,
                descriptionTranslations: attributes[0].descriptionTranslationMap,
                usedInProducts: false,
                properties: {
                    options: firstAttributeOptions.map(({code, nameTranslationMap, id}) => ({
                        canDelete: true,
                        id,
                        code,
                        translations: nameTranslationMap
                    }))
                },
                attributeGroupId: null,
                attributeGroupSortOrder: null,
                isConfirmable: false,
                hasConfirmedValues: false
            }
        ]);
    });

    it('should paginate with limit and offset', async () => {
        const attributes = await Promise.all(
            range(3).map(() =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {
                        type: AttributeType.NUMBER,
                        isArray: false,
                        isValueLocalizable: false
                    }
                })
            )
        );

        const foundAttributes = await getAttributesHandler.handle({
            context,
            data: {
                body: {
                    limit: 1,
                    offset: 1
                }
            }
        });

        expect(foundAttributes.totalCount).toEqual(3);
        expect(foundAttributes.list).toEqual([
            {
                id: attributes[1].id,
                type: AttributeType.NUMBER,
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last
                },
                createdAt: expect.any(Date),
                updatedAt: expect.any(Date),
                isArray: attributes[1].isArray,
                isValueLocalizable: attributes[1].isValueLocalizable,
                isImmutable: attributes[1].isImmutable,
                code: attributes[1].code,
                ticket: attributes[1].ticket,
                nameTranslations: {},
                descriptionTranslations: {},
                usedInProducts: false,
                properties: {
                    isInteger: undefined,
                    isNonNegative: undefined,
                    min: undefined,
                    max: undefined,
                    maxArraySize: undefined
                },
                attributeGroupId: null,
                attributeGroupSortOrder: null,
                isConfirmable: false
            }
        ]);
    });

    it('should search by code', async () => {
        const attributes = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {
                        type: AttributeType.NUMBER,
                        code: i === 1 ? 'test_code' : undefined,
                        isArray: false,
                        isValueLocalizable: false,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    }
                })
            )
        );

        const foundAttributes = await getAttributesHandler.handle({
            context,
            data: {
                body: {
                    limit: 10,
                    offset: 0,
                    search: 'st_co'
                }
            }
        });

        expect(foundAttributes.totalCount).toEqual(1);
        expect(foundAttributes.list).toEqual([
            {
                id: attributes[1].id,
                type: AttributeType.NUMBER,
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last
                },
                createdAt: expect.any(Date),
                updatedAt: expect.any(Date),
                isArray: attributes[1].isArray,
                isValueLocalizable: attributes[1].isValueLocalizable,
                isImmutable: attributes[1].isImmutable,
                code: attributes[1].code,
                ticket: attributes[1].ticket,
                nameTranslations: attributes[1].nameTranslationMap,
                descriptionTranslations: {},
                usedInProducts: false,
                properties: {
                    isInteger: undefined,
                    isNonNegative: undefined,
                    min: undefined,
                    max: undefined,
                    maxArraySize: undefined
                },
                attributeGroupId: null,
                attributeGroupSortOrder: null,
                isConfirmable: false
            }
        ]);
    });

    it('should search by name translation with region lang', async () => {
        const attributes = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttribute({
                    userId: user.id,
                    attribute: {
                        type: AttributeType.NUMBER,
                        isArray: false,
                        isValueLocalizable: false,
                        nameTranslationMap: TestFactory.createTranslationMap({
                            langCodes,
                            values:
                                i === 1 ? ['имя атрибута на языке региона', 'another_lang_name_translation'] : undefined
                        })
                    }
                })
            )
        );

        let foundAttributes = await getAttributesHandler.handle({
            context,
            data: {
                body: {
                    limit: 10,
                    offset: 0,
                    search: 'имя атрибута на языке региона'
                }
            }
        });

        expect(foundAttributes.totalCount).toEqual(1);
        expect(foundAttributes.list).toEqual([
            {
                id: attributes[1].id,
                type: AttributeType.NUMBER,
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last
                },
                createdAt: expect.any(Date),
                updatedAt: expect.any(Date),
                isArray: attributes[1].isArray,
                isImmutable: attributes[1].isImmutable,
                isValueLocalizable: attributes[1].isValueLocalizable,
                code: attributes[1].code,
                ticket: attributes[1].ticket,
                nameTranslations: attributes[1].nameTranslationMap,
                descriptionTranslations: attributes[1].descriptionTranslationMap,
                usedInProducts: false,
                properties: {
                    isInteger: undefined,
                    isNonNegative: undefined,
                    min: undefined,
                    max: undefined,
                    maxArraySize: undefined
                },
                attributeGroupId: null,
                attributeGroupSortOrder: null,
                isConfirmable: false
            }
        ]);

        foundAttributes = await getAttributesHandler.handle({
            context,
            data: {
                body: {
                    limit: 10,
                    offset: 0,
                    search: 'another_lang_name_translation'
                }
            }
        });

        expect(foundAttributes.totalCount).toEqual(0);
        expect(foundAttributes.list).toEqual([]);
    });
});
