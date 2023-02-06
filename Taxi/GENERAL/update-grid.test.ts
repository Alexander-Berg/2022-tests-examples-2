/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {UpdatedGrid} from 'types/catalog/grid';

import {updateGridHandler} from './update-grid';

describe('update grid', () => {
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

    it('should update gird itself', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED,
            shortTitleTranslationMap: {
                [langCodes[0]]: 'сетка'
            },
            longTitleTranslationMap: {
                [langCodes[0]]: 'ceтк',
                [langCodes[1]]: 'gri'
            }
        });

        const updateParams: UpdatedGrid = {
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [langCodes[1]]: 'grid'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'сетка',
                [langCodes[1]]: 'grid'
            },
            meta: {foo: 'bar'},
            description: 'description'
        };

        await updateGridHandler.handle({context, data: {params: {id: grid.id}, body: updateParams}});
        const updatedGrid = (await TestFactory.getGrids()).find(({id}) => id === grid.id)!;

        expect(updatedGrid).toEqual({
            ...grid,
            status: updateParams.status,
            shortTitleTranslationMap: updateParams.shortTitleTranslations,
            longTitleTranslationMap: updateParams.longTitleTranslations,
            meta: updateParams.meta,
            description: updateParams.description
        });
    });

    it('should update linked groups', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: regions[0].id
        });

        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/0/111', filename: '0_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/0/222', filename: '0_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/1/111', filename: '1_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/1/222', filename: '1_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/2/111', filename: '2_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/2/222', filename: '2_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/3/111', filename: '3_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/3/222', filename: '3_222.png', width: 2, height: 2}
                ]
            })
        ]);

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: groups[0].id,
            images: [{imageUrl: 'http://avatars/0/111', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: groups[1].id,
            images: [
                {imageUrl: 'http://avatars/1/111', width: 2, height: 2},
                {imageUrl: 'http://avatars/1/222', width: 2, height: 2}
            ],
            meta: {foo: 'bar'}
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: groups[2].id,
            images: [{imageUrl: 'http://avatars/2/222', width: 2, height: 2}]
        });

        const updateParams: UpdatedGrid = {
            groups: [
                {
                    id: groups[1].id,
                    linkImage: {imageUrl: 'http://avatars/1/111', filename: '1_111.png'},
                    linkMeta: {foo: 'bar100500'}
                },
                {
                    id: groups[3].id,
                    linkImage: {imageUrl: 'http://avatars/3/222', filename: '3_222.png'},
                    linkMeta: {}
                },
                {
                    id: groups[2].id,
                    linkImage: {imageUrl: 'http://avatars/2/222', filename: '2_222.png'},
                    linkMeta: {}
                }
            ]
        };

        await updateGridHandler.handle({context, data: {params: {id: grid.id}, body: updateParams}});
        const gridGroups = await TestFactory.getGridGroups(grid.id);

        expect(gridGroups).toEqual([
            expect.objectContaining({
                groupId: groups[1].id,
                meta: {foo: 'bar100500'},
                groupImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/1/111',
                        filename: '1_111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                groupId: groups[3].id,
                meta: {},
                groupImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/3/222',
                        filename: '3_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                groupId: groups[2].id,
                meta: {},
                groupImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/2/222',
                        filename: '2_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);
    });

    it('should not link group from another region', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: regions[0].id
        });

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[1].id
        });

        const updateParams: UpdatedGrid = {groups: [{id: group.id, linkMeta: {}}]};

        await expect(
            updateGridHandler.handle({context, data: {params: {id: grid.id}, body: updateParams}})
        ).rejects.toThrow('FALSY check_grid_group_region');
    });

    it('should not link foreign category images', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: regions[0].id
        });

        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [{imageUrl: 'http://avatars/0/111', filename: '0_111.png', width: 2, height: 2}]
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id,
                images: [{imageUrl: 'http://avatars/1/111', filename: '1_111.png', width: 2, height: 2}]
            })
        ]);

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: groups[0].id,
            images: [{imageUrl: 'http://avatars/0/111', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: groups[1].id,
            images: [{imageUrl: 'http://avatars/1/111', width: 2, height: 2}]
        });

        const updateParams: UpdatedGrid = {
            groups: [
                {
                    id: groups[0].id,
                    linkMeta: {},
                    linkImage: {imageUrl: 'http://avatars/1/111', filename: '1_111.png'}
                },
                {
                    id: groups[1].id,
                    linkMeta: {},
                    linkImage: {imageUrl: 'http://avatars/0/111', filename: '0_111.png'}
                }
            ]
        };

        await expect(
            updateGridHandler.handle({context, data: {params: {id: grid.id}, body: updateParams}})
        ).rejects.toThrow(EntityNotFoundError);
    });
});
