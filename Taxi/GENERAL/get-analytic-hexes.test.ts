import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {AnalystEntity} from 'types/analyst';

import {getAnalyticHexesHandler} from './get-analytic-hexes';

describe('getAnalyticsHandler()', () => {
    let region: RegionEntity;
    let user: UserEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should retrieve hexes by geo id', async () => {
        await TestFactory.createHex();
        await TestFactory.createSocdem();
        await TestFactory.createIntervals();

        const res = await getAnalyticHexesHandler.handle({
            data: {
                query: {
                    filters: {
                        cityGeoId: CityGeoId.MOSCOW,
                        layers: [AnalystEntity.SOCDEM_C1C2RES],
                        fromLngLat: [0, 0],
                        toLngLat: [90, 180]
                    }
                }
            },
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should get hex by map tile coordinates', async () => {
        await TestFactory.createHex({
            id: '23123',
            polygon:
                // eslint-disable-next-line max-len
                'POLYGON ((38.48308873803271 55.28482415491604, 38.48544657360161 55.28374238662002, 38.4882095776162 55.2844816204767, 38.48861485927743 55.28630268796643, 38.48625690045098 55.28738449950236, 38.48349378322096 55.2866452003062, 38.48308873803271 55.28482415491604))',
            cityGeoId: CityGeoId.MOSCOW,
            city: 'Moscow'
        });
        await TestFactory.createSocdem();
        await TestFactory.createIntervals();

        const res = await getAnalyticHexesHandler.handle({
            data: {
                query: {
                    filters: {
                        fromLngLat: [0, 0],
                        toLngLat: [90, 180],
                        layers: [AnalystEntity.SOCDEM_C1C2RES]
                    }
                }
            },
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return 0 results, given hex coordinates in Africa', async () => {
        await TestFactory.createHex();
        await TestFactory.createSocdem();
        await TestFactory.createIntervals();

        const res = await getAnalyticHexesHandler.handle({
            data: {
                query: {
                    filters: {
                        fromLngLat: [9.795678, 25.424706],
                        toLngLat: [8.407168, 33.164245],
                        layers: [AnalystEntity.SOCDEM_C1C2RES]
                    }
                }
            },
            context
        });

        expect(res.items).toHaveLength(0);
    });

    it('should throw an error if city geo id does not exist', async () => {
        await TestFactory.createHex();
        await TestFactory.createSocdem();
        await TestFactory.createIntervals();

        await expect(
            getAnalyticHexesHandler.handle({
                data: {
                    query: {
                        filters: {
                            cityGeoId: 4000,
                            fromLngLat: [0, 0],
                            toLngLat: [90, 180],
                            layers: [AnalystEntity.SOCDEM_C1C2RES]
                        }
                    }
                },
                context
            })
        ).rejects.toThrow();
    });
});
