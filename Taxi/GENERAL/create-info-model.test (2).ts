/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {range} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {DbTable} from '@/src/entities/const';
import type {History} from '@/src/entities/history/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {InfoModelAttribute} from '@/src/entities/info-model-attribute/entity';
import type {Lang} from '@/src/entities/lang/entity';
import {toHstoreValue} from '@/src/service/hstore-type/to-hstore-value';
import {AttributeType} from '@/src/types/attribute';
import type {NewInfoModel} from '@/src/types/info-model';

import {createInfoModelApiHandler} from './create-info-model';

interface ExecuteHandlerParams {
    body: NewInfoModel;
    region: string;
    login: string;
}

function executeHandler(params: ExecuteHandlerParams): Promise<InfoModel> {
    const {body, login, region} = params;

    return new Promise((resolve, reject) => {
        createInfoModelApiHandler(
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
            } as any,
            {json: resolve} as any,
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

describe('create info model', () => {
    it('should create info model with translations', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const attributes = await Promise.all(
            range(4).map(async () => {
                const attribute = await TestFactory.createAttribute({
                    attribute: {
                        type: AttributeType.STRING,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes: langs.map((it) => it.isoCode)})
                    },
                    userId: user.id
                });

                return attribute;
            })
        );

        const titleTranslations = makeTranslations(langs);
        const descriptionTranslations = makeTranslations(langs);

        const result = await executeHandler({
            body: {
                code: 'some_code',
                titleTranslations,
                descriptionTranslations,
                attributes: {
                    custom: attributes.slice(0, 2).map(({id}, i) => ({
                        id,
                        isImportant: Boolean(i)
                    }))
                }
            },
            region: region.isoCode,
            login: user.login
        });

        expect(result).toEqual({
            id: expect.any(Number),
            code: 'some_code',
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            titleTranslations,
            descriptionTranslations,
            createdAt: expect.any(Date),
            averageFullness: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            productsCount: 0,
            attributes: attributes.slice(0, 2).map((attr, i) => ({
                id: attr.id,
                code: attr.code,
                nameTranslations: attr.nameTranslationMap,
                descriptionTranslations: {},
                type: attr.type,
                isImportant: Boolean(i),
                isArray: attr.isArray,
                attributeGroupSortOrder: null,
                createdAt: expect.any(Date)
            })),
            usedInMasterCategories: false
        });
    });

    it('should fixed updating in history', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const result = await executeHandler({
            body: {
                code: 'some_code',
                titleTranslations: {},
                descriptionTranslations: {},
                attributes: {
                    custom: [
                        {
                            id: attribute.id,
                            isImportant: true
                        }
                    ]
                }
            },
            region: region.isoCode,
            login: user.login
        });

        const history = await TestFactory.getHistory();
        const infoModelCreatedHistory = history.find((it) => it.tableName === DbTable.INFO_MODEL) as History<InfoModel>;
        const infoModelAttributeCreateHistory = history.find(
            (it) => it.tableName === DbTable.INFO_MODEL_ATTRIBUTE
        ) as History<InfoModelAttribute>;

        expect(infoModelCreatedHistory.newRow!.id).toBe(toHstoreValue(result.id));
        expect(infoModelCreatedHistory.source).toBe('ui');

        expect(infoModelAttributeCreateHistory.newRow!.attribute_id).toBe(toHstoreValue(attribute.id));
        expect(infoModelAttributeCreateHistory.source).toBe('ui');
    });

    it('should add required attribute firstly', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();

        await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueRequired: true},
            userId: user.id
        });
        await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueRequired: true},
            userId: user.id
        });

        const customAttributes = await Promise.all(
            range(4).map(async () => {
                return TestFactory.createAttribute({
                    attribute: {type: AttributeType.STRING},
                    userId: user.id
                });
            })
        );

        const result = await executeHandler({
            body: {
                code: 'some_code',
                titleTranslations: {},
                descriptionTranslations: {},
                attributes: {
                    custom: customAttributes.slice(0, 2).map(({id}, i) => ({
                        id,
                        isImportant: Boolean(i)
                    }))
                }
            },
            region: region.isoCode,
            login: user.login
        });

        expect(result).toEqual({
            id: expect.any(Number),
            code: 'some_code',
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            titleTranslations: {},
            descriptionTranslations: {},
            createdAt: expect.any(Date),
            averageFullness: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            productsCount: 0,
            attributes: [...customAttributes.slice(0, 2)].map((it, i) => ({
                id: it.id,
                code: it.code,
                nameTranslations: {},
                descriptionTranslations: {},
                type: it.type,
                isImportant: Boolean(i),
                isArray: it.isArray,
                attributeGroup: undefined,
                attributeGroupSortOrder: null,
                createdAt: expect.any(Date)
            })),
            usedInMasterCategories: false
        });

        const allInfoModelAttributes = await TestFactory.getInfoModelAttributes();
        const infoModelAttributes = allInfoModelAttributes.filter((it) => it.infoModelId === result.id);

        expect(infoModelAttributes.map((it) => it.attribute.isValueRequired)).toEqual([true, true, false, false]);
    });
});
