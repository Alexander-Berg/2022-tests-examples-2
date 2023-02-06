import {random, range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {emptyArray, emptyObject} from '@/src/constants';
import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {UnknownAttributesError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {createAttributeGroupHandler} from './create-attribute-group';
import {formatAttributeGroupItem} from './utils/format-attribute-group';

describe('create attribute group', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attributeGroup: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    function createEmptyBody(code: string) {
        return {
            code,
            nameTranslations: emptyObject,
            descriptionTranslations: emptyObject,
            attributes: emptyArray
        };
    }

    it('should create group', async () => {
        const attributes = await Promise.all(
            range(4).map(async () => {
                const attribute = await TestFactory.createAttribute({
                    attribute: {
                        type: AttributeType.STRING,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    },
                    userId: user.id
                });

                return attribute;
            })
        );

        const attributeGroup = {
            code: 'testGroup',
            nameTranslations: {
                [langCodes[0]]: 'название',
                [langCodes[1]]: 'title'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'описание',
                [langCodes[1]]: 'description'
            },
            attributes: attributes.map(({id}) => id)
        };

        const result = await createAttributeGroupHandler.handle({context, data: {body: attributeGroup}});
        const createdAttributeGroup = await TestFactory.getAttributeGroupById(result.id);

        expect(result).toEqual({
            ...attributeGroup,
            id: createdAttributeGroup?.id,
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: expect.any(Date),
            attributes: attributes.map(formatAttributeGroupItem),
            sortOrder: 0
        });
    });

    it('sort order increases correctly', async () => {
        const firstGroup = await createAttributeGroupHandler.handle({
            context,
            data: {
                body: createEmptyBody('test1')
            }
        });
        const secondGroup = await createAttributeGroupHandler.handle({
            context,
            data: {
                body: createEmptyBody('test2')
            }
        });
        const thirdGroup = await createAttributeGroupHandler.handle({
            context,
            data: {
                body: createEmptyBody('test3')
            }
        });

        const orders = [firstGroup, secondGroup, thirdGroup].map(({sortOrder}) => sortOrder);

        expect(orders).toEqual([0, 1, 2]);
    });

    it('sort throw error if attribute group with the same code already exists', async () => {
        await createAttributeGroupHandler.handle({
            context,
            data: {
                body: createEmptyBody('test1')
            }
        });

        const secondGroupPromise = createAttributeGroupHandler.handle({
            context,
            data: {
                body: createEmptyBody('test1')
            }
        });

        await expect(secondGroupPromise.catch((err) => err.driverError.detail)).resolves.toBe(
            'Key (code)=(test1) already exists.'
        );
    });

    it('should throw error if attribute does not exist', async () => {
        const createPromise = createAttributeGroupHandler.handle({
            context,
            data: {body: {...createEmptyBody('test420'), attributes: [random(420)]}}
        });

        await expect(createPromise).rejects.toThrow(UnknownAttributesError);
    });
});
