/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants/index';
import {getFrontCategoryById} from '@/src/entities/front-category/api/get-front-category-by-id';
import {FrontCategory} from '@/src/entities/front-category/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    ActiveCategoryWithDisabledParentIsForbidden,
    EmptyNameTranslationsIsForbidden,
    InactiveCategoryWithActiveChildrenIsForbidden,
    NotUniqueFrontCategoryDeeplink
} from '@/src/errors';
import {executeInTransaction} from 'service/db';
import {CategoryStatusUpdateStrategy} from 'types/category-status';
import {FrontCategoryStatus} from 'types/front-category';

import {updateFrontCategoryApiHandler, UpdateFrontCategoryBodyStruct} from './update-front-category';

interface ExecuteHandlerParams {
    body: UpdateFrontCategoryBodyStruct;
    region: string;
    login: string;
    frontCategoryId: number;
}

function executeHandler(params: ExecuteHandlerParams): Promise<void> {
    const {body, login, region, frontCategoryId} = params;

    return new Promise((resolve, reject) => {
        updateFrontCategoryApiHandler(
            {
                body,
                params: {id: frontCategoryId},
                auth: {
                    login
                },
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

async function createParent(user: User, region: Region) {
    return TestFactory.createFrontCategory({
        userId: user.id,
        code: 'some_parent',
        imageUrl: '',
        regionId: region.id,
        status: FrontCategoryStatus.ACTIVE,
        promo: false
    });
}

describe('update front category', () => {
    let user: User;
    let region: Region;
    let langs: [Lang, Lang];

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {frontCategory: {canEdit: true}}});
        region = await TestFactory.createRegion();
        langs = [await TestFactory.createLang({isoCode: 'fr'}), await TestFactory.createLang({isoCode: 'en'})];
        const langIds = langs.map(({id}) => id);
        await TestFactory.createLocale({regionId: region.id, langIds});
    });

    it('should update front category with translations', async () => {
        const id = await executeInTransaction(
            {authorId: user.id, stamp: MOCKED_STAMP, source: 'ui'},
            async (manager) => {
                const {
                    identifiers: [{id}]
                } = await manager.insert(FrontCategory, {
                    code: 'some code',
                    imageUrl: 'some image',
                    legalRestrictions: '18',
                    deeplink: 'somedeeplink',
                    regionId: region.id,
                    nameTranslationMap: {
                        [langs[0].isoCode]: 'name',
                        [langs[1].isoCode]: 'имя'
                    }
                });

                return id;
            }
        );

        await executeHandler({
            frontCategoryId: id,
            body: {
                imageUrl: 'new image url',
                deeplink: 'newdeeplink',
                legalRestrictions: '16',
                nameTranslations: {[langs[0].isoCode]: 'new name', [langs[1].isoCode]: 'новое имя'},
                descriptionTranslations: {[langs[0].isoCode]: 'description', [langs[1].isoCode]: 'описание'}
            },
            login: user.login,
            region: region.isoCode
        });

        const frontCategory = await getFrontCategoryById(id);

        expect(frontCategory!.frontCategory).toMatchObject({
            code: 'some code',
            deeplink: 'newdeeplink',
            legalRestrictions: '16',
            nameTranslationMap: {[langs[0].isoCode]: 'new name', [langs[1].isoCode]: 'новое имя'},
            descriptionTranslationMap: {[langs[0].isoCode]: 'description', [langs[1].isoCode]: 'описание'}
        });
    });

    it('should throw error if front category does not exist', async () => {
        const handlerPromise = executeHandler({
            frontCategoryId: 999,
            body: {
                imageUrl: 'new image url',
                deeplink: 'newdeeplink',
                legalRestrictions: '16',
                nameTranslations: {[langs[0].isoCode]: 'new name', [langs[1].isoCode]: 'новое имя'},
                descriptionTranslations: {[langs[0].isoCode]: 'description', [langs[1].isoCode]: 'описание'}
            },
            login: user.login,
            region: region.isoCode
        });

        await expect(handlerPromise).rejects.toThrow('Could not find any entity of type "FrontCategory" matching: 999');
    });

    it('should throw when parentId changes', async () => {
        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const child1 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: root.id,
            regionId: region.id,
            sortOrder: 0
        });
        const child2 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: root.id,
            regionId: region.id,
            sortOrder: 1
        });

        child1.parentId = child2.id;

        const promise = executeInTransaction({authorId: user.id, stamp: MOCKED_STAMP, source: 'ui'}, (manager) =>
            manager.save(FrontCategory, child1)
        );

        await expect(promise).rejects.toThrow('PARENT_CHANGING_IS_NOT_ALLOWED');
    });

    describe('changing status', () => {
        it('should throw when parent is being disabled with active children', async () => {
            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED
            });
            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE
            });
            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: root.id,
                body: {status: {value: FrontCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).rejects.toThrow("The category can't be active if it has inactive subcategorie");
        });

        it('should not throw when parent is being disabled with disabled children', async () => {
            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: root.id,
                body: {status: {value: FrontCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).resolves.toMatchObject({
                id: root.id,
                code: root.code,
                status: FrontCategoryStatus.DISABLED
            });
        });

        it('should throw when child changes to active with disabled parent', async () => {
            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED
            });

            const child = await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: child.id,
                body: {status: {value: FrontCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).rejects.toThrow(ActiveCategoryWithDisabledParentIsForbidden);
        });

        it('should not throw when child changes to active with active parent', async () => {
            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            const child = await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: child.id,
                body: {status: {value: FrontCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).resolves.toMatchObject({
                id: child.id,
                code: child.code,
                status: FrontCategoryStatus.ACTIVE
            });
        });

        it('should not throw when root changes to active', async () => {
            // const lang = await TestFactory.createLang();

            // await TestFactory.createLocale({regionId: region.id, langIds: [lang.id]});

            // const nameTranslationMap = await TestFactory.createTranslationMap({
            //     langCodes: [lang.isoCode],
            //     values: ['test']
            // });
            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: root.id,
                body: {status: {value: FrontCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).resolves.toMatchObject({
                id: root.id,
                code: root.code,
                status: FrontCategoryStatus.ACTIVE
            });
        });

        it('should throw when parent become disabled with active children', async () => {
            // const lang = await TestFactory.createLang();

            // await TestFactory.createLocale({regionId: region.id, langIds: [lang.id]});

            // const nameTranslationMap = await TestFactory.createTranslationMap({
            //     langCodes: [lang.isoCode],
            //     values: ['test']
            // });

            const root = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            await TestFactory.createFrontCategory({
                userId: user.id,
                parentId: root.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap: {
                    [langs[0].isoCode]: 'name',
                    [langs[1].isoCode]: 'имя'
                }
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: root.id,
                body: {status: {value: FrontCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).rejects.toThrow(InactiveCategoryWithActiveChildrenIsForbidden);
        });

        it('should throw when category become active, but name translations are not completely filled', async () => {
            const langCodes = langs.map(({isoCode}) => isoCode);

            const nameTranslationMap = await TestFactory.createTranslationMap({
                langCodes,
                values: ['test', ' ']
            });

            const category = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.DISABLED,
                nameTranslationMap
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: category.id,
                body: {status: {value: FrontCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
            });

            await expect(promise).rejects.toThrow(EmptyNameTranslationsIsForbidden);
        });
    });

    describe('changing name translations', () => {
        it('should throw when category is active, but name translations are not completely filled', async () => {
            const langCodes = langs.map(({isoCode}) => isoCode);

            const nameTranslationMap = await TestFactory.createTranslationMap({
                langCodes,
                values: ['test1', 'test2']
            });

            const category = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                status: FrontCategoryStatus.ACTIVE,
                nameTranslationMap
            });

            const promise = executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: category.id,
                body: {nameTranslations: {en: '   '}}
            });

            await expect(promise).rejects.toThrow(EmptyNameTranslationsIsForbidden);
        });
    });

    it('should update front category with unique deeplink in same parent', async () => {
        const deeplink = 'unique';
        const parent = await createParent(user, region);

        await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink: deeplink + '1',
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        const category = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_2',
            parentId: parent.id,
            deeplink: deeplink + '2',
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        const result = await executeHandler({
            region: region.isoCode,
            login: user.login,
            frontCategoryId: category.id,
            body: {deeplink: deeplink + '3'}
        });

        expect(result).toMatchObject({deeplink: deeplink + '3'});
    });

    it('should throw error if deeplink is not uniq in same parent', async () => {
        const deeplink = 'unique';
        const parent = await createParent(user, region);

        await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink,
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        const category = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_2',
            parentId: parent.id,
            deeplink: 'smthother',
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        const promise = executeHandler({
            region: region.isoCode,
            login: user.login,
            frontCategoryId: category.id,
            body: {deeplink}
        });

        await expect(promise).rejects.toThrow(NotUniqueFrontCategoryDeeplink);
    });

    it('should throw error if deeplink has wrong pattern', async () => {
        const parent = await createParent(user, region);

        const category = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink: 'smthother',
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        await pMap(
            ['фывфыв', 'asd zxc', 'as,d'],
            async (wrongValue) => {
                const promise = executeHandler({
                    region: region.isoCode,
                    login: user.login,
                    frontCategoryId: category.id,
                    body: {deeplink: wrongValue}
                });

                await expect(promise).rejects.toThrow('Incorrect data format passed: {messages}');
            },
            {concurrency: 1}
        );
    });

    it('should not set null on empty deeplink with undefined', async () => {
        const parent = await createParent(user, region);

        const category = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink: 'smthother',
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        expect(category.deeplink).toBe('smthother');

        const result = await executeHandler({
            region: region.isoCode,
            login: user.login,
            frontCategoryId: category.id,
            body: {deeplink: undefined}
        });

        expect(result).toMatchObject({deeplink: category.deeplink});
    });

    it('should set null on empty deeplink with empty string', async () => {
        const parent = await createParent(user, region);

        const category = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink: 'smthother',
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE,
            promo: false
        });

        expect(category.deeplink).toBe('smthother');

        const result = await executeHandler({
            region: region.isoCode,
            login: user.login,
            frontCategoryId: category.id,
            body: {deeplink: ''}
        });

        expect(result).toMatchObject({deeplink: null});
    });

    it('should handle recursive status activation', async () => {
        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: root.id,
            status: FrontCategoryStatus.DISABLED,
            nameTranslationMap: {
                [langs[0].isoCode]: 'name1',
                [langs[1].isoCode]: 'name2'
            }
        });

        const child10 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.DISABLED
        });

        const child11 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.DISABLED
        });

        const child12 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.DISABLED
        });

        await expect(
            executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: fc.id,
                body: {status: {value: FrontCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.RECURSIVE}}
            })
        ).resolves.not.toThrow();

        const updatedIds = [fc, child10, child11, child12].map(({id}) => id);
        const frontCategories = await TestFactory.getFrontCategories();

        expect(
            frontCategories
                .filter(({id}) => updatedIds.includes(id))
                .every(({status}) => status === FrontCategoryStatus.ACTIVE)
        ).toBeTruthy();
    });

    it('should handle recursive status deactivation', async () => {
        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE
        });

        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: root.id,
            status: FrontCategoryStatus.ACTIVE,
            nameTranslationMap: {
                [langs[0].isoCode]: 'name1',
                [langs[1].isoCode]: 'name2'
            }
        });

        const child10 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.ACTIVE
        });

        const child11 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.ACTIVE
        });

        const child12 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: fc.id,
            status: FrontCategoryStatus.DISABLED
        });

        await TestFactory.flushHistory();

        await expect(
            executeHandler({
                region: region.isoCode,
                login: user.login,
                frontCategoryId: fc.id,
                body: {status: {value: FrontCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.RECURSIVE}}
            })
        ).resolves.not.toThrow();

        const updatedIds = [fc, child10, child11].map(({id}) => id);
        const unchangedIds = [child12].map(({id}) => id);
        const allIds = [...updatedIds, ...unchangedIds];
        const frontCategories = await TestFactory.getFrontCategories();

        expect(
            frontCategories
                .filter(({id}) => allIds.includes(id))
                .every(({status}) => status === FrontCategoryStatus.DISABLED)
        ).toBeTruthy();

        const historyRecords = await TestFactory.dispatchHistory();
        expect(historyRecords).toHaveLength(updatedIds.length);
    });

    it('should update timetable', async () => {
        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parent = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: root.id,
            regionId: region.id
        });

        const child = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: parent.id,
            regionId: region.id,
            nameTranslationMap: {
                [langs[0].isoCode]: 'name',
                [langs[1].isoCode]: 'имя'
            },
            timetable: {
                dates: {},
                days: {monday: {begin: '09:00', end: '21:00'}}
            }
        });

        const promise = executeHandler({
            frontCategoryId: child.id,
            body: {
                nameTranslations: {[langs[0].isoCode]: 'name'},
                timetable: {
                    beginDate: '01.01.2022',
                    entries: [{days: ['monday'], begin: '08:00', end: '20:00'}]
                }
            },
            login: user.login,
            region: region.isoCode
        });

        await expect(promise).resolves.toMatchObject({
            timetable: {
                beginDate: '01.01.2022',
                entries: [{days: ['monday'], begin: '08:00', end: '20:00'}]
            }
        });
    });
});
