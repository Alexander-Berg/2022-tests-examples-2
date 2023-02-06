/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {FrontCategory} from '@/src/entities/front-category/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    ActiveCategoryWithDisabledParentIsForbidden,
    EmptyNameTranslationsIsForbidden,
    NotUniqueFrontCategoryDeeplink
} from '@/src/errors';
import {ensureConnection} from 'service/db';
import {FrontCategoryStatus} from 'types/front-category';

import {createFrontCategoryApiHandler, CreateFrontCategoryBodyStruct} from './create-front-category';

interface ExecuteHandlerParams {
    body: CreateFrontCategoryBodyStruct;
    region: string;
    login: string;
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

    return {user, root, region, children};
}

function executeHandler(params: ExecuteHandlerParams): Promise<void> {
    const {body, login, region} = params;

    return new Promise((resolve, reject) => {
        createFrontCategoryApiHandler(
            {
                body,
                auth: {
                    login
                },
                header: (name: string): string | undefined => {
                    if (name === REGION_HEADER) {
                        return region;
                    }

                    return;
                },
                id: MOCKED_STAMP
            } as never,
            {json: resolve} as never,
            reject
        );
    });
}

function makeTranslations(langs: Lang[]) {
    return langs.reduce(
        (acc, lang) => ({
            ...acc,
            [lang.isoCode]: Math.random().toString()
        }),
        {}
    );
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

describe('create front category', () => {
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

    it('should create front category with translations', async () => {
        const fcParent = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_parent',
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED,
            promo: false
        });

        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);
        const result = await executeHandler({
            body: {
                code: 'some_code',
                nameTranslations,
                descriptionTranslations,
                deeplink: 'some_deeplink',
                legalRestrictions: '18',
                parentId: fcParent.id,
                imageUrl: '',
                status: FrontCategoryStatus.DISABLED,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        expect(result).toMatchObject({
            id: expect.any(Number),
            code: 'some_code',
            deeplink: 'some_deeplink',
            region: {id: region.id, isoCode: region.isoCode},
            author: {login: user.login},
            nameTranslations,
            descriptionTranslations
        });
    });

    it('should throw error if region is not equal with parent', async () => {
        const otherRegion = await TestFactory.createRegion();

        const fcParent = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_parent',
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED,
            promo: false
        });

        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);

        let errorMessage: string | undefined;

        try {
            await executeHandler({
                body: {
                    code: 'some_code2',
                    nameTranslations,
                    descriptionTranslations,
                    parentId: fcParent.id,
                    imageUrl: '',
                    status: FrontCategoryStatus.DISABLED,
                    promo: false
                },
                region: otherRegion.isoCode,
                login: user.login
            });
        } catch (error) {
            errorMessage = error.message;
        }

        expect(errorMessage).toMatch('FALSY is_front_category_and_parent_in_same_region');
    });

    it('should set sortOrder to max+1', async () => {
        const fcParent = await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_parent',
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED,
            promo: false
        });

        const {manager} = await ensureConnection();

        for (let i = 0; i < 3; i++) {
            const nameTranslations = makeTranslations(langs);
            const descriptionTranslations = makeTranslations(langs);
            const code = `some_code_with_sortOrder_${i}`;
            const result = await executeHandler({
                body: {
                    code,
                    nameTranslations,
                    descriptionTranslations,
                    parentId: fcParent.id,
                    imageUrl: '',
                    status: FrontCategoryStatus.DISABLED,
                    promo: false
                },
                region: region.isoCode,
                login: user.login
            });

            await expect(result).toMatchObject({
                id: expect.any(Number),
                code,
                region: {id: region.id, isoCode: region.isoCode}
            });

            const addedFrontCategory = await manager.getRepository(FrontCategory).findOne({where: {code}});

            expect(addedFrontCategory!.sortOrder).toBe(i);
        }
    });

    it('should not create front category with invalid region and without parentId', async () => {
        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);
        const result = executeHandler({
            body: {
                code: 'some_code3',
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.DISABLED,
                promo: false
            },
            region: 'invalid region',
            login: user.login
        });

        await expect(result).rejects.toThrow('Region {region} not found');
    });

    it('should throw when creating a 3rd level', async () => {
        const {children, region, user} = await createAllEntities();

        // Levels: 0 -> 1 -> 2
        const lastPossibleLevel = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: children[0].id,
            regionId: region.id,
            sortOrder: 0
        });

        // Levels: 0 -> 1 -> 2 -> 3 crash!
        const promise = TestFactory.createFrontCategory({
            userId: user.id,
            parentId: lastPossibleLevel.id,
            regionId: region.id,
            sortOrder: 0
        });

        await expect(promise).rejects.toThrow('MAX_LEVEL_IS_3');
    });

    it('should form the correct tpath', async () => {
        const {children, root, region, user} = await createAllEntities();

        const lastPossibleLevel = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: children[0].id,
            regionId: region.id,
            sortOrder: 0
        });

        expect(root.tpath).toBe(root.id.toString());

        expect(children[0].tpath).toBe(`${root.id}.${children[0].id}`);
        expect(children[1].tpath).toBe(`${root.id}.${children[1].id}`);
        expect(children[2].tpath).toBe(`${root.id}.${children[2].id}`);

        expect(lastPossibleLevel.tpath).toBe(`${root.id}.${children[0].id}.${lastPossibleLevel.id}`);
    });

    it('should throw when creating active category inside disabled parent', async () => {
        const {user, region} = await createAllEntities();
        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED
        });

        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);
        const promise = executeHandler({
            body: {
                code: 'some_code',
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                parentId: root.id,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        await expect(promise).rejects.toThrow(ActiveCategoryWithDisabledParentIsForbidden);
    });

    it('should throw when creating active category with not completely filled translations', async () => {
        const promise = executeHandler({
            body: {
                code: 'some_code',
                nameTranslations: {en: 'test', fr: ''},
                descriptionTranslations: {},
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        await expect(promise).rejects.toThrow(EmptyNameTranslationsIsForbidden);
    });

    it('should create front category with unique deeplink in same parent', async () => {
        const deeplink = 'unique';
        const parent = await createParent(user, region);
        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);
        await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink,
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED,
            promo: false
        });

        const result = await executeHandler({
            body: {
                code: 'some_code_2',
                deeplink: deeplink + '1',
                parentId: parent.id,
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        expect(result).toMatchObject({
            deeplink: deeplink + '1'
        });
    });

    it('should throw error if deeplink is not uniq in same parent', async () => {
        const parent = await createParent(user, region);
        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);

        const deeplink = 'unique';

        await TestFactory.createFrontCategory({
            userId: user.id,
            code: 'some_code_1',
            parentId: parent.id,
            deeplink,
            imageUrl: '',
            regionId: region.id,
            status: FrontCategoryStatus.DISABLED,
            promo: false
        });

        const promise = executeHandler({
            body: {
                code: 'some_code_2',
                deeplink,
                parentId: parent.id,
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        await expect(promise).rejects.toThrow(NotUniqueFrontCategoryDeeplink);
    });

    it('should throw error if deeplink has wrong pattern', async () => {
        await pMap(
            ['фывфыв', 'asd zxc', 'as,d'],
            async (wrongValue) => {
                const result = executeHandler({
                    body: {
                        code: 'some_code_2',
                        deeplink: wrongValue,
                        nameTranslations: {},
                        descriptionTranslations: {},
                        imageUrl: '',
                        status: FrontCategoryStatus.ACTIVE,
                        promo: false
                    },
                    region: region.isoCode,
                    login: user.login
                });

                await expect(result).rejects.toThrow('Incorrect data format passed: {messages}');
            },
            {concurrency: 1}
        );
    });

    it('should set null on empty deeplink with undefined or empty string', async () => {
        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);

        const undefinedResult = await executeHandler({
            body: {
                code: 'some_code_1',
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        const emptyStringResult = await executeHandler({
            body: {
                code: 'some_code_2',
                deeplink: '',
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                status: FrontCategoryStatus.ACTIVE,
                promo: false
            },
            region: region.isoCode,
            login: user.login
        });

        expect(undefinedResult).toMatchObject({deeplink: null});
        expect(emptyStringResult).toMatchObject({deeplink: null});
    });

    it('should create front category with timetable', async () => {
        const {children, region, user} = await createAllEntities();
        const nameTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);

        const undefinedResult = await executeHandler({
            body: {
                code: 'some_code_1',
                status: FrontCategoryStatus.ACTIVE,
                nameTranslations,
                descriptionTranslations,
                imageUrl: '',
                promo: false,
                parentId: children[0].id,
                timetable: {
                    beginDate: '01.01.2022',
                    endDate: '31.12.2022',
                    entries: [
                        {
                            days: ['tuesday', 'monday'],
                            begin: '09:00',
                            end: '21:00'
                        },
                        {
                            days: ['wednesday'],
                            begin: '09:00',
                            end: '21:00'
                        }
                    ]
                }
            },
            region: region.isoCode,
            login: user.login
        });

        expect(undefinedResult).toMatchObject({deeplink: null});
    });
});
