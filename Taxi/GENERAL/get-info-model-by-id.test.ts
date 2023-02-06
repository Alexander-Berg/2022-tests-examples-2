/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {random, range} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {DbTable} from '@/src/entities/const';
import {EntityNotFoundError} from '@/src/errors';
import {AttributeType} from '@/src/types/attribute';
import type {TranslationMap} from 'types/translation';

import {getInfoModelByIdApiHandler} from './get-info-model-by-id';

interface ExecuteHandlerParams {
    id: string;
    region: string;
}

function executeHandler({id, region}: ExecuteHandlerParams): Promise<any> {
    return new Promise((resolve, reject) => {
        getInfoModelByIdApiHandler(
            {
                params: {id},
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

describe('get info model by id', () => {
    it('should return info model', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        // Создаем атрибут
        const attributes = await Promise.all(
            range(5).map(async () => {
                const attribute = await TestFactory.createAttribute({
                    attribute: {
                        type: AttributeType.STRING,
                        nameTranslationMap: TestFactory.createTranslationMap({
                            langCodes: langs.map((it) => it.isoCode)
                        }),
                        descriptionTranslationMap: TestFactory.createTranslationMap({
                            langCodes: langs.map((it) => it.isoCode)
                        })
                    },
                    userId: user.id
                });

                return attribute;
            })
        );

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attributes[2].id,
                    isImportant: true
                },
                {
                    id: attributes[4].id,
                    isImportant: true
                }
            ]
        });

        let lastTitleTranslations: TranslationMap = {};

        // Добавляем изменения инфомодели, чтобы проверить что отдается корректный создатель сущности
        for (const _ of range(4)) {
            lastTitleTranslations = TestFactory.createTranslationMap({langCodes: langs.map((it) => it.isoCode)});

            await TestFactory.updateInfoModel(infoModel.id, {
                userId: (await TestFactory.createUser({} as any)).id,
                infoModel: {titleTranslationMap: lastTitleTranslations}
            });
        }

        // Проверяем, что история работает
        const history = await TestFactory.getHistory();
        const infoModelHistory = history.filter((it) => it.tableName === DbTable.INFO_MODEL && it.action === 'U');

        expect(infoModelHistory).toHaveLength(4);

        const result = await executeHandler({
            id: infoModel.id.toString(),
            region: region.isoCode
        });

        expect(result).toEqual({
            id: infoModel.id,
            code: infoModel.code,
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            titleTranslations: lastTitleTranslations,
            usedInMasterCategories: false,
            descriptionTranslations: infoModel.descriptionTranslationMap,
            createdAt: expect.any(Date),
            averageFullness: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            productsCount: 0,
            attributes: [
                {
                    id: attributes[2].id,
                    code: attributes[2].code,
                    nameTranslations: attributes[2].nameTranslationMap,
                    descriptionTranslations: attributes[2].descriptionTranslationMap,
                    type: attributes[2].type,
                    isArray: attributes[2].isArray,
                    isImportant: true,
                    attributeGroupSortOrder: null,
                    createdAt: expect.any(Date),
                    isConfirmable: false
                },
                {
                    id: attributes[4].id,
                    code: attributes[4].code,
                    nameTranslations: attributes[4].nameTranslationMap,
                    descriptionTranslations: attributes[4].descriptionTranslationMap,
                    type: attributes[4].type,
                    isArray: attributes[4].isArray,
                    isImportant: true,
                    attributeGroupSortOrder: null,
                    createdAt: expect.any(Date),
                    isConfirmable: false
                }
            ]
        });
    });

    it('should return error if info model from other region', async () => {
        let error = null;
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });

        try {
            await executeHandler({
                id: infoModel.id.toString(),
                region: otherRegion.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'InfoModel'});
    });

    it('should return error if info model does not exist', async () => {
        let error = null;
        const unknownId = random(999999).toString();
        const region = await TestFactory.createRegion();

        try {
            await executeHandler({
                id: unknownId,
                region: region.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'InfoModel'});
    });
});
