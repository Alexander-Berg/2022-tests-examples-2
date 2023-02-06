/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {createCategoryHandler} from './create-category';

describe('create category', () => {
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

    it('should create category', async () => {
        const categoryParams = {
            code: 'category',
            status: CatalogStatus.ACTIVE,
            deeplink: 'deeplink',
            shortTitleTranslations: {
                [langCodes[0]]: 'категория',
                [langCodes[1]]: 'category'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'категория',
                [langCodes[1]]: 'category'
            },
            meta: {foo: 'bar'},
            description: 'description',
            specialCategory: 'special',
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', formats: [2], links: []},
                {imageUrl: 'http://avatars/222', filename: '222.png', formats: [2], links: []}
            ]
        };

        const result = await createCategoryHandler.handle({context, data: {body: categoryParams}});
        const createdCategory = (await TestFactory.getCategories()).find(({id}) => id === result.id)!;

        expect(createdCategory).toBeTruthy();
        expect(result).toEqual({
            ...categoryParams,
            id: createdCategory.id,
            legacyId: createdCategory.legacyId,
            region: {
                id: regions[0].id,
                isoCode: regions[0].isoCode
            },
            groups: [],
            frontCategories: [],
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
