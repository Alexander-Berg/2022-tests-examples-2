import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributeGroupByIdHandler} from './get-attribute-group-by-id';
import {formatAttributeGroupItem} from './utils/format-attribute-group';

describe('get attribute group by id', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should return existing group', async () => {
        const attributes = await Promise.all(
            range(1).map(async () => {
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
            attributes: attributes.map(({id}) => id),
            nameTranslations: {},
            descriptionTranslations: {}
        };

        const {id: attributeGroupId} = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup});

        const createdAttributeGroup = await getAttributeGroupByIdHandler.handle({
            context,
            data: {params: {id: attributeGroupId}}
        });

        expect(createdAttributeGroup).toEqual({
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

    it('should throw not found if not exists', async () => {
        const createdAttributeGroupPromise = getAttributeGroupByIdHandler.handle({
            context,
            data: {params: {id: 0}}
        });

        await expect(createdAttributeGroupPromise).rejects.toThrow(EntityNotFoundError);
        await expect(createdAttributeGroupPromise.catch((err) => err.parameters)).resolves.toMatchObject({
            entity: 'AttributeGroup'
        });
    });
});
