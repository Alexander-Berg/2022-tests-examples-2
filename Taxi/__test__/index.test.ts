import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {DraftApiPath} from '../../../../enums';
import {CorrectedGoalRule, CorrectedSingleRideRule, RulesData} from '../../../../types';
import SmartSubventionService from '../../SmartSubventionService';
import {getTableSmartRuleGroups, getTimezonesData} from '../index';

describe('getTableSmartRuleGroups', () => {
    it('Должна разделять список правил по таймзонам и типам правил', () => {
        const rules: Array<CorrectedSingleRideRule | CorrectedGoalRule> = [
            {
                id: '103483e9-6fb9-4a38-b2e3-7e2827863990',
                start: '2021-07-08T00:00:00+00:00',
                end: '2022-07-09T00:00:00+00:00',
                updated_at: '2021-07-07T09:33:18.605368+00:00',
                rates: [
                    {week_day: 'mon', start: '00:00', bonus_amount: '0'},
                    {week_day: 'thu', start: '00:00', bonus_amount: '134'},
                    {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '134'},
                ],
                budget_id: '2f38f9bb-6862-449b-bc08-20963059b6e2',
                schedule_ref: '8eca5910-3dac-4d08-949f-0e17df2eaf9c',
                draft_id: '197113',
                zone: 'accra',
                tariff_class: 'selfdriving',
                rule_type: 'single_ride',
            },
            {
                id: '26d859ea-aa44-49d3-865a-d53bd7ac8e34',
                start: '2021-07-17T11:11:00+00:00',
                end: '2022-07-18T22:22:00+00:00',
                updated_at: '2021-07-16T14:38:07.817082+00:00',
                activity_points: 22,
                rates: [
                    {week_day: 'wed', start: '11:11', bonus_amount: '123'},
                    {week_day: 'sat', start: '22:22', bonus_amount: '0'},
                ],
                budget_id: '6e25f6de-0ea2-4ca2-8eda-cfd29ac4894a',
                schedule_ref: 'de7423b1-ab7d-4ef0-9f98-0858fb068ae3',
                draft_id: '202261',
                zone: 'accra',
                tariff_class: 'business',
                geoarea: '11111',
                rule_type: 'single_ride',
            },
            {
                id: '6fdf24d8-afee-4c0e-80c3-206e9e17cbba',
                start: '2021-07-17T00:07:00+00:00',
                end: '2022-07-18T00:07:00+00:00',
                updated_at: '2021-06-17T15:56:23.391644+00:00',
                rates: [
                    {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                schedule_ref: 'cbfaa4ce-afd0-4139-99c4-5ccb157b5aea',
                draft_id: '186060',
                zone: 'accra',
                tariff_class: 'econom',
                rule_type: 'single_ride',
            },
            {
                id: '96f12b00-7587-46ec-a0a7-5a31f2b92b67',
                start: '2021-07-23T00:00:00+00:00',
                end: '2022-07-24T00:00:00+00:00',
                updated_at: '2021-07-21T07:55:09.761494+00:00',
                rates: [
                    {week_day: 'tue', start: '00:00', bonus_amount: '89'},
                    {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: '971f5f72-1aa3-4d62-9a4c-6723a65bf4b0',
                schedule_ref: '67bece95-437e-4694-bf9a-03c740b7448e',
                draft_id: '203740',
                zone: 'accra',
                tariff_class: 'business2',
                rule_type: 'single_ride',
            },
            {
                id: 'a6936b03-076a-4c9f-90a0-209e74421f47',
                tariff_class: 'selfdriving',
                geonode: 'br_root/br_ghana/br_accra/accra',
                counters: {
                    schedule: [
                        {week_day: 'wed', start: '00:00', counter: 'A'},
                        {week_day: 'thu', start: '00:00', counter: '0'},
                    ],
                    steps: [{id: 'A', steps: [{nrides: 12, amount: '12'}]}],
                },
                global_counters: [{local: 'A', global: '191533:A'}],
                window: 2,
                currency: 'GHS',
                start: '2021-07-01T00:00:00+00:00',
                end: '2022-07-02T00:00:00+00:00',
                updated_at: '2021-06-30T09:57:12.605962+00:00',
                budget_id: 'e814fcf9-8860-4c32-bb57-bd14d6b427df',
                draft_id: '191533',
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
            {
                id: 'ddff8c2c-6ba2-48d4-8168-141b02b38204',
                start: '2021-07-17T00:07:00+00:00',
                end: '2022-07-18T00:07:00+00:00',
                updated_at: '2021-06-17T15:56:23.391644+00:00',
                rates: [
                    {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                schedule_ref: 'cbfaa4ce-afd0-4139-99c4-5ccb157b5aea',
                draft_id: '186060',
                zone: 'accra',
                tariff_class: 'vezeteconom',
                rule_type: 'single_ride',
            },
            {
                id: 'f187e9f5-56f0-42ca-a630-e860f7d75f2f',
                start: '2021-07-17T00:07:00+00:00',
                end: '2022-07-18T00:07:00+00:00',
                updated_at: '2021-06-17T15:56:23.391644+00:00',
                rates: [
                    {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                schedule_ref: 'cbfaa4ce-afd0-4139-99c4-5ccb157b5aea',
                draft_id: '186060',
                zone: 'accra',
                tariff_class: 'uberx',
                rule_type: 'single_ride',
            },
            {
                id: 'feaca8dd-bab4-4939-b195-b9ac50f43d5e',
                tariff_class: 'business2',
                geonode: 'br_root/br_ghana/br_accra/accra',
                counters: {
                    schedule: [
                        {week_day: 'fri', start: '12:31', counter: 'A'},
                        {week_day: 'sat', start: '23:42', counter: '0'},
                    ],
                    steps: [{id: 'A', steps: [{nrides: 2, amount: '3'}]}],
                },
                global_counters: [{local: 'A', global: '199609:A'}],
                window: 4,
                currency: 'GHS',
                start: '2021-07-14T00:00:00+00:00',
                end: '2022-07-17T00:00:00+00:00',
                updated_at: '2021-07-12T17:00:22.307319+00:00',
                budget_id: 'bc2c56b0-295f-4e9e-88f4-53e171a2e05b',
                draft_id: '199609',
                tag: 'kek',
                activity_points: 22,
                rule_type: 'goal',
                schedule_ref: 'schedule_ref',
            },
        ];

        return expectSaga(getTableSmartRuleGroups, rules)
            .provide([
                [
                    call(getTimezonesData, rules),
                    [
                        {
                            zone: 'accra',
                            tariffZone: 'accra',
                            timeZoneData: {
                                name: 'Africa/Accra',
                                offsetData: 'Africa/Accra МСК-3',
                                offset: -3,
                                correctedOffset: 0,
                                currency: 'GHS',
                            },
                        },
                    ],
                ],
                [call(SmartSubventionService.getDrafts, rules), []],
            ])
            .run()
            .then(res => {
                const expected = {
                    timeZoneData: {
                        name: 'Africa/Accra',
                        offsetData: 'Africa/Accra МСК-3',
                        offset: -3,
                        correctedOffset: 0,
                        currency: 'GHS',
                    },
                    rules: [
                        {
                            id: '103483e9-6fb9-4a38-b2e3-7e2827863990',
                            updated_at: '2021-07-07T09:33:18.605368+00:00',
                            rates: [
                                {week_day: 'mon', start: '00:00', bonus_amount: '0'},
                                {week_day: 'thu', start: '00:00', bonus_amount: '134'},
                                {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                                {week_day: 'sun', start: '00:00', bonus_amount: '134'},
                            ],
                            budget_id: '2f38f9bb-6862-449b-bc08-20963059b6e2',
                            zone: 'accra',
                            tariff_class: 'selfdriving',
                            rule_type: 'single_ride',
                            draft_id: '197113',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: '26d859ea-aa44-49d3-865a-d53bd7ac8e34',
                            updated_at: '2021-07-16T14:38:07.817082+00:00',
                            activity_points: 22,
                            rates: [
                                {week_day: 'wed', start: '11:11', bonus_amount: '123'},
                                {week_day: 'sat', start: '22:22', bonus_amount: '0'},
                            ],
                            budget_id: '6e25f6de-0ea2-4ca2-8eda-cfd29ac4894a',
                            zone: 'accra',
                            tariff_class: 'business',
                            geoarea: '11111',
                            rule_type: 'single_ride',
                            draft_id: '202261',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: '6fdf24d8-afee-4c0e-80c3-206e9e17cbba',
                            updated_at: '2021-06-17T15:56:23.391644+00:00',
                            rates: [
                                {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                                {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                            ],
                            budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                            zone: 'accra',
                            tariff_class: 'econom',
                            rule_type: 'single_ride',
                            draft_id: '186060',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: '96f12b00-7587-46ec-a0a7-5a31f2b92b67',
                            updated_at: '2021-07-21T07:55:09.761494+00:00',
                            rates: [
                                {week_day: 'tue', start: '00:00', bonus_amount: '89'},
                                {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                            ],
                            budget_id: '971f5f72-1aa3-4d62-9a4c-6723a65bf4b0',
                            zone: 'accra',
                            tariff_class: 'business2',
                            rule_type: 'single_ride',
                            draft_id: '203740',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: 'a6936b03-076a-4c9f-90a0-209e74421f47',
                            tariff_class: 'selfdriving',
                            geonode: 'br_root/br_ghana/br_accra/accra',
                            global_counters: [{local: 'A', global: '191533:A'}],
                            window: 2,
                            currency: 'GHS',
                            updated_at: '2021-06-30T09:57:12.605962+00:00',
                            budget_id: 'e814fcf9-8860-4c32-bb57-bd14d6b427df',
                            draft_id: '191533',
                            rule_type: 'goal',
                            steps: [{id: 'A', steps: [{nrides: 12, amount: '12'}]}],
                            rates: [
                                {week_day: 'wed', start: '00:00', bonus_amount: 'A'},
                                {week_day: 'thu', start: '00:00', bonus_amount: '0'},
                            ],
                            zone: 'accra',
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: 'ddff8c2c-6ba2-48d4-8168-141b02b38204',
                            updated_at: '2021-06-17T15:56:23.391644+00:00',
                            rates: [
                                {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                                {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                            ],
                            budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                            zone: 'accra',
                            tariff_class: 'vezeteconom',
                            rule_type: 'single_ride',
                            draft_id: '186060',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: 'f187e9f5-56f0-42ca-a630-e860f7d75f2f',
                            updated_at: '2021-06-17T15:56:23.391644+00:00',
                            rates: [
                                {week_day: 'sat', start: '00:00', bonus_amount: '12'},
                                {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                            ],
                            budget_id: '623609a7-da20-49d7-9601-82fdab751692',
                            zone: 'accra',
                            tariff_class: 'uberx',
                            rule_type: 'single_ride',
                            draft_id: '186060',
                            isScheduleRef: false,
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                        {
                            id: 'feaca8dd-bab4-4939-b195-b9ac50f43d5e',
                            tariff_class: 'business2',
                            geonode: 'br_root/br_ghana/br_accra/accra',
                            global_counters: [{local: 'A', global: '199609:A'}],
                            window: 4,
                            currency: 'GHS',
                            updated_at: '2021-07-12T17:00:22.307319+00:00',
                            budget_id: 'bc2c56b0-295f-4e9e-88f4-53e171a2e05b',
                            draft_id: '199609',
                            tag: 'kek',
                            activity_points: 22,
                            rule_type: 'goal',
                            steps: [{id: 'A', steps: [{nrides: 2, amount: '3'}]}],
                            rates: [
                                {week_day: 'fri', start: '12:31', bonus_amount: 'A'},
                                {week_day: 'sat', start: '23:42', bonus_amount: '0'},
                            ],
                            zone: 'accra',
                            apiPath: DraftApiPath.Unknown,
                            draftZones: ['accra'],
                        },
                    ],
                };
                const {rules, ...otherValues} = res.returnValue as RulesData;
                expect({
                    ...otherValues,
                    rules: rules.map(rule => {
                        const {start, end, ...otherProps} = rule;

                        return otherProps;
                    }),
                }).toEqual(expected);
            });
    });
});
