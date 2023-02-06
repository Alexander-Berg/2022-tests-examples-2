/* eslint-disable @typescript-eslint/no-explicit-any */
import {range} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';

import {getInfoModelsApiHandler, GetInfoModelsBody} from './get-info-models';

interface ExecuteHandlerParams {
    body: GetInfoModelsBody;
    lang: string;
    region: string;
}

function executeHandler(params: ExecuteHandlerParams): Promise<any> {
    const {body, lang, region} = params;

    return new Promise((resolve, reject) => {
        getInfoModelsApiHandler(
            {
                body,
                localization: {
                    uiLang: lang
                },
                header: (name: string): string | undefined => {
                    if (name === REGION_HEADER) {
                        return region;
                    }

                    return;
                }
            } as any,
            {json: resolve} as any,
            reject
        );
    });
}

describe('get info models', () => {
    it('should return info models in correct region', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const lang = await TestFactory.createLang();

        const infoModels: InfoModel[] = [];

        // Целевые инфо модели
        infoModels[0] = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        infoModels[1] = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        // Инфо модели для шума
        infoModels[2] = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: otherRegion.id
        });
        infoModels[3] = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: otherRegion.id
        });

        // Добавляем обновлений инфо модели, чтобы проверить запрос с историей
        // Должен вернуться создатель сущности
        for (const i of range(8)) {
            await TestFactory.updateInfoModel(infoModels[0].id, {
                userId: (await TestFactory.createUser({} as any)).id,
                infoModel: {
                    titleTranslationMap: i % 2 === 0 ? {[lang.isoCode]: 'foo'} : {}
                }
            });
        }

        const {list, totalCount} = await executeHandler({
            body: {limit: 10, offset: 0},
            lang: lang.isoCode,
            region: region.isoCode
        });

        // Проверяем, что история работает
        const history = await TestFactory.getHistory();
        const infoModelHistory = history.filter((it) => it.tableName === DbTable.INFO_MODEL && it.action === 'U');

        expect(infoModelHistory).toHaveLength(8);

        expect(list).toEqual(
            infoModels
                .slice(0, 2)
                .reverse()
                .map((it) => ({
                    id: it.id,
                    createdAt: expect.any(Date),
                    code: it.code,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    titleTranslations: {},
                    descriptionTranslations: {},
                    averageFullness: 0,
                    filledProductsCount: 0,
                    notFilledProductsCount: 0,
                    fullness: 0,
                    productsCount: 0,
                    attributes: []
                }))
        );
        expect(totalCount).toBe(2);
    });

    it('should return info models with limit and offset', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const lang = await TestFactory.createLang();

        const infoModels: InfoModel[] = [];

        // Целевые инфо модели
        for (const i of range(12)) {
            infoModels[i] = await TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id
            });
        }

        // Инфо модели для шума
        await Promise.all(
            range(10).map(() =>
                TestFactory.createInfoModel({
                    userId: user.id,
                    regionId: otherRegion.id
                })
            )
        );

        const {list, totalCount} = await executeHandler({
            body: {limit: 2, offset: 4},
            lang: lang.isoCode,
            region: region.isoCode
        });

        expect(list).toEqual(
            infoModels
                .reverse()
                .slice(4, 6)
                .map((it) => ({
                    id: it.id,
                    createdAt: expect.any(Date),
                    code: it.code,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    titleTranslations: {},
                    descriptionTranslations: {},
                    averageFullness: 0,
                    filledProductsCount: 0,
                    notFilledProductsCount: 0,
                    fullness: 0,
                    productsCount: 0,
                    attributes: []
                }))
        );
        expect(totalCount).toBe(12);
    });

    it('should return info models after searching by code', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const lang = await TestFactory.createLang();

        const searchPattern = 'llApS';

        const infoModels: InfoModel[] = [];

        // Целевые инфо модели
        for (const i of range(9)) {
            infoModels[i] = await TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id,
                infoModel: {
                    code: `a${searchPattern}xcq${Math.random()}we`
                }
            });
        }

        // Инфо модели для шума
        await Promise.all(
            range(10).map(() =>
                TestFactory.createInfoModel({
                    userId: user.id,
                    regionId: region.id,
                    infoModel: {
                        code: Math.random().toString()
                    }
                })
            )
        );

        const {list, totalCount} = await executeHandler({
            body: {limit: 2, offset: 5, search: searchPattern},
            lang: lang.isoCode,
            region: region.isoCode
        });

        expect(list).toEqual(
            infoModels
                .reverse()
                .slice(5, 7)
                .map((it) => ({
                    id: it.id,
                    createdAt: expect.any(Date),
                    code: it.code,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    titleTranslations: {},
                    descriptionTranslations: {},
                    averageFullness: 0,
                    filledProductsCount: 0,
                    notFilledProductsCount: 0,
                    fullness: 0,
                    productsCount: 0,
                    attributes: []
                }))
        );
        expect(totalCount).toBe(9);
    });

    it('should return info models after searching by title and lang', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang(), TestFactory.createLang()]);
        const [otherLang, targetLang] = langs;
        await TestFactory.createLocale({regionId: region.id, langIds: [targetLang.id]});

        const searchPattern = 'zzPQa';
        const expectedValue = `zxca${searchPattern}nnzx`;

        const otherSearchPattern = 'foobar';
        const otherExpectedValue = `aaa${otherSearchPattern}zzz`;

        const infoModels: InfoModel[] = [];

        // Целевые инфо модели
        for (const i of range(13)) {
            infoModels[i] = await TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id,
                infoModel: {
                    titleTranslationMap: TestFactory.createTranslationMap({
                        langCodes: langs.map((it) => it.isoCode),
                        values: langs.map((lang) =>
                            lang.id === targetLang.id
                                ? expectedValue
                                : lang.id === otherLang.id
                                ? otherExpectedValue
                                : Math.random().toString()
                        )
                    })
                }
            });
        }

        // Инфо модели для шума
        await Promise.all(
            range(10).map(async () => {
                return TestFactory.createInfoModel({
                    userId: user.id,
                    regionId: region.id,
                    infoModel: {
                        titleTranslationMap: TestFactory.createTranslationMap({
                            langCodes: langs.map((it) => it.isoCode)
                        })
                    }
                });
            })
        );

        const {list, totalCount} = await executeHandler({
            body: {limit: 2, offset: 7, search: searchPattern},
            lang: targetLang.isoCode,
            region: region.isoCode
        });

        expect(list).toEqual(
            infoModels
                .reverse()
                .slice(7, 9)
                .map((it) => ({
                    id: it.id,
                    createdAt: expect.any(Date),
                    code: it.code,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    titleTranslations: it.titleTranslationMap,
                    descriptionTranslations: {},
                    averageFullness: 0,
                    filledProductsCount: 0,
                    notFilledProductsCount: 0,
                    fullness: 0,
                    productsCount: 0,
                    attributes: []
                }))
        );
        expect(totalCount).toBe(13);

        const emptyResponse = await executeHandler({
            body: {limit: 2, offset: 0, search: otherSearchPattern},
            lang: otherLang.isoCode,
            region: region.isoCode
        });

        expect(emptyResponse.list).toEqual([]);
        expect(emptyResponse.totalCount).toBe(0);
    });
});
