import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {User} from '@/src/entities/user/entity';
import moveArrayElementImmutable from '@/src/utils/move-array-element-immutable';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {moveMasterCategoryHandler} from './move-master-category';

describe('move master category (move inside same parent, aka sort)', () => {
    let user: User;
    let context: ApiRequestContext;

    const moveCategory = (masterCategoryId: number, parentCategoryId: number, index: number) =>
        moveMasterCategoryHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategoryId
                },
                body: {
                    parentId: parentCategoryId,
                    index
                }
            }
        });

    const createRootMasterCategory = async () => {
        const region = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        return parentMasterCategory;
    };

    const createChildMasterCategories = async (regionId: number, childrenCount: number, parentCategoryId: number) => {
        const children = await Promise.all(
            Array.from({length: childrenCount}, (_, i) =>
                TestFactory.createMasterCategory({
                    userId: user.id,
                    regionId,
                    parentId: parentCategoryId,
                    sortOrder: i
                })
            )
        );
        return children;
    };

    const createMasterCategoryWithChildren = async (childrenCount: number) => {
        const parentCategory = await createRootMasterCategory();
        await createChildMasterCategories(parentCategory.regionId, childrenCount, parentCategory.id);
        return parentCategory;
    };

    const getSortedChildMasterCategoriesIds = async (parentMasterCategory: MasterCategory) => {
        const childCategories = await TestFactory.getMasterCategories();
        return childCategories
            .filter(({parentId}) => parentId === parentMasterCategory.id)
            .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
            .map(({id}) => id);
    };

    const getSortedChildMasterCategoriesSortOrders = async (parentMasterCategory: MasterCategory) => {
        const childCategories = await TestFactory.getMasterCategories();
        return childCategories
            .filter(({parentId}) => parentId === parentMasterCategory.id)
            .map(({sortOrder}) => sortOrder)
            .sort((a, b) => (a ?? 0) - (b ?? 0));
    };

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {masterCategory: {canEdit: true}}});
        context = await TestFactory.createApiContext({user});
    });

    it('should sort child categories when moving inside same parent category', async () => {
        const parentMasterCategory = await createMasterCategoryWithChildren(5);
        const initialOrder = await getSortedChildMasterCategoriesIds(parentMasterCategory);
        await moveCategory(initialOrder[1], parentMasterCategory.id, 1);
        expect(await getSortedChildMasterCategoriesIds(parentMasterCategory)).toEqual(initialOrder);

        await moveCategory(initialOrder[1], parentMasterCategory.id, 3);
        expect(await getSortedChildMasterCategoriesIds(parentMasterCategory)).toEqual(
            moveArrayElementImmutable(initialOrder, 1, 3)
        );
    });

    it('should append category to the end of the child list if index is negative', async () => {
        const parentMasterCategory = await createMasterCategoryWithChildren(5);
        const initialOrder = await getSortedChildMasterCategoriesIds(parentMasterCategory);

        await moveCategory(initialOrder[3], parentMasterCategory.id, -100);
        expect(await getSortedChildMasterCategoriesIds(parentMasterCategory)).toEqual(
            moveArrayElementImmutable(initialOrder, 3, 100)
        );
    });

    it('should append category to the end of the child list if index exceed child list size', async () => {
        const parentMasterCategory = await createMasterCategoryWithChildren(5);
        const initialOrder = await getSortedChildMasterCategoriesIds(parentMasterCategory);

        await moveCategory(initialOrder[2], parentMasterCategory.id, 100);
        expect(await getSortedChildMasterCategoriesIds(parentMasterCategory)).toEqual(
            moveArrayElementImmutable(initialOrder, 2, 100)
        );
    });

    it('should sort child categories when moving to another parent category', async () => {
        const root = await createRootMasterCategory();
        const [sourceParentMasterCategory, targetParentMasterCategory] = await createChildMasterCategories(
            root.regionId,
            2,
            root.id
        );
        await createChildMasterCategories(sourceParentMasterCategory.regionId, 5, sourceParentMasterCategory.id);
        await createChildMasterCategories(sourceParentMasterCategory.regionId, 5, targetParentMasterCategory.id);

        const sourceParentMasterCategoryChildrenOrder = await getSortedChildMasterCategoriesIds(
            sourceParentMasterCategory
        );

        const targetParentMasterCategoryChildrenOrder = await getSortedChildMasterCategoriesIds(
            targetParentMasterCategory
        );

        const masterCategoryId = sourceParentMasterCategoryChildrenOrder[0];
        const index = 2;

        await moveCategory(masterCategoryId, targetParentMasterCategory.id, index);

        const expectedSource = sourceParentMasterCategoryChildrenOrder.filter((id) => id !== masterCategoryId);
        expect(await getSortedChildMasterCategoriesIds(sourceParentMasterCategory)).toEqual(expectedSource);
        const expectedSourceSortOrders = expectedSource.map((_, i) => i);
        expect(await getSortedChildMasterCategoriesSortOrders(sourceParentMasterCategory)).toEqual(
            expectedSourceSortOrders
        );

        const expectedTarget = targetParentMasterCategoryChildrenOrder
            .slice(0, index)
            .concat(masterCategoryId)
            .concat(targetParentMasterCategoryChildrenOrder.slice(index));

        expect(await getSortedChildMasterCategoriesIds(targetParentMasterCategory)).toEqual(expectedTarget);
        const expectedTargetSortOrders = expectedTarget.map((_, i) => i);
        expect(await getSortedChildMasterCategoriesSortOrders(targetParentMasterCategory)).toEqual(
            expectedTargetSortOrders
        );
    });
});
