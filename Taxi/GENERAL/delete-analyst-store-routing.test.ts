import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {deleteAnalystStoreRoutingHandler} from 'server/routes/api/internal/v1/analyst-store-routing/delete-analyst-store-routing';
import {AnalystStoreRoutingStatus} from 'types/analyst-store-routing';

describe('delete routing new store', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return routing', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            cityId: CityGeoId.MOSCOW,
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        const res = await deleteAnalystStoreRoutingHandler.handle({
            data: {body: {id: '1'}},
            context
        });

        expect(res.deletedCount).toBeGreaterThan(0);
    });

    it('should throw error if routing new store not exist', async () => {
        const unknownId = random(999999);

        await expect(
            deleteAnalystStoreRoutingHandler.handle({
                data: {body: {id: String(unknownId)}},
                context
            })
        ).rejects.toThrow();
    });
});
