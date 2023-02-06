import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone} from 'service/seed-db/fixtures';
import {AnalystForecastMode, CourierTypePredict} from 'types/analyst-forecast-orders';
import {AnalystStoreRoutingStatus} from 'types/analyst-store-routing';

import {updateAnalystForecastOrdersHandler} from './update-analyst-forecast-order';

describe('update analyst forecast orders', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return analyst forecast orders', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            zone,
            name: 'test name'
        });

        await TestFactory.createAnalystForecastOrders(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            cityGeoId: CityGeoId.MOSCOW,
            managerPointId: managerPoint.id,
            managerZoneId: managerZone.id,
            mode: AnalystForecastMode.NEW_STORE_NEW_ZONE,
            courierTypePredict: CourierTypePredict.FOOT
        });

        const res = await updateAnalystForecastOrdersHandler.handle({
            data: {body: {id: '1', status: AnalystStoreRoutingStatus.STOPPED}},
            context
        });

        expect(res.id).toEqual('1');
        expect(res.status).toEqual(AnalystStoreRoutingStatus.STOPPED);
    });

    it('should throw error if routing new store not exist', async () => {
        const unknownId = random(999999);

        await expect(
            updateAnalystForecastOrdersHandler.handle({
                data: {body: {id: String(unknownId), status: AnalystStoreRoutingStatus.DONE}},
                context
            })
        ).rejects.toThrow();
    });
});
