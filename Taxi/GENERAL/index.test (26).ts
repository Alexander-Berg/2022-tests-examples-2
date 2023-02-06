import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {config} from 'service/cfg';
import {CatalogStatus} from 'types/catalog/base';

import {getLayouts} from './index';

describe('get layouts', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should return layouts', async () => {
        const categories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [
                        {imageUrl: 'http://avatars/category/0/0', filename: '0.png', width: 2, height: 2},
                        {imageUrl: 'http://avatars/category/0/0', filename: '0.png', width: 3, height: 2},
                        {imageUrl: 'http://avatars/category/0/1', filename: '1.png', width: 2, height: 2}
                    ]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    images: [{imageUrl: 'http://avatars/category/1/0', filename: '0.png', width: 2, height: 2}]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [
                        {imageUrl: 'http://avatars/category/2/0', filename: '0.png', width: 2, height: 2},
                        {imageUrl: 'http://avatars/category/2/0', filename: '0.png', width: 3, height: 2}
                    ]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [{imageUrl: 'http://avatars/category/3/0', filename: '0.png', width: 3, height: 2}]
                }
            ],
            TestFactory.createCategory,
            {concurrency: 1}
        );
        const groups = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [
                        {imageUrl: 'http://avatars/group/0/0', filename: '0.png', width: 2, height: 2},
                        {imageUrl: 'http://avatars/group/0/1', filename: '1.png', width: 2, height: 2}
                    ]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    images: [{imageUrl: 'http://avatars/group/1/0', filename: '0.png', width: 2, height: 2}]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [{imageUrl: 'http://avatars/group/2/0', filename: '0.png', width: 2, height: 2}]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    images: [{imageUrl: 'http://avatars/group/3/0', filename: '0.png', width: 2, height: 2}]
                }
            ],
            TestFactory.createGroup,
            {concurrency: 1}
        );
        const grids = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    meta: {foo: 'bar'}
                }
            ],
            TestFactory.createGrid,
            {concurrency: 1}
        );

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            categoryId: categories[0].id,
            groupId: groups[0].id,
            images: [
                {imageUrl: 'http://avatars/category/0/0', width: 2, height: 2},
                {imageUrl: 'http://avatars/category/0/0', width: 3, height: 2}
            ],
            meta: {foo: 'group category meta'}
        });
        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            categoryId: categories[1].id,
            groupId: groups[0].id,
            images: [{imageUrl: 'http://avatars/category/1/0', width: 2, height: 2}]
        });
        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            categoryId: categories[2].id,
            groupId: groups[0].id
        });
        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            categoryId: categories[3].id,
            groupId: groups[0].id,
            images: [{imageUrl: 'http://avatars/category/3/0', width: 3, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            groupId: groups[0].id,
            gridId: grids[0].id,
            images: [{imageUrl: 'http://avatars/group/0/0', width: 2, height: 2}],
            meta: {foo: 'grid group meta'}
        });
        await TestFactory.linkGroupToGrid({
            userId: user.id,
            groupId: groups[1].id,
            gridId: grids[0].id,
            images: [{imageUrl: 'http://avatars/group/1/0', width: 2, height: 2}]
        });
        await TestFactory.linkGroupToGrid({
            userId: user.id,
            groupId: groups[2].id,
            gridId: grids[0].id
        });
        await TestFactory.linkGroupToGrid({
            userId: user.id,
            groupId: groups[3].id,
            gridId: grids[0].id,
            images: [{imageUrl: 'http://avatars/group/3/0', width: 2, height: 2}]
        });

        await expect(getLayouts({lastCursor: 0, limit: 2})).resolves.toEqual({
            lastCursor: 2,
            items: [
                {
                    id: grids[0].id,
                    legacyId: grids[0].legacyId,
                    alias: grids[0].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `grid:${region.isoCode}:${grids[0].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `grid:${region.isoCode}:${grids[0].code}:long`
                    },
                    meta: {},
                    groups: [
                        {
                            id: groups[0].id,
                            layoutMeta: {foo: 'grid group meta'},
                            imageUrlTemplate: 'http://avatars/group/0/0',
                            dimensions: {width: 2, height: 2},
                            categories: [
                                {
                                    id: categories[0].id,
                                    layoutMeta: {foo: 'group category meta'},
                                    images: [
                                        {
                                            imageUrlTemplate: 'http://avatars/category/0/0',
                                            dimensions: {width: 2, height: 2}
                                        },
                                        {
                                            imageUrlTemplate: 'http://avatars/category/0/0',
                                            dimensions: {width: 3, height: 2}
                                        }
                                    ]
                                },
                                {
                                    id: categories[3].id,
                                    layoutMeta: {},
                                    images: [
                                        {
                                            imageUrlTemplate: 'http://avatars/category/3/0',
                                            dimensions: {width: 3, height: 2}
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            id: groups[3].id,
                            layoutMeta: {},
                            imageUrlTemplate: 'http://avatars/group/3/0',
                            dimensions: {width: 2, height: 2},
                            categories: []
                        }
                    ]
                },
                {
                    id: grids[2].id,
                    legacyId: grids[2].legacyId,
                    alias: grids[2].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `grid:${region.isoCode}:${grids[2].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `grid:${region.isoCode}:${grids[2].code}:long`
                    },
                    meta: {foo: 'bar'},
                    groups: []
                }
            ]
        });
    });
});
