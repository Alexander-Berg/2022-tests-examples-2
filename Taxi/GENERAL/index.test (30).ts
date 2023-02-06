import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {FrontCategory} from '@/src/entities/front-category/entity';
import {MasterCategory} from '@/src/entities/master-category/entity';
import type {User} from '@/src/entities/user/entity';
import {ensureConnection} from 'service/db';

import {getDeletedCategories} from './index';

describe('get deleted categories', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return deleted categories after cursor', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const before = await getDeletedCategories({limit: 100, lastCursor: 0});
        expect(before.items).toHaveLength(0);

        const connection = await ensureConnection();
        await connection.getRepository(MasterCategory).delete({
            id: mc.id
        });

        const after1 = await getDeletedCategories({limit: 100, lastCursor: 0});
        expect(after1.items).toEqual([`master:${region.isoCode}:${mc.code}`]);

        await connection.getRepository(FrontCategory).delete({
            id: fc.id
        });

        const after2 = await getDeletedCategories({limit: 100, lastCursor: after1.lastCursor});
        expect(after2.items).toEqual([`front:${region.isoCode}:${fc.code}`]);
    });

    it('should return deleted categories in order by revision', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id
        });

        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fc2 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const before = await getDeletedCategories({limit: 100, lastCursor: 0});
        expect(before.items).toHaveLength(0);

        const connection = await ensureConnection();

        await connection.getRepository(FrontCategory).delete({
            id: fc2.id
        });

        await connection.getRepository(MasterCategory).delete({
            id: mc.id
        });

        await connection.getRepository(FrontCategory).delete({
            id: fc1.id
        });

        const after = await getDeletedCategories({limit: 100, lastCursor: 0});
        expect(after.items).toEqual([
            `front:${region.isoCode}:${fc2.code}`,
            `master:${region.isoCode}:${mc.code}`,
            `front:${region.isoCode}:${fc1.code}`
        ]);
    });
});
