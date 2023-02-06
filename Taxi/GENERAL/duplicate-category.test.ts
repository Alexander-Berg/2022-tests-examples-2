/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {duplicateCategoryHandler} from './duplicate-category';

describe('duplicate category', () => {
    let user: User;
    let region: Region;
    let lang: Lang;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang();
        context = await TestFactory.createApiContext({user, region, lang});
    });

    it('should duplicate category', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: region.id,
            shortTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            longTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            meta: {foo: 'bar'},
            description: 'description',
            specialCategory: 'special',
            deeplink: 'deeplink',
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });

        const frontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentFrontCategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategory.id
        });

        const result = await duplicateCategoryHandler.handle({
            context,
            data: {
                params: {id: category.id},
                body: {code: category.code + '_duplicated'}
            }
        });
        const duplicatedCategory = (await TestFactory.getCategories()).find(({id}) => id === result.id)!;
        const duplicatedCategoryImages = await TestFactory.getCategoryImages(result.id);
        const duplicatedCategoryFrontCategories = await TestFactory.getCategoryFrontCategories(result.id);

        expect(duplicatedCategory).toBeTruthy();
        expect(duplicatedCategory).toEqual({
            ...category,
            id: duplicatedCategory.id,
            legacyId: duplicatedCategory.legacyId,
            historySubjectId: duplicatedCategory.historySubjectId,
            code: category.code + '_duplicated'
        });
        expect(duplicatedCategoryImages).toEqual([
            expect.objectContaining({
                imageUrl: 'http://avatars/111',
                filename: '111.png',
                imageDimension: expect.objectContaining({width: 2, height: 2})
            })
        ]);
        expect(duplicatedCategoryFrontCategories).toEqual([
            expect.objectContaining({
                frontCategoryId: frontCategory.id
            })
        ]);
    });
});
