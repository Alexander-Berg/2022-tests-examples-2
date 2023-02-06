/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {EntityNotFoundError, NewRequiredAttributesForbidden, UnknownAttributesError} from '@/src/errors';
import {AttributeType} from '@/src/types/attribute';
import type {UpdateInfoModel} from 'types/info-model';

import {updateInfoModelApiHandler} from './update-info-model';

interface ExecuteHandlerParams {
    body: UpdateInfoModel;
    infoModelId: number;
    login: string;
    region: string;
}

function executeHandler(params: ExecuteHandlerParams): Promise<any> {
    const {body, login, region, infoModelId} = params;

    return new Promise((resolve, reject) => {
        updateInfoModelApiHandler(
            {
                body,
                params: {
                    id: infoModelId.toString()
                },
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
            } as any,
            {json: resolve} as any,
            reject
        );
    });
}

describe('update info model', () => {
    it('should add translations', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const [lang, otherLang] = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const result = await executeHandler({
            body: {
                titleTranslations: {
                    [lang.isoCode]: 'title',
                    [otherLang.isoCode]: 'title_other'
                },
                descriptionTranslations: {
                    [lang.isoCode]: 'description'
                },
                attributes: {custom: []}
            },
            login: user.login,
            region: region.isoCode,
            infoModelId: infoModel.id
        });

        expect(result).toEqual({
            id: infoModel.id,
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            code: infoModel.code,
            createdAt: expect.any(Date),
            titleTranslations: {
                [lang.isoCode]: 'title',
                [otherLang.isoCode]: 'title_other'
            },
            descriptionTranslations: {
                [lang.isoCode]: 'description'
            },
            averageFullness: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            productsCount: 0,
            attributes: [],
            usedInMasterCategories: false
        });
    });

    it('should update translations', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const [lang, otherLang] = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            infoModel: {
                titleTranslationMap: TestFactory.createTranslationMap({
                    langCodes: [lang.isoCode, otherLang.isoCode],
                    values: ['initial', 'initial']
                })
            }
        });

        const result = await executeHandler({
            body: {
                titleTranslations: {
                    [lang.isoCode]: 'title_other'
                },
                descriptionTranslations: {},
                attributes: {custom: []}
            },
            login: user.login,
            region: region.isoCode,
            infoModelId: infoModel.id
        });

        expect(result).toEqual({
            id: infoModel.id,
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            code: infoModel.code,
            createdAt: expect.any(Date),
            titleTranslations: {
                [lang.isoCode]: 'title_other',
                [otherLang.isoCode]: 'initial'
            },
            descriptionTranslations: {},
            averageFullness: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            productsCount: 0,
            attributes: [],
            usedInMasterCategories: false
        });
    });

    it('should return error if info model does not exist', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();

        let error = null;
        const unknownInfoModelId = random(10000, 99999);

        try {
            await executeHandler({
                body: {
                    titleTranslations: {},
                    descriptionTranslations: {},
                    attributes: {custom: []}
                },
                login: user.login,
                region: region.isoCode,
                infoModelId: unknownInfoModelId
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'InfoModel'});
    });

    it('should return error if attributes does not exist', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });

        let error = null;
        const unknownAttributeId = random(10000, 99999);

        try {
            await executeHandler({
                body: {
                    titleTranslations: {},
                    descriptionTranslations: {},
                    attributes: {
                        custom: [
                            {id: attribute.id, isImportant: false},
                            {
                                id: unknownAttributeId,
                                isImportant: false
                            }
                        ]
                    }
                },
                login: user.login,
                region: region.isoCode,
                infoModelId: infoModel.id
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(UnknownAttributesError);
    });

    it('should return error if new attributes is required', async () => {
        const user = await TestFactory.createUser({rules: {infoModel: {canEdit: true}}});
        const region = await TestFactory.createRegion();
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                attribute: {type: AttributeType.STRING, isValueRequired: true},
                userId: user.id
            }),
            TestFactory.createAttribute({
                attribute: {type: AttributeType.STRING},
                userId: user.id
            })
        ]);
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });

        let error = null;

        try {
            await executeHandler({
                body: {
                    titleTranslations: {},
                    descriptionTranslations: {},
                    attributes: {custom: attributes.map(({id}) => ({id, isImportant: false}))}
                },
                login: user.login,
                region: region.isoCode,
                infoModelId: infoModel.id
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(NewRequiredAttributesForbidden);
    });
});
