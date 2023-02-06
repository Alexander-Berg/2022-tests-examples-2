import {random} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getParentInfoModelHandler} from './get-parent-info-model';

describe('get parent info model', () => {
    let user: User;
    let langs: Lang[];
    let langCodes: string[];
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user});
    });

    it('should return parent info model with translations', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            infoModel: {
                titleTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
        });

        let result = await getParentInfoModelHandler.handle({
            context,
            data: {
                params: {
                    id: parentMasterCategory.id
                }
            }
        });

        expect(result).toEqual({
            infoModel: {
                id: infoModel.id,
                code: infoModel.code,
                titleTranslations: infoModel.titleTranslationMap,
                descriptionTranslations: infoModel.descriptionTranslationMap
            },
            category: {
                id: parentMasterCategory.id,
                code: parentMasterCategory.code,
                nameTranslations: parentMasterCategory.nameTranslationMap,
                descriptionTranslations: parentMasterCategory.descriptionTranslationMap,
                ownProductsCount: 0
            }
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            sortOrder: 0
        });

        result = await getParentInfoModelHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategory.id
                }
            }
        });

        expect(result).toEqual({
            infoModel: {
                id: infoModel.id,
                code: infoModel.code,
                titleTranslations: infoModel.titleTranslationMap,
                descriptionTranslations: infoModel.descriptionTranslationMap
            },
            category: {
                id: parentMasterCategory.id,
                code: parentMasterCategory.code,
                nameTranslations: parentMasterCategory.nameTranslationMap,
                descriptionTranslations: parentMasterCategory.descriptionTranslationMap,
                ownProductsCount: 0
            }
        });
    });

    it('should throw error if master category does not exist', async () => {
        const unknownId = random(999999);
        const promise = getParentInfoModelHandler.handle({
            context,
            data: {
                params: {id: unknownId}
            }
        });

        await expect(promise).rejects.toThrow(EntityNotFoundError);
        await expect(promise.catch((err) => err.parameters)).resolves.toMatchObject({
            entity: 'InfoModelWithOwnerMasterCategory'
        });
    });
});
