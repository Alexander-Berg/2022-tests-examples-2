/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getAttributeHistory} from './get-history-by-attribute-id';

describe('get history by attribute id', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return attribute history', async () => {
        // TODO: implement
    });

    it('should return error if attribute does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        try {
            await getAttributeHistory.handle({
                context,
                data: {params: {id: unknownId}}
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Attribute'});
    });
});
