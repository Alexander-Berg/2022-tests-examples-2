import {subDays} from 'date-fns';
import values from 'lodash/values';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';
import {read, utils} from 'xlsx';

import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getWmsZonesAnalyticsHandler} from './export-wms-zones-analytics';
import {wmsZoneAnalyticsHeaderKeys, zoneAnalyticsMock} from './fixtures';

const wmsZoneHeaderKeys = [
    'export-entities-id',
    'export-entities-name',
    'export-entities-status',
    'export-entities-delivery-type',

    ...wmsZoneAnalyticsHeaderKeys
];

describe('getWmsZonesAnalyticsHandler()', () => {
    let context: UserApiRequestContext;

    beforeEach(async () => {
        context = await TestFactory.createUserApiContext();
    });

    it('should export currently effective zones only', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});
        await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: subDays(nowDate, 4),
            storeId: store.id
        });
        await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 6),
            effectiveTill: subDays(nowDate, 5),
            storeId: store.id
        });
        const effectiveZone = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            storeId: store.id
        });

        await TestFactory.createWmsZonesAnalytics({
            zoneId: effectiveZone.id,
            analystData: zoneAnalyticsMock
        });

        const file = await getWmsZonesAnalyticsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
            context
        });

        const rows = read(file, {type: 'buffer'});
        const sheetRows = values(rows.Sheets);
        const tableRows = utils.sheet_to_json<string[]>(sheetRows[0]);

        expect(tableRows).toHaveLength(1);
        expect(tableRows[0]).toMatchObject({'export-entities-id': effectiveZone.id});
    });

    it('should export two wms zones', async () => {
        const cityGeoId = CityGeoId.MOSCOW;

        const store = await TestFactory.createWmsStore({cityGeoId});
        await TestFactory.createWmsZone({
            storeId: store.id
        });

        const oneZone = await TestFactory.createWmsZone({
            storeId: store.id
        });

        const secondZone = await TestFactory.createWmsZone({
            storeId: store.id
        });

        await TestFactory.createWmsZonesAnalytics({
            zoneId: oneZone.id,
            analystData: zoneAnalyticsMock
        });

        await TestFactory.createWmsZonesAnalytics({
            zoneId: secondZone.id,
            analystData: zoneAnalyticsMock
        });

        const file = await getWmsZonesAnalyticsHandler({
            data: {query: {filters: {cityGeoId, wmsZoneIds: [secondZone.id, oneZone.id]}}},
            context
        });

        const rows = read(file, {type: 'buffer'});
        const sheetRows = values(rows.Sheets);

        const tableRows = utils.sheet_to_json<string[]>(sheetRows[0]);

        expect(tableRows).toHaveLength(2);
    });

    it('should export zones with correct fields', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});
        await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: subDays(nowDate, 4),
            storeId: store.id
        });
        const zoneNow = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            storeId: store.id,
            store
        });

        await TestFactory.createWmsZonesAnalytics({
            zoneId: zoneNow.id,
            analystData: zoneAnalyticsMock
        });

        const file = await getWmsZonesAnalyticsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
            context
        });

        const rows = read(file, {type: 'buffer'});

        const sheetRows = values(rows.Sheets);

        const tableHeaders = utils.sheet_to_json<string[]>(sheetRows[0], {
            header: 1,
            range: 'A1-ZZZ1',
            blankrows: false
        })[0];

        expect(tableHeaders).toEqual(wmsZoneHeaderKeys);
    });
});
