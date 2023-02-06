import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {FrontCategory} from '@/src/entities/front-category/entity';
import {MasterCategory} from '@/src/entities/master-category/entity';
import type {User} from '@/src/entities/user/entity';
import {getResizedImageUrl} from '@/src/utils/get-resized-image-url';
import {ensureConnection} from 'service/db';
import {FrontCategoryStatus} from 'types/front-category';
import {ImageSize} from 'types/image';
import {MasterCategoryStatus} from 'types/master-category';

import {getActualCategories} from './index';

describe('get actual categories', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser();
    });

    it('should return actual categories after cursor', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            nameTranslationMap: {
                ru: 'name_1'
            },
            descriptionTranslationMap: {
                ru: 'description'
            }
        });

        const data1 = await getActualCategories({limit: 1, lastCursor: 0});
        expect(data1.items).toEqual([
            {
                type: 'master',
                code: `master:${region.isoCode}:${mcRoot.code}`,
                parentCode: null,
                name: {
                    ru_RU: 'name'
                },
                status: mcRoot.status,
                description: {},
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            }
        ]);

        const data2 = await getActualCategories({limit: 1, lastCursor: data1.lastCursor});
        expect(data2.items).toEqual([
            {
                type: 'master',
                code: `master:${region.isoCode}:${mc.code}`,
                parentCode: `master:${region.isoCode}:${mcRoot.code}`,
                name: {
                    ru_RU: 'name_1'
                },
                status: mc.status,
                description: {
                    ru_RU: 'description'
                },
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            }
        ]);
    });

    it('should return master and front categories', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                ru: 'name'
            },
            descriptionTranslationMap: {
                ru: 'description'
            }
        });

        const data = await getActualCategories({limit: 2, lastCursor: 0});
        expect(data.items).toEqual([
            {
                type: 'master',
                code: `master:${region.isoCode}:${mc.code}`,
                parentCode: null,
                name: {
                    ru_RU: 'name'
                },
                status: mc.status,
                description: {},
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            },
            {
                type: 'front',
                code: `front:${region.isoCode}:${fc.code}`,
                parentCode: null,
                name: {
                    ru_RU: 'name'
                },
                status: mc.status,
                description: {
                    ru_RU: 'description'
                },
                deeplinkId: fc.deeplink,
                images: [getResizedImageUrl(fc.imageUrl, ImageSize.ORIGINAL)],
                legalRestrictions: [fc.legalRestrictions],
                order: null,
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            }
        ]);
    });

    it('should not return category if lang does not exist in locale', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            nameTranslationMap: {
                ru: 'name'
            },
            descriptionTranslationMap: {
                unknown: 'description'
            }
        });

        const data = await getActualCategories({limit: 1000, lastCursor: 0});
        expect(data.items).toEqual([
            {
                type: 'master',
                code: `master:${region.isoCode}:${mcRoot.code}`,
                parentCode: null,
                name: {
                    ru_RU: 'name'
                },
                status: mcRoot.status,
                description: {},
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            }
        ]);
    });

    it('should not return category if name is empty dictionary', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {}
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const data = await getActualCategories({limit: 1000, lastCursor: 0});
        expect(data.items).toEqual([
            {
                type: 'master',
                code: `master:${region.isoCode}:${mc.code}`,
                parentCode: `master:${region.isoCode}:${mcRoot.code}`,
                name: {
                    ru_RU: 'name'
                },
                status: mc.status,
                description: {},
                businessCluster: region.isoCode,
                created: expect.any(Number),
                updated: expect.any(Number)
            }
        ]);
    });

    it('should return categories after updating in "master_category"', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const before = await getActualCategories({limit: 2, lastCursor: 0});
        expect(before.items[0].code).toBe(`master:${region.isoCode}:${mcRoot.code}`);
        expect(before.items[1].code).toBe(`master:${region.isoCode}:${mc.code}`);

        const connection = await ensureConnection();

        await connection
            .createQueryBuilder()
            .update(MasterCategory)
            .set({
                status: MasterCategoryStatus.DISABLED
            })
            .where({id: mcRoot.id})
            .execute();

        const after = await getActualCategories({limit: 100, lastCursor: 0});
        expect(after.items[1].code).toBe(`master:${region.isoCode}:${mcRoot.code}`);
    });

    it('should return categories after updating in "front_category"', async () => {
        const region = await TestFactory.createRegion();

        const fcRoot = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fcRoot.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const before = await getActualCategories({limit: 2, lastCursor: 0});
        expect(before.items[0].code).toBe(`front:${region.isoCode}:${fcRoot.code}`);
        expect(before.items[1].code).toBe(`front:${region.isoCode}:${fc.code}`);

        const connection = await ensureConnection();

        await connection
            .createQueryBuilder()
            .update(FrontCategory)
            .set({
                status: FrontCategoryStatus.DISABLED
            })
            .where({id: fcRoot.id})
            .execute();

        const after = await getActualCategories({limit: 2, lastCursor: 0});
        expect(after.items[1].code).toBe(`front:${region.isoCode}:${fcRoot.code}`);
    });

    it('should return actual categories after reseting cursor', async () => {
        const region = await TestFactory.createRegion();
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const data1 = await getActualCategories({limit: 100, lastCursor: 0});
        expect(data1.items).toHaveLength(2);
        expect(data1.items[0]).toMatchObject({code: `master:${region.isoCode}:${mc.code}`});
        expect(data1.items[1]).toMatchObject({code: `front:${region.isoCode}:${fc.code}`});

        const data2 = await getActualCategories({limit: 100, lastCursor: data1.lastCursor});
        expect(data2.items).toHaveLength(0);

        const connection = await ensureConnection();
        await connection.query(`
            UPDATE history_subject
            SET revision = DEFAULT
            WHERE id IN (SELECT history_subject_id FROM master_category);
        `);

        const data3 = await getActualCategories({limit: 100, lastCursor: data2.lastCursor});
        expect(data3.items).toHaveLength(1);
        expect(data3.items[0]).toMatchObject({code: `master:${region.isoCode}:${mc.code}`});

        await connection.query(`
            UPDATE history_subject
            SET revision = DEFAULT
            WHERE id IN (SELECT history_subject_id FROM front_category);
        `);

        const data4 = await getActualCategories({limit: 100, lastCursor: data3.lastCursor});
        expect(data4.items).toHaveLength(1);
        expect(data4.items[0]).toMatchObject({code: `front:${region.isoCode}:${fc.code}`});
    });

    it('should return master category code as is if akeneo legacy and RU', async () => {
        const region = await TestFactory.createRegion({code: 'RU'});
        const im = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: im.id,
            akeneoLegacy: true,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const data = await getActualCategories({limit: 2, lastCursor: 0});
        expect(data.items).toHaveLength(1);
        expect(data.items[0].code).toBe(mc.code);
    });

    it('should return front category code as is if akeneo legacy', async () => {
        const region = await TestFactory.createRegion();
        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            akeneoLegacy: true,
            nameTranslationMap: {
                ru: 'name'
            }
        });

        const data = await getActualCategories({limit: 2, lastCursor: 0});
        expect(data.items).toHaveLength(1);
        expect(data.items[0].code).toBe(fc.code);
    });
});
