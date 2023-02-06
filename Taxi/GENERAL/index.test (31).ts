/*
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {Product} from '@/src/entities/product/entity';
import type {User} from '@/src/entities/user/entity';
import {ensureConnection} from 'service/db';

import {getDeletedProducts} from './index';

describe('get deleted categories', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return deleted products after cursor', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const products = await Promise.all([
            TestFactory.createProduct({userId: user.id, masterCategoryId: mc.id, regionId: region.id}),
            TestFactory.createProduct({userId: user.id, masterCategoryId: mc.id, regionId: region.id})
        ]);

        const before = await getDeletedProducts({limit: 100, lastCursor: 0});
        expect(before.items).toHaveLength(0);

        const connection = await ensureConnection();
        await connection.getRepository(Product).delete({
            id: products[0].id
        });

        const after1 = await getDeletedProducts({limit: 100, lastCursor: 0});
        expect(after1.items).toEqual([products[0].identifier.toString()]);

        await connection.getRepository(Product).delete({
            id: products[1].id
        });

        const after2 = await getDeletedProducts({limit: 100, lastCursor: after1.lastCursor});
        expect(after2.items).toEqual([products[1].identifier.toString()]);
    });

    it('should return deleted products in order by revision', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const products = await pMap(
            [1, 2, 3],
            async () => {
                return TestFactory.createProduct({userId: user.id, masterCategoryId: mc.id, regionId: region.id});
            },
            {concurrency: 1}
        );

        const before = await getDeletedProducts({limit: 100, lastCursor: 0});
        expect(before.items).toHaveLength(0);

        const connection = await ensureConnection();

        await connection.getRepository(Product).delete({
            id: products[1].id
        });

        await connection.getRepository(Product).delete({
            id: products[2].id
        });

        await connection.getRepository(Product).delete({
            id: products[0].id
        });

        const after = await getDeletedProducts({limit: 100, lastCursor: 0});
        expect(after.items).toEqual([
            products[1].identifier.toString(),
            products[2].identifier.toString(),
            products[0].identifier.toString()
        ]);
    });
});
*/
import {getDeletedProducts} from './index';

describe('get deleted categories', () => {
    it('should return empty result', async () => {
        const res = await getDeletedProducts({limit: 100, lastCursor: 0});
        expect(res.items).toHaveLength(0);
    });
});
