/* eslint-disable @typescript-eslint/no-explicit-any */
import {range} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {TankerCatalogExporter} from 'service/tanker-catalog-exporter';
import TankerProvider from 'service/tanker-provider';
import type {TranslationMap} from 'types/translation';

describe('tanker attribute options exporter', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should upload catalog entities translations', async () => {
        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });

        const frontCategories = await Promise.all([
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                parentId: parentFrontCategory.id,
                nameTranslationMap: {}
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                parentId: parentFrontCategory.id,
                nameTranslationMap: {ru: 'фронт категория'}
            })
        ]);

        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {},
                shortTitleTranslationMap: {}
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {ru: 'категория'},
                shortTitleTranslationMap: {en: 'category'}
            })
        ]);

        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {},
                shortTitleTranslationMap: {}
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {ru: 'группа'},
                shortTitleTranslationMap: {en: 'group'}
            })
        ]);

        const grids = await Promise.all([
            TestFactory.createGrid({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {},
                shortTitleTranslationMap: {}
            }),
            TestFactory.createGrid({
                userId: user.id,
                regionId: region.id,
                longTitleTranslationMap: {ru: 'сетка'},
                shortTitleTranslationMap: {en: 'grid'}
            })
        ]);

        let keyset: string = '';
        const keys: TranslationMap[] = [];

        jest.spyOn(TankerProvider.prototype as any, 'upsertKeyset').mockImplementation(async (params: any) => {
            keyset = params.keyset;
            params.keys.forEach((key: TranslationMap) => keys.push(key));
        });

        const tankerCatalogExporter = new TankerCatalogExporter();
        await tankerCatalogExporter.upsertCatalogTranslations();

        expect(keyset).toMatch(/^Catalog/);
        expect(keys).toHaveLength(7);
        expect(keys).toEqual(
            expect.arrayContaining([
                {
                    name: `subcategory:${region.isoCode}:${frontCategories[1].code}`,
                    translations: {ru: 'фронт категория', en: ''}
                },
                {
                    name: `category:${region.isoCode}:${categories[1].code}:long`,
                    translations: {ru: 'категория', en: ''}
                },
                {
                    name: `category:${region.isoCode}:${categories[1].code}:short`,
                    translations: {en: 'category'}
                },
                {
                    name: `group:${region.isoCode}:${groups[1].code}:long`,
                    translations: {ru: 'группа', en: ''}
                },
                {
                    name: `group:${region.isoCode}:${groups[1].code}:short`,
                    translations: {en: 'group'}
                },
                {
                    name: `grid:${region.isoCode}:${grids[1].code}:long`,
                    translations: {ru: 'сетка', en: ''}
                },
                {
                    name: `grid:${region.isoCode}:${grids[1].code}:short`,
                    translations: {en: 'grid'}
                }
            ])
        );
    });

    it('should read by chunks', async () => {
        await Promise.all(
            range(5).map(async (i) => {
                await TestFactory.createCategory({
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {en: `category ${i}`}
                });
            })
        );

        let execCount = 0;

        jest.spyOn(TankerProvider.prototype as any, 'upsertKeyset').mockImplementation(async () => {
            execCount++;
        });

        const tankerAttributeOptionsExporter = new TankerCatalogExporter();
        (tankerAttributeOptionsExporter as any).CHUNK_SIZE = 3;
        await tankerAttributeOptionsExporter.upsertCatalogTranslations();

        expect(execCount).toBe(2);
    });
});
