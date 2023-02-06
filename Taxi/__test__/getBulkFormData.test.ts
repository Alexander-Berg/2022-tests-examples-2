import moment from 'moment';
import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {apiInstance as geoHierarchyApiInstance} from '_api/geo-hierarchy/GeoHierarchyV2API';
import {DraftStatusEnum} from '_libs/drafts/types';

import {apiInstance} from '../../../api/SmartSubventionsAPI';
import {BULK_MODEL, GEO_HIERARCHY_REQUEST_DATA} from '../../../consts';
import {DraftApiPath, ZoneCheckboxMode} from '../../../enums';
import {REQUEST_ZONE_OPERATION} from '../../../sagas/services/consts';
import {getTimezonesData} from '../../../sagas/services/utils';
import {BulkFormData, CorrectedSingleRideRule, TableGoalRule} from '../../../types';
import {getBulkFormData} from '../saga';

const omitRuleEnd = (data: BulkFormData) => {
    return data.map(val => ({
        ...val,
        rules: val.rules.map(rule => {
            const {end, ...otherProps} = rule;
            return otherProps;
        }),
    }));
};
describe('getBulkFormData', () => {
    test('zone an hierarchy, selected rules, loaded data', () => {
        const zone = 'accra';
        const hierarchy = 'br_moscow';
        const selectedRule: CorrectedSingleRideRule = {
            id: '2c2181db-b81a-4949-bb17-0c929a6f94e8',
            start: '2021-04-30 03:00',
            end: '2021-05-02T00:00:00+00:00',
            updated_at: '2021-04-28T10:14:15.30534+00:00',
            rates: [
                {week_day: 'thu', start: '11:11', bonus_amount: '123'},
                {week_day: 'fri', start: '22:22', bonus_amount: '0'},
            ],
            budget_id: '0a18d5da-0c3a-445b-92d8-f410f46dd0a6',
            schedule_ref: '93b4d757-4807-4bca-8d47-55039dab6e84',
            draft_id: '161084',
            zone: zone,
            tariff_class: 'econom',
            rule_type: 'single_ride',
        };
        const selectedHierarchyRule: TableGoalRule = {
            id: 'fa8362c8-b506-473c-a4d9-4d95413f18e9',
            tariff_class: 'econom',
            geonode: 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow',
            rates: [
                {week_day: 'thu', start: '11:11', bonus_amount: '123'},
                {week_day: 'fri', start: '22:22', bonus_amount: '0'},
            ],
            steps: [
                {
                    id: 'A',
                    steps: [{nrides: 1, amount: '1033.44'}],
                },
            ],
            window: 1,
            currency: 'RUB',
            start: '2021-04-08 00:00',
            end: moment('2021-05-02T00:00:00+00:00'),
            budget_id: '1e055450-e77f-43b2-a9e0-cfc9c4c526ad',
            draft_id: '151623',
            tag: 'test_goal_subv_1',
            branding_type: 'no_full_branding',
            rule_type: 'goal',
            zone: 'br_moscow',
            apiPath: DraftApiPath.PersonalGoalCreate,
            ticket: '',
            draftZones: [],
        };
        const state: unknown = {
            asyncOperations: {
                [REQUEST_ZONE_OPERATION]: {
                    result: {
                        timeZoneData: {
                            name: 'Africa/Accra',
                            offsetData: 'Africa/Accra МСК-3',
                            offset: -3,
                        },
                        rules: [
                            selectedRule,
                            selectedHierarchyRule,
                            {
                                id: '55f6d546-2cae-4723-a86e-0ede7078332c',
                                start: '2021-04-30 03:00',
                                end: moment('2021-05-02T00:00:00+00:00'),
                                updated_at: '2021-04-28T10:14:15.30534+00:00',
                                rates: [
                                    {week_day: 'thu', start: '11:11', bonus_amount: '123'},
                                    {week_day: 'fri', start: '22:22', bonus_amount: '0'},
                                ],
                                budget_id: '0a18d5da-0c3a-445b-92d8-f410f46dd0a6',
                                schedule_ref: '93b4d757-4807-4bca-8d47-55039dab6e84',
                                draft_id: '161084',
                                zone: zone,
                                tariff_class: 'uberx',
                                rule_type: 'single_ride',
                                multidraftId: undefined,
                            },
                            {
                                id: '7372390b-7ddf-43c3-9802-c3326fd9bf2f',
                                start: '2021-04-30 03:00',
                                end: moment('2021-05-02T00:00:00+00:00'),
                                updated_at: '2021-04-28T10:14:15.30534+00:00',
                                rates: [
                                    {week_day: 'thu', start: '11:11', bonus_amount: '123'},
                                    {week_day: 'fri', start: '22:22', bonus_amount: '0'},
                                ],
                                budget_id: '0a18d5da-0c3a-445b-92d8-f410f46dd0a6',
                                schedule_ref: '93b4d757-4807-4bca-8d47-55039dab6e84',
                                draft_id: '161084',
                                zone: zone,
                                tariff_class: 'vezeteconom',
                                rule_type: 'single_ride',
                                multidraftId: undefined,
                            },
                        ],
                    },
                },
            },
            [BULK_MODEL]: {
                draft: {
                    status: DraftStatusEnum.Approved,
                    data: {
                        ticketData: {},
                        closeAt: {
                            date: moment(),
                            time: '10:00',
                        },
                        ruleIds: [],
                    },
                    id: 123,
                },
                zoneData: {
                    zoneCheckbox: ZoneCheckboxMode.Partial,
                    ruleIds: {
                        '2c2181db-b81a-4949-bb17-0c929a6f94e8': true,
                        'fa8362c8-b506-473c-a4d9-4d95413f18e9': true,
                    },
                },
            },
        };

        return expectSaga(getBulkFormData)
            .withState(state)
            .provide([
                [call(geoHierarchyApiInstance.request, GEO_HIERARCHY_REQUEST_DATA), []],
                [
                    call(getTimezonesData, [selectedRule, selectedHierarchyRule]),
                    [
                        {
                            zone: zone,
                            tariffZone: zone,
                            timeZoneData: {
                                name: 'Africa/Accra',
                                offsetData: 'Africa/Accra МСК-3',
                                offset: -3,
                            },
                        },
                        {
                            zone: hierarchy,
                            tariffZone: 'boryasvo',
                            timeZoneData: {
                                name: 'Europe/Moscow',
                                offsetData: 'Europe/Moscow МСК0',
                                offset: 0,
                            },
                        },
                    ],
                ],
                [call(apiInstance.getByDraftIds, ['151623']), []],
            ])
            .run()
            .then(res => {
                expect(omitRuleEnd(res.returnValue)).toEqual([
                    {
                        zone: 'accra',
                        offsetData: 'Africa/Accra МСК-3',
                        offset: -3,
                        zoneName: 'accra',
                        rules: [
                            {
                                id: '2c2181db-b81a-4949-bb17-0c929a6f94e8',
                                tariffClass: 'econom',
                                draftId: '161084',
                                ruleType: 'single_ride',
                                subZone: undefined,
                            },
                        ],
                    },
                    {
                        zone: 'br_moscow',
                        offsetData: 'Europe/Moscow МСК0',
                        offset: 0,
                        zoneName: 'br_moscow',
                        rules: [
                            {
                                draftId: '161084',
                                id: '2c2181db-b81a-4949-bb17-0c929a6f94e8',
                                ruleType: 'single_ride',
                                subZone: undefined,
                                tariffClass: 'econom',
                            },
                            {
                                id: 'fa8362c8-b506-473c-a4d9-4d95413f18e9',
                                tariffClass: 'econom',
                                draftId: '151623',
                                ruleType: 'goal',
                                subZone: undefined,
                            },
                        ],
                    },
                ]);
            });
    });
    // tslint:disable-next-line:max-file-line-count
});
