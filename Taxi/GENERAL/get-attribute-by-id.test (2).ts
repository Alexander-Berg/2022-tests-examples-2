import {seed, uuid} from 'casual';
import {maxBy, minBy, random, range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {DbTable} from '@/src/entities/const';
import type {Lang} from '@/src/entities/lang/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributeByIdHandler} from './get-attribute-by-id';

seed(3);

describe('get attribute by id', () => {
    let user: User;
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        langs = await Promise.all(range(2).map(() => TestFactory.createLang()));
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user});
    });

    it('should return existing attribute', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const attributeOptions = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: attribute.id,
                        sortOrder: i,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    }
                })
            )
        );

        const updatedTicket = uuid;

        await TestFactory.updateAttribute(attribute.id, {
            userId: user.id,
            attribute: {ticket: updatedTicket}
        });

        const history = (await TestFactory.getHistory()).filter((it) => it.tableName === DbTable.ATTRIBUTE);
        const firstHistoryItem = minBy(history, ({createdAt}) => createdAt);
        const lastHistoryItem = maxBy(history, ({createdAt}) => createdAt);

        const foundAttribute = await getAttributeByIdHandler.handle({
            context,
            data: {
                params: {
                    id: attribute.id
                }
            }
        });

        expect(foundAttribute).toEqual({
            id: attribute.id,
            type: AttributeType.SELECT,
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: firstHistoryItem?.createdAt,
            updatedAt: lastHistoryItem?.createdAt,
            isArray: attribute.isArray,
            isClient: attribute.isClient,
            isImmutable: attribute.isImmutable,
            isValueLocalizable: attribute.isValueLocalizable,
            code: attribute.code,
            ticket: updatedTicket,
            nameTranslations: attribute.nameTranslationMap,
            descriptionTranslations: attribute.descriptionTranslationMap,
            properties: {
                options: attributeOptions.map(({code, nameTranslationMap, id}) => ({
                    canDelete: true,
                    code,
                    id,
                    translations: nameTranslationMap
                }))
            },
            usedInProducts: false,
            attributeGroupId: null,
            attributeGroupSortOrder: null
        });
    });

    it('should throw error if attribute does not exist', async () => {
        let error = null;
        const unknownId = random(999999);

        try {
            await getAttributeByIdHandler.handle({
                context,
                data: {
                    params: {
                        id: unknownId
                    }
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Attribute'});
    });
});
