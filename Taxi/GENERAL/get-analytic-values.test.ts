import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import {hexesZone, hexPolygons} from '@/src/service/seed-db/fixtures';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {AnalystOrderSource, AnalyticSpecialValue} from 'types/analyst';
import {Role} from 'types/idm';

import {getAnalyticValuesHandler} from './get-analytic-values';

describe('getAnalyticValuesHandler', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return aggregated analytics data for a zone', async () => {
        const hexes = [
            {
                ...hexPolygons[0],
                socdem: {
                    ttlResidentsReal: 50
                },
                orders: [
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 10,
                        avgPrice: 500,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-11-01'),
                        countOrder: 20,
                        avgPrice: 800,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-10-31'),
                        countOrder: 40,
                        avgPrice: 1000,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            },
            {
                ...hexPolygons[1],
                socdem: {
                    ttlResidentsReal: 40
                },
                orders: [
                    {
                        date: new Date('2022-01-01'),
                        countOrder: 30,
                        avgPrice: 500,
                        avgCte: 10,
                        gmv: 30,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 20,
                        avgPrice: 800,
                        avgCte: 10,
                        gmv: 30,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            }
        ];

        await Promise.all(
            hexes.map(({id, polygon, city, cityGeoId}) => TestFactory.createHex({id, polygon, city, cityGeoId}))
        );
        await Promise.all(hexes.map(({id, socdem}) => TestFactory.createSocdem({hexId: id, socdem})));
        await Promise.all(
            hexes.map(({id, orders}) =>
                TestFactory.createHexOrders(
                    orders.map((orderData) => ({
                        hexId: id,
                        ...orderData
                    }))
                )
            )
        );

        const result = await getAnalyticValuesHandler.handle({
            data: {
                query: {
                    filters: {
                        ...hexesZone,
                        cityGeoId: CityGeoId.MOSCOW
                    },
                    from: new Date('2021-11-01'),
                    to: new Date('2022-01-01')
                }
            },
            context
        });

        const item1 = result.items.find(({hexId}) => hexId === hexes[0].id);
        const item2 = result.items.find(({hexId}) => hexId === hexes[1].id);

        expect(item1?.socdem_ttl_residents_real).toEqual(50);
        expect(item1?.taxi_orders_avg_price).toEqual(700);
        expect(item1?.taxi_orders_count).toEqual(0);

        expect(item2?.socdem_ttl_residents_real).toEqual(40);
        expect(item2?.taxi_orders_avg_price).toEqual(620);
        expect(item2?.taxi_orders_count).toEqual(1);
    });

    it('should return aggregated analytics data for a zone for manager with default access', async () => {
        const managerUser = await TestFactory.createUser({role: Role.MANAGER, uid: 100});
        const newContext = await TestFactory.createUserApiContext({region, user: managerUser});

        const hexes = [
            {
                ...hexPolygons[0],
                socdem: {
                    ttlResidentsReal: 50
                },
                orders: [
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 10,
                        avgPrice: 500,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-11-01'),
                        countOrder: 20,
                        avgPrice: 800,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-10-31'),
                        countOrder: 40,
                        avgPrice: 1000,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            },
            {
                ...hexPolygons[1],
                socdem: {
                    ttlResidentsReal: 40
                },
                orders: [
                    {
                        date: new Date('2022-01-01'),
                        countOrder: 30,
                        avgPrice: 500,
                        avgCte: 10,
                        gmv: 30,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 20,
                        avgPrice: 800,
                        avgCte: 10,
                        gmv: 30,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            }
        ];

        await Promise.all(
            hexes.map(({id, polygon, city, cityGeoId}) => TestFactory.createHex({id, polygon, city, cityGeoId}))
        );
        await Promise.all(hexes.map(({id, socdem}) => TestFactory.createSocdem({hexId: id, socdem})));
        await Promise.all(
            hexes.map(({id, orders}) =>
                TestFactory.createHexOrders(
                    orders.map((orderData) => ({
                        hexId: id,
                        ...orderData
                    }))
                )
            )
        );

        const result = await getAnalyticValuesHandler.handle({
            data: {
                query: {
                    filters: {
                        ...hexesZone,
                        cityGeoId: CityGeoId.MOSCOW
                    },
                    from: new Date('2021-11-01'),
                    to: new Date('2022-01-01')
                }
            },
            context: newContext
        });

        const item1 = result.items.find(({hexId}) => hexId === hexes[0].id);
        const item2 = result.items.find(({hexId}) => hexId === hexes[1].id);

        expect(item1?.socdem_ttl_residents_real).toEqual(50);
        expect(item1?.taxi_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item1?.taxi_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item1?.eda_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item1?.eda_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item1?.lavka_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item1?.lavka_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);

        expect(item2?.socdem_ttl_residents_real).toEqual(40);
        expect(item2?.taxi_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item2?.taxi_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item2?.eda_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item2?.eda_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item2?.lavka_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(item2?.lavka_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
    });
});
