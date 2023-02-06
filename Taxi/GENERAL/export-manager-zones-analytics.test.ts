import values from 'lodash/values';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';
import {read, utils} from 'xlsx';

import {getManagerZonesAnalytics} from '@/src/entities/manager-zone-analytics/api/get-manager-zones-analytics';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import type {ManagerZonesAnalyticsRow} from 'types/export';

import {getManagerZonesAnalyticsHandler} from './export-manager-zones-analytics';
import {managerZoneAnalyticsHeaderKeys, zoneAnalyticsMock} from './fixtures';

const managerZoneHeaderKeys = ['export-entities-id', 'export-entities-name', ...managerZoneAnalyticsHeaderKeys];

describe('getManagerZonesAnalyticsHandler()', () => {
    let context: UserApiRequestContext;

    beforeEach(async () => {
        context = await TestFactory.createUserApiContext();
    });

    it('should export newly created manager zone', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone 1';
        const user = await context.user;

        const zone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });
        await TestFactory.createManagerZoneAnalytics({
            managerZoneId: zone.id,
            analystData: zoneAnalyticsMock
        });

        const zonesAnalyticsEntities = await getManagerZonesAnalytics({
            cityGeoId
        });

        const file = await getManagerZonesAnalyticsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
            context
        });

        const rows = read(file, {type: 'buffer'});
        const sheetRows = values(rows.Sheets);
        const tableRows = utils.sheet_to_json<ManagerZonesAnalyticsRow[]>(sheetRows[0]);

        expect(tableRows).toEqual(
            expect.arrayContaining([
                expect.objectContaining({'export-entities-id': zonesAnalyticsEntities[0].managerZoneId})
            ])
        );
    });

    it('should export two zones', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone 1';
        const user = await context.user;

        const zoneOne = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        const zoneTwo = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        const zoneThree = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        await TestFactory.createManagerZoneAnalytics({
            managerZoneId: zoneOne.id,
            analystData: zoneAnalyticsMock
        });

        await TestFactory.createManagerZoneAnalytics({
            managerZoneId: zoneTwo.id,
            analystData: zoneAnalyticsMock
        });

        await TestFactory.createManagerZoneAnalytics({
            managerZoneId: zoneThree.id,
            analystData: zoneAnalyticsMock
        });

        const file = await getManagerZonesAnalyticsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, draftIds: [zoneOne.id, zoneTwo.id]}}},
            context
        });

        const rows = read(file, {type: 'buffer'});
        const sheetRows = values(rows.Sheets);
        const tableRows = utils.sheet_to_json<ManagerZonesAnalyticsRow[]>(sheetRows[0]);

        expect(tableRows).toHaveLength(2);
    });

    it('should export manager zones with correct fields', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone 2';
        const user = await context.user;

        const zone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });
        await TestFactory.createManagerZoneAnalytics({
            managerZoneId: zone.id,
            analystData: zoneAnalyticsMock
        });

        const file = await getManagerZonesAnalyticsHandler({
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

        expect(tableHeaders).toEqual(managerZoneHeaderKeys);
    });
});
