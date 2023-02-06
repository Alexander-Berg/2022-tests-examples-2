import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {SearchEntity} from 'types/search';

import {addSearchHistoryHandler} from './add-search-history';

describe('add search history', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return search history item', async () => {
        const res = await addSearchHistoryHandler.handle({
            data: {
                body: {
                    entityData: {
                        id: '1',
                        type: SearchEntity.MANAGER_POINTS,
                        cityGeoId: CityGeoId.MOSCOW,
                        name: 'name',
                        location: {point: [32, 34]}
                    }
                }
            },
            context
        });

        expect(res.items[0].id).not.toBeUndefined();
    });
});
