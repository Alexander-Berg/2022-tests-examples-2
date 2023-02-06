/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {duplicateGridHandler} from './duplicate-grid';

describe('duplicate grid', () => {
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

    it('should duplicate grid', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: region.id,
            shortTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            longTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            meta: {foo: 'bar'},
            description: 'description'
        });

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: region.id,
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: group.id,
            meta: {foo: 'link meta'},
            images: [{imageUrl: 'http://avatars/111', width: 2, height: 2}]
        });

        const result = await duplicateGridHandler.handle({
            context,
            data: {
                params: {id: grid.id},
                body: {code: grid.code + '_duplicated'}
            }
        });
        const duplicatedGrid = (await TestFactory.getGrids()).find(({id}) => id === result.id)!;
        const duplicatedGridGroups = await TestFactory.getGridGroups(result.id);

        expect(duplicatedGrid).toBeTruthy();
        expect(duplicatedGrid).toEqual({
            ...grid,
            id: duplicatedGrid.id,
            legacyId: duplicatedGrid.legacyId,
            historySubjectId: duplicatedGrid.historySubjectId,
            code: grid.code + '_duplicated'
        });
        expect(duplicatedGridGroups).toEqual([
            expect.objectContaining({
                groupId: group.id,
                meta: {foo: 'link meta'},
                groupImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/111',
                        filename: '111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);
    });
});
