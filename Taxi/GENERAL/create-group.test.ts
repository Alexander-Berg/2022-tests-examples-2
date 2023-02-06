/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {createGroupHandler} from './create-group';

describe('create group', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should create group', async () => {
        const groupParams = {
            code: 'group',
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [langCodes[0]]: 'прилавок',
                [langCodes[1]]: 'group'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'прилавок',
                [langCodes[1]]: 'group'
            },
            meta: {foo: 'bar'},
            description: 'description',
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', links: []},
                {imageUrl: 'http://avatars/222', filename: '222.png', links: []}
            ]
        };

        const result = await createGroupHandler.handle({context, data: {body: groupParams}});
        const createdGroup = (await TestFactory.getGroups()).find(({id}) => id === result.id)!;

        expect(createdGroup).toBeTruthy();
        expect(result).toEqual({
            ...groupParams,
            id: createdGroup.id,
            legacyId: createdGroup.legacyId,
            region: {
                id: regions[0].id,
                isoCode: regions[0].isoCode
            },
            grids: [],
            categories: [],
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date)
        });
    });
});
