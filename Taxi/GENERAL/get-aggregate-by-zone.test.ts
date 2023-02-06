import {subDays} from 'date-fns';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import {hexPolygons, hexPolygonsZone, WMS_ZONES_ANALYTICS, WMS_ZONES_ORDERS_LIST} from '@/src/service/seed-db/fixtures';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {AnalystOrderSource, AnalyticSpecialValue, ZoneEntityType} from 'types/analyst';
import {Role} from 'types/idm';

import {getAggregateByZone} from './get-aggregate-by-zone';

describe('getAggregateByZone', () => {
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
                    ttlResidentsReal: 22
                },
                orders: [
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 17,
                        avgPrice: 835,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-08-01'),
                        countOrder: 13,
                        avgPrice: 749,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-05-01'),
                        countOrder: 38,
                        avgPrice: 719,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            },
            {
                ...hexPolygons[1],
                socdem: {
                    ttlResidentsReal: 25
                },
                orders: [
                    {
                        date: new Date('2022-01-01'),
                        countOrder: 13,
                        avgPrice: 1255,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-09-01'),
                        countOrder: 17,
                        avgPrice: 902,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-06-01'),
                        countOrder: 25,
                        avgPrice: 627,
                        avgCte: 10,
                        gmv: 20,
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

        const result = await getAggregateByZone.handle({
            data: {
                body: {
                    cityGeoId: CityGeoId.MOSCOW,
                    zone: hexPolygonsZone,
                    entity: ZoneEntityType.WMS_ZONE,
                    from: new Date('2021-11-01'),
                    to: new Date('2022-01-01')
                }
            },
            context
        });

        expect(result.socdem_ttl_residents_real).toEqual(47);
        expect(result.taxi_orders_avg_price).toEqual(1017);
        expect(result.taxi_orders_count).toEqual(1);
    });

    it('should return analytics data for a zone for manager with default access', async () => {
        const managerUser = await TestFactory.createUser({role: Role.MANAGER, uid: 100});
        const newContext = await TestFactory.createUserApiContext({region, user: managerUser});

        const hexes = [
            {
                ...hexPolygons[0],
                socdem: {
                    ttlResidentsReal: 22
                },
                orders: [
                    {
                        date: new Date('2021-12-01'),
                        countOrder: 17,
                        avgPrice: 835,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-08-01'),
                        countOrder: 13,
                        avgPrice: 749,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-05-01'),
                        countOrder: 38,
                        avgPrice: 719,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    }
                ]
            },
            {
                ...hexPolygons[1],
                socdem: {
                    ttlResidentsReal: 25
                },
                orders: [
                    {
                        date: new Date('2022-01-01'),
                        countOrder: 13,
                        avgPrice: 1255,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-09-01'),
                        countOrder: 17,
                        avgPrice: 902,
                        avgCte: 10,
                        gmv: 20,
                        type: AnalystOrderSource.TAXI
                    },
                    {
                        date: new Date('2021-06-01'),
                        countOrder: 25,
                        avgPrice: 627,
                        avgCte: 10,
                        gmv: 20,
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

        const result = await getAggregateByZone.handle({
            data: {
                body: {
                    cityGeoId: CityGeoId.MOSCOW,
                    zone: hexPolygonsZone,
                    entity: ZoneEntityType.WMS_ZONE,
                    from: new Date('2021-11-01'),
                    to: new Date('2022-01-01')
                }
            },
            context: newContext
        });

        expect(result.socdem_c1c2Res).toEqual(0);
        expect(result.socdem_ttl_residents_real).toEqual(47);
        expect(result.socdem_cost_on_meter).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.lavka_orders_avg_cte).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.eda_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.eda_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.lavka_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.lavka_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.lavka_orders_gmv).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.taxi_orders_avg_price).toEqual(AnalyticSpecialValue.NO_ACCESS);
        expect(result.taxi_orders_count).toEqual(AnalyticSpecialValue.NO_ACCESS);
    });

    it('should return analytics data for a zone by zone id', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});

        const wmsZone = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: subDays(nowDate, 4),
            storeId: store.id
        });

        const {zoneId} = await TestFactory.createWmsZonesAnalytics({
            zoneId: wmsZone.id,
            analystData: WMS_ZONES_ANALYTICS[0].analystData
        });

        await TestFactory.createWmsZoneOrders(
            WMS_ZONES_ORDERS_LIST.map((order) => ({
                ...order,
                zoneId
            }))
        );

        const result = await getAggregateByZone.handle({
            data: {
                body: {
                    cityGeoId: CityGeoId.MOSCOW,
                    zone: hexPolygonsZone,
                    entity: ZoneEntityType.WMS_ZONE,
                    zoneId
                }
            },
            context
        });

        expect(result.socdem_c1c2Res).toEqual(6417);
        expect(result.socdem_p4p5Res).toEqual(6415);
        expect(result.socdem_ttl_residents_real).toEqual(25478);
        expect(result.socdem_cost_on_meter).toEqual(76968.33);
        expect(result.taxi_orders_avg_price).toEqual(250);
        expect(result.taxi_orders_count).toEqual(4);
        expect(result.lavka_orders_avg_cte).toEqual(10);
        expect(result.lavka_orders_avg_price).toEqual(542);
        expect(result.lavka_orders_count).toEqual(7);
        expect(result.lavka_orders_gmv).toEqual(200);
        expect(result.eda_orders_avg_price).toEqual(645);
        expect(result.eda_orders_count).toEqual(14);
    });
});
