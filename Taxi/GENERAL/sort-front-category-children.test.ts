import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {FrontCategory} from '@/src/entities/front-category/entity';
import {ensureConnection} from 'service/db';

import {sortFrontCategoryChildrenApiHandler} from './sort-front-category-children';

function executeHandler(login: string, parentId: number, region: string, children: number[]): Promise<void> {
    return new Promise((resolve, reject) => {
        sortFrontCategoryChildrenApiHandler(
            {
                body: {children},
                params: {id: parentId},
                auth: {login},
                id: MOCKED_STAMP,
                header: (name: string): string | undefined => {
                    if (name === REGION_HEADER) {
                        return region;
                    }

                    return;
                }
            } as never,
            {json: resolve} as never,
            reject
        );
    });
}

async function createAllEntities() {
    const user = await TestFactory.createUser({rules: {frontCategory: {canEdit: true}}});
    const region = await TestFactory.createRegion();

    const root = await TestFactory.createFrontCategory({
        userId: user.id,
        regionId: region.id
    });
    const children = [];

    for (let i = 0; i < 3; i++) {
        children.push(
            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                sortOrder: i
            })
        );
    }

    const ids = children.map((c) => c.id);
    return {user, root, children, ids, region};
}

describe('sort front categories', () => {
    it('should sort front categories', async () => {
        const {user, root, children, region, ids} = await createAllEntities();
        await executeHandler(user.login, root.id, region.isoCode, [ids[1], ids[2], ids[0]]);
        const {manager} = await ensureConnection();
        const childrenResult = await manager.find(FrontCategory, {
            where: {parentId: root.id},
            order: {sortOrder: 'ASC'}
        });

        expect(childrenResult).toMatchObject([
            {
                ...children[1],
                sortOrder: 0
            },
            {
                ...children[2],
                sortOrder: 1
            },
            {
                ...children[0],
                sortOrder: 2
            }
        ]);
    });

    it('should throw error when some children are missing', async () => {
        const {user, root, region, ids} = await createAllEntities();
        const childrenResult = executeHandler(user.login, root.id, region.isoCode, [ids[0], ids[1]]);

        await expect(childrenResult).rejects.toThrow('Incorrect data format passed');
    });

    it('should throw error when extra children provided', async () => {
        const {user, root, region, ids} = await createAllEntities();
        const EXTRA_CHILD = 999;
        const childrenResult = executeHandler(user.login, root.id, region.isoCode, [
            ids[0],
            ids[1],
            ids[2],
            EXTRA_CHILD
        ]);

        await expect(childrenResult).rejects.toThrow('Incorrect data format passed');
    });

    it('should throw error when duplicate children provided', async () => {
        const {user, root, region, ids} = await createAllEntities();
        const childrenResult = executeHandler(user.login, root.id, region.isoCode, [ids[0], ids[1], ids[1]]);

        await expect(childrenResult).rejects.toThrow('Non-unique values passed');
    });
});
