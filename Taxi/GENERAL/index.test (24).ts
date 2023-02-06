import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {config} from 'service/cfg';
import {CatalogStatus} from 'types/catalog/base';
import {FrontCategoryStatus} from 'types/front-category';

import {getCategories} from './index';

describe('get categories', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should return categories', async () => {
        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });
        const frontCategories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id,
                    status: FrontCategoryStatus.DISABLED
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id,
                    akeneoLegacy: true
                }
            ],
            TestFactory.createFrontCategory,
            {concurrency: 1}
        );
        const categories = await pMap(
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
                    specialCategory: 'special',
                    deeplink: 'deeplink',
                    meta: {foo: 'bar'}
                }
            ],
            TestFactory.createCategory,
            {concurrency: 1}
        );

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            frontCategoryId: frontCategories[0].id,
            categoryId: categories[0].id
        });
        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            frontCategoryId: frontCategories[1].id,
            categoryId: categories[0].id
        });
        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            frontCategoryId: frontCategories[2].id,
            categoryId: categories[0].id
        });

        await expect(getCategories({lastCursor: 0, limit: 2})).resolves.toEqual({
            lastCursor: 2,
            items: [
                {
                    id: categories[0].id,
                    legacyId: categories[0].legacyId,
                    alias: categories[0].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `category:${region.isoCode}:${categories[0].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `category:${region.isoCode}:${categories[0].code}:long`
                    },
                    meta: {},
                    subcategories: [
                        {id: frontCategories[0].id, alias: `front:${region.isoCode}:${frontCategories[0].code}`},
                        {id: frontCategories[2].id, alias: frontCategories[2].code}
                    ]
                },
                {
                    id: categories[2].id,
                    legacyId: categories[2].legacyId,
                    alias: categories[2].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `category:${region.isoCode}:${categories[2].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `category:${region.isoCode}:${categories[2].code}:long`
                    },
                    specialCategory: 'special',
                    deeplink: 'deeplink',
                    meta: {foo: 'bar'},
                    subcategories: []
                }
            ]
        });
    });
});
