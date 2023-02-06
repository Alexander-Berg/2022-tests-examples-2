import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {executeInTransaction} from 'service/db';

import {countDependentProducts} from './count-dependent-products';

async function createMasterCategoryWithInfoModel(region: Region, user: User, parentId?: number) {
    const {id: infoModelId} = await TestFactory.createInfoModel({
        userId: user.id,
        regionId: region.id
    });

    return TestFactory.createMasterCategory({
        userId: user.id,
        infoModelId,
        regionId: region.id,
        parentId
    });
}

describe('count affected products', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should count own products', async () => {
        const masterCategory = await createMasterCategoryWithInfoModel(region, user);

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            executeInTransaction({source: 'ui', stamp: MOCKED_STAMP, authorId: user.id}, async (manager) =>
                countDependentProducts(manager, masterCategory)
            )
        ).resolves.toEqual(1);
    });

    it('should count products of children without info model and skip parent products', async () => {
        const rootMasterCategory = await createMasterCategoryWithInfoModel(region, user);

        const parentMasterCategories = await Promise.all([
            await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: rootMasterCategory.id
            }),
            await createMasterCategoryWithInfoModel(region, user, rootMasterCategory.id)
        ]);

        const masterCategories = await Promise.all([
            await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: parentMasterCategories[0].id
            }),
            await TestFactory.createMasterCategory({
                userId: user.id,
                regionId: region.id,
                parentId: parentMasterCategories[1].id
            }),
            await createMasterCategoryWithInfoModel(region, user, parentMasterCategories[0].id),
            await createMasterCategoryWithInfoModel(region, user, parentMasterCategories[1].id)
        ]);

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: rootMasterCategory.id,
            regionId: region.id
        });

        await Promise.all(
            masterCategories.map((masterCategory) =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: masterCategory.id,
                    regionId: region.id
                })
            )
        );

        // 2 зависимых продукта у корня категорий
        // 1 - собственный
        // 0 - у дочерней категории без инфо модели
        // 1 - у листовой категории без инфо модели
        await expect(
            executeInTransaction({source: 'ui', stamp: MOCKED_STAMP, authorId: user.id}, async (manager) =>
                countDependentProducts(manager, rootMasterCategory)
            )
        ).resolves.toEqual(2);

        // по 1 зависимому продукту у дочерних категорий с и без инфо моделей
        // 0 - собственных
        // 1 - у листовой категории без инфо модели
        await Promise.all(
            parentMasterCategories.map((masterCategory) =>
                expect(
                    executeInTransaction({source: 'ui', stamp: MOCKED_STAMP, authorId: user.id}, async (manager) =>
                        countDependentProducts(manager, masterCategory)
                    )
                ).resolves.toEqual(1)
            )
        );

        // по 1 зависимому продукту у листовых категорий
        // 1 - собственный
        await Promise.all(
            masterCategories.map((masterCategory) =>
                expect(
                    executeInTransaction({source: 'ui', stamp: MOCKED_STAMP, authorId: user.id}, async (manager) =>
                        countDependentProducts(manager, masterCategory)
                    )
                ).resolves.toEqual(1)
            )
        );
    });
});
