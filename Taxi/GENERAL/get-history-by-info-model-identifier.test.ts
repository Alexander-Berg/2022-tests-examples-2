/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {orderBy} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import {AttributeType} from '@/src/types/attribute';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getInfoModelHistory} from './get-history-by-info-model-identifier';

describe('get history by info-model id', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return info-model history', async () => {
        const attr1 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
        });
        const attr2 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
        });
        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [
                {id: attr1.id, isImportant: true},
                {id: attr2.id, isImportant: false}
            ],
            infoModel: {
                titleTranslationMap: {en: 'test_info_model_title_en'}
            }
        });

        const history = await getInfoModelHistory.handle({
            context,
            data: {params: {id: infoModel.id}}
        });

        history.list[0].mutation.attributes!.new = orderBy(history.list[0].mutation.attributes!.new, (a) => a.code);

        expect(history.list.slice(0, 2)).toMatchObject([
            {
                author: {id: user.id, login: user.login},
                stamp: MOCKED_STAMP,
                mutation: {
                    id: {old: null, new: infoModel.id},
                    code: {old: null, new: infoModel.code},
                    titleTranslationMap: {old: null, new: infoModel.titleTranslationMap},
                    attributes: {
                        old: [],
                        new: orderBy([{code: attr2.code, isImportant: false}], (a) => a.code)
                    }
                }
            }
        ]);
    });

    it('should return error if info-model does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        try {
            await getInfoModelHistory.handle({
                context,
                data: {params: {id: unknownId}}
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'InfoModel'});
    });
});
