/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {duplicateGroupHandler} from './duplicate-group';

describe('duplicate group', () => {
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

    it('should duplicate group', async () => {
        const group = await TestFactory.createGroup({
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
            images: [{imageUrl: 'http://avatars/group/111', filename: '111.png', width: 2, height: 2}]
        });

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: region.id,
            images: [{imageUrl: 'http://avatars/category/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: category.id,
            meta: {foo: 'link meta'},
            images: [{imageUrl: 'http://avatars/category/111', width: 2, height: 2}]
        });

        const result = await duplicateGroupHandler.handle({
            context,
            data: {
                params: {id: group.id},
                body: {code: group.code + '_duplicated'}
            }
        });
        const duplicatedGroup = (await TestFactory.getGroups()).find(({id}) => id === result.id)!;
        const duplicatedGroupImages = await TestFactory.getGroupImages(result.id);
        const duplicatedGroupCategories = await TestFactory.getGroupCategories(result.id);

        expect(duplicatedGroup).toBeTruthy();
        expect(duplicatedGroup).toEqual({
            ...group,
            id: duplicatedGroup.id,
            legacyId: duplicatedGroup.legacyId,
            historySubjectId: duplicatedGroup.historySubjectId,
            code: group.code + '_duplicated'
        });
        expect(duplicatedGroupImages).toEqual([
            expect.objectContaining({
                imageUrl: 'http://avatars/group/111',
                filename: '111.png',
                imageDimension: expect.objectContaining({width: 2, height: 2})
            })
        ]);
        expect(duplicatedGroupCategories).toEqual([
            expect.objectContaining({
                categoryId: category.id,
                meta: {foo: 'link meta'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/category/111',
                        filename: '111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);
    });
});
