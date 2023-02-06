import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {getSearchHistoryHandler} from 'server/routes/api/internal/v1/search/get-search-history';

describe('get search history', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return search history items', async () => {
        await TestFactory.createSearchHistory(user.uid);

        const res = await getSearchHistoryHandler.handle({
            data: {},
            context
        });

        expect(res.items).not.toHaveLength(0);
    });

    it('should return no search history items if there`re no history for this user', async () => {
        const res = await getSearchHistoryHandler.handle({
            data: {},
            context
        });

        expect(res.items).toHaveLength(0);
    });
});
