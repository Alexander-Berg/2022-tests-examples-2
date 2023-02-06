import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {config} from 'service/cfg';
import {FrontCategoryStatus} from 'types/front-category';
import {WeekDay} from 'types/time';

import {getSubcategories} from './index';

describe('get subcategories', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should return subcategories', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const products = await pMap(
            Array.from({length: 4}).map(() => ({
                userId: user.id,
                regionId: region.id,
                masterCategoryId: masterCategory.id
            })),
            TestFactory.createProduct,
            {concurrency: 1}
        );

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
                    parentId: parentFrontCategory.id,
                    productIds: [products[0].id, products[1].id]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id,
                    status: FrontCategoryStatus.DISABLED,
                    productIds: [products[2].id]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id,
                    productIds: [products[3].id],
                    timetable: {
                        dates: {begin: '01.01.2022', end: '31.12.2022'},
                        days: {[WeekDay.MONDAY]: {begin: '10:00', end: '18:00'}}
                    }
                }
            ],
            TestFactory.createFrontCategory,
            {concurrency: 1}
        );

        await expect(getSubcategories({lastCursor: 0, limit: 2})).resolves.toEqual({
            lastCursor: 2,
            items: [
                {
                    id: frontCategories[0].id,
                    titleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `subcategory:${region.isoCode}:${frontCategories[0].code}`
                    },
                    products: [{id: products[0].identifier}, {id: products[1].identifier}],
                    timetable: {dates: {}, days: []}
                },
                {
                    id: frontCategories[3].id,
                    titleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `subcategory:${region.isoCode}:${frontCategories[3].code}`
                    },
                    products: [{id: products[3].identifier}],
                    timetable: {
                        dates: {begin: '01.01.2022', end: '31.12.2022'},
                        days: [{type: WeekDay.MONDAY, begin: '10:00', end: '18:00'}]
                    }
                }
            ]
        });
    });
});
