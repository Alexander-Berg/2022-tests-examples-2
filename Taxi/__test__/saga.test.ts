import moment from 'moment';
import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'redux-saga/effects';

import {apiInstance as geoHierarchyApiInstance} from '_api/geo-hierarchy/GeoHierarchyV2API';
import {AdminGeoNode} from '_api/geo-hierarchy/types';
import {apiInstance as tariffsApiInstance} from '_api/tariffs/TariffsAPI';
import {BRANDING_VALUES} from '_pkg/utils/makeBrandingTypeOptions';
import {DraftModes} from '_types/common/drafts';

import {apiInstance as budgetApiInstance} from '../../../api/BudgetAPI';
import {apiInstance as smartSubventionsApiInstance} from '../../../api/SmartSubventionsAPI';
import {DEFAULT_TIME, GEO_HIERARCHY_REQUEST_DATA} from '../../../consts';
import {GoalMode} from '../../../enums';
import {GEONODES_OPERATION} from '../../../sagas/services/consts';
import SmartSubventionService from '../../../sagas/services/SmartSubventionService';
import {getBudget} from '../../../sagas/services/utils';
import {getSmartRuleDraft} from '../../../sagas/utils';
import {GoalRuleVM, SingleRideRuleVM, TariffSettingsZone} from '../../../types';
import {getDefaultEndDate, getDefaultStartDate} from '../../../utils';
import {getCurrModel} from '../saga';

const GEO_NODES: Array<AdminGeoNode> = [
    {
        name: 'br_astana',
        hierarchy_type: 'BR',
        node_type: 'agglomeration',
        tariff_zones: ['astana'],
        name_ru: 'Астана',
        name_en: 'Astana',
        population: 1047966,
        oebs_mvp_id: 'AST',
    },
];

const startDate = getDefaultStartDate();
const endDate = getDefaultEndDate();

const expectRule = (model: SingleRideRuleVM | GoalRuleVM, expectedModel: Partial<SingleRideRuleVM | GoalRuleVM>) => {
    const {start: resultStart, end: resultEnd, $view: resultView, ...otherResultData} = model;
    const {
        start: expectedResultStart,
        end: expectedResultEnd,
        $view: expectedResultView,
        ...otherExpectedReslutData
    } = expectedModel;
    expect(otherResultData).toEqual(otherExpectedReslutData);
};

describe('getCurrentModel', () => {
    it('должна возвращать дефолтную модель', () => {
        const DEFAULT_MODEL = {
            start: {
                time: DEFAULT_TIME,
                date: startDate,
            },
            end: {
                time: DEFAULT_TIME,
                date: endDate,
            },
            offset: 3,
            rule_type: 'single_ride',
            rates: [{}],
            budget: {rolling: true, weekly_validation: true},
            branding_type: BRANDING_VALUES.ANY_BRANDING,
        };
        return expectSaga(getCurrModel, DraftModes.CreateDraft, undefined)
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: GEO_NODES,
                },
            })
            .provide([[call(geoHierarchyApiInstance.request, GEO_HIERARCHY_REQUEST_DATA), []]])
            .run()
            .then(model => {
                expect(model.returnValue).toEqual(DEFAULT_MODEL);
            });
    });

    it('должна возвращать single ride модель при подтягивании драфта single ride субсидии', () => {
        const SINGLE_RIDE_DRAFT: any = {
            id: 141727,
            created_by: 'mikhail-kilin',
            comments: [{login: 'mikhail-kilin', comment: 'mikhail-kilin прикрепил тикет TAXIRATE-53'}],
            created: '2021-03-16T13:12:52+0300',
            updated: '2021-03-16T13:12:52+0300',
            approvals: [],
            status: 'need_approval',
            version: 2,
            run_manually: false,
            service_name: 'billing-subventions-x',
            api_path: 'subventions_x_v2_create',
            data: {
                doc_id: 'd16a8fda-e90e-4846-8153-280854f7368d',
                rule_spec: {
                    rule: {
                        end: '2021-03-20T12:04:00+00:00',
                        tag: 'shooting',
                        rates: [
                            {start: '12:41', week_day: 'tue', bonus_amount: '124'},
                            {start: '21:41', week_day: 'fri', bonus_amount: '0'},
                        ],
                        start: '2021-03-18T12:31:00+00:00',
                        rule_type: 'single_ride',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                    },
                    zones: ['accra'],
                    budget: {daily: '1', weekly: '1', rolling: true, threshold: 2},
                    geoareas: ['15'],
                    tariff_classes: ['business2'],
                },
                old_rule_ids: [],
                created_rules: [
                    {
                        id: '33f83456-1ed6-4757-9625-681528252994',
                        end: '2021-03-20T12:04:00+00:00',
                        tag: 'shooting',
                        zone: 'accra',
                        rates: [
                            {start: '12:41', week_day: 'tue', bonus_amount: '124'},
                            {start: '21:41', week_day: 'fri', bonus_amount: '0'},
                        ],
                        start: '2021-03-18T12:31:00+00:00',
                        geoarea: '15',
                        rule_type: 'single_ride',
                        tariff_class: 'business2',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                    },
                ],
            },
            mode: 'push',
            change_doc_id: 'accra:d16a8fda-e90e-4846-8153-280854f7368d',
            tickets: ['TAXIRATE-53'],
            summary: {},
            errors: [],
            headers: {},
            query_params: {},
            summoned_users: [],
            reapply_allowed_for_failed: false,
            ticket: 'TAXIRATE-53',
            object_id: 'billing-subventions-x:subventions_x_v2_create',
        };
        const TIMEZONE_SETTINGS: Array<TariffSettingsZone> = [
            {
                zone: 'accra',
                tariff_settings: {
                    tariff_settings_id: '5caf05328f8d18512aeb00c5',
                    home_zone: 'accra',
                    is_disabled: false,
                    timezone: 'Africa/Accra',
                    city_id: 'Аккра',
                    country: 'gha',
                    hide_dest_for_driver: false,
                    client_exact_order_round_minutes: 10,
                    client_exact_order_times: [600],
                },
            },
        ];
        const EXPECTED_SINGLE_DIRE_MODEL: SingleRideRuleVM = {
            budget: {daily: '1', weekly: '1', rolling: true, threshold: 2},
            start: {date: moment('2021-03-18T12:31:00.000Z'), time: '12:31'},
            end: {date: moment('2021-03-20T12:04:00.000Z'), time: '12:04'},
            id: '141727',
            rule_type: 'single_ride',
            zone: ['accra'],
            tariff_class: ['business2'],
            activity_points: 1,
            branding_type: 'no_full_branding',
            ticketData: {},
            geoarea: ['15'],
            tag: 'shooting',
            old_rule_ids: [],
            offset: 0,
            $view: {
                start: {date: moment('2021-03-18T12:31:00.000Z'), time: '12:31'},
                end: {date: moment('2021-03-20T12:04:00.000Z'), time: '12:04'},
            },
            currency: 'RUB',
            draft_id: '141727',
            rates: [{bonus_amount: '124', start: '12:41', weekDayStart: 'tue', weekDayEnd: 'fri', end: '21:41'}],
        };
        return expectSaga(getCurrModel, DraftModes.ShowDraft, '141727')
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: GEO_NODES,
                },
            })
            .provide([
                [call(getSmartRuleDraft, '141727'), SINGLE_RIDE_DRAFT],
                [call(tariffsApiInstance.getTariffSettings, 'accra'), TIMEZONE_SETTINGS],
                [call(geoHierarchyApiInstance.request, GEO_HIERARCHY_REQUEST_DATA), []],
            ])
            .run()
            .then(res => {
                expectRule(res.returnValue, EXPECTED_SINGLE_DIRE_MODEL);
            });
    });

    it('должна возвращать single ride модель при подтягивагии single ride правила', () => {
        const API_SINGLE_RIDE = {
            id: '9a097cbb-47f0-49fc-a62e-97fa8997815a',
            start: '2021-03-17T00:00:00+00:00',
            end: '2021-03-19T00:00:00+00:00',
            updated_at: '2021-03-16T12:39:11.802369+00:00',
            tag: 'dasha',
            branding_type: 'sticker_and_lightbox',
            activity_points: 1,
            rates: [
                {week_day: 'tue', start: '12:34', bonus_amount: '1'},
                {week_day: 'fri', start: '12:41', bonus_amount: '0'},
            ],
            budget_id: 'b6a4b28f-2d4c-4306-8d11-a3386e79c03d',
            draft_id: '141803',
            zone: 'accra',
            tariff_class: 'business',
            geoarea: '11_12рпита',
            rule_type: 'single_ride',
        };

        const SUBGMV_BUDGET = {
            id: 'b6a4b28f-2d4c-4306-8d11-a3386e79c03d',
            weekly: false,
            daily: true,
            threshold: '10',
        };

        const EXPECTED_SINGLE_RIDE_MODEL: Partial<SingleRideRuleVM> = {
            budget: {
                weekly: '123',
                threshold: 123,
                rolling: true,
                daily: '1',
                subgmv: SUBGMV_BUDGET.threshold,
                daily_validation: SUBGMV_BUDGET.daily,
                weekly_validation: SUBGMV_BUDGET.weekly,
            },
            start: {date: moment('2021-03-17T00:00:00.000Z'), time: '00:00'},
            end: {date: moment('2021-03-19T00:00:00.000Z'), time: '00:00'},
            id: '9a097cbb-47f0-49fc-a62e-97fa8997815a',
            rule_type: 'single_ride',
            zone: ['accra'],
            tariff_class: ['business'],
            activity_points: 1,
            branding_type: 'sticker_and_lightbox',
            ticketData: {},
            geoarea: ['11_12рпита'],
            tag: 'dasha',
            old_rule_ids: [],
            offset: 0,
            currency: 'RUB',
            $view: {
                start: {date: moment('2021-03-17T00:00:00.000Z'), time: '00:00'},
                end: {date: moment('2021-03-19T00:00:00.000Z'), time: '00:00'},
            },
            draft_id: '141803',
            rates: [{bonus_amount: '1', start: '12:34', weekDayStart: 'tue', weekDayEnd: 'fri', end: '12:41'}],
        };
        const TIMEZONE_SETTINGS: Array<TariffSettingsZone> = [
            {
                zone: 'accra',
                tariff_settings: {
                    tariff_settings_id: '5caf05328f8d18512aeb00c5',
                    home_zone: 'accra',
                    is_disabled: false,
                    timezone: 'Africa/Accra',
                    city_id: 'Аккра',
                    country: 'gha',
                    hide_dest_for_driver: false,
                    client_exact_order_round_minutes: 10,
                    client_exact_order_times: [600],
                },
            },
        ];
        const LIMITS = {
            currency: 'GHS',
            label: 'accra',
            windows: [
                {
                    type: 'tumbling',
                    value: '1.0000',
                    size: 86400,
                    label: 'Дневной',
                    threshold: 200,
                    tumbling_start: '2021-03-17T00:00:00.000000+00:00',
                },
                {type: 'sliding', value: '123.0000', size: 604800, label: '7-дневный', threshold: 123},
            ],
            tickets: ['TAXIRATE-53'],
            ref: 'b6a4b28f-2d4c-4306-8d11-a3386e79c03d',
            approvers: ['mikhail-kilin'],
        };

        return expectSaga(getCurrModel, DraftModes.Show, '123')
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: [],
                },
            })
            .provide([
                [call(smartSubventionsApiInstance.get, '123'), {rule: API_SINGLE_RIDE, budget: SUBGMV_BUDGET}],
                [call(geoHierarchyApiInstance.request, GEO_HIERARCHY_REQUEST_DATA), []],
                [call(tariffsApiInstance.getTariffSettings, 'accra'), TIMEZONE_SETTINGS],
                [call(budgetApiInstance.get, 'b6a4b28f-2d4c-4306-8d11-a3386e79c03d'), LIMITS],
            ])
            .run()
            .then(res => {
                expectRule(res.returnValue, EXPECTED_SINGLE_RIDE_MODEL);
            });
    });

    it('должна возвращать goal модель при подтягивании драфта goal субсидии', () => {
        const GOAL_DRAFT: any = {
            id: 141841,
            created_by: 'mikhail-kilin',
            comments: [{login: 'mikhail-kilin', comment: 'mikhail-kilin прикрепил тикет TAXIRATE-53'}],
            created: '2021-03-16T16:01:38+0300',
            updated: '2021-03-16T16:01:38+0300',
            approvals: [],
            status: 'need_approval',
            version: 2,
            run_manually: false,
            service_name: 'billing-subventions-x',
            api_path: 'subventions_x_v2_create',
            data: {
                doc_id: '45a05e2b-7a74-4e7f-907c-1f0734b191b7',
                rule_spec: {
                    rule: {
                        end: '2021-03-26T18:00:00+00:00',
                        tag: 'reposition_district_extracoms_8',
                        start: '2021-03-16T18:00:00+00:00',
                        window: 1,
                        counters: {
                            steps: [{id: 'A', steps: [{amount: '2', nrides: 1}]}],
                            schedule: [
                                {start: '12:41', counter: 'A', week_day: 'wed'},
                                {start: '12:41', counter: '0', week_day: 'sat'},
                            ],
                        },
                        currency: 'RUB',
                        rule_type: 'goal',
                        branding_type: 'sticker_and_lightbox',
                        activity_points: 1,
                        unique_driver_id: '123',
                    },
                    zones: ['/br_root/br_kazakhstan/br_astana'],
                    budget: {daily: '4', weekly: '2', rolling: true, threshold: 3},
                    geoareas: ['11111'],
                    tariff_classes: ['business'],
                },
                old_rule_ids: [],
                created_rules: [
                    {
                        id: 'bc0c3e78-4a66-44f7-ad61-3567bd571066',
                        end: '2021-03-26T18:00:00+00:00',
                        tag: 'reposition_district_extracoms_8',
                        start: '2021-03-16T18:00:00+00:00',
                        window: 1,
                        geoarea: '11111',
                        geonode: '/br_root/br_kazakhstan/br_astana',
                        counters: {
                            steps: [{id: 'A', steps: [{amount: '2', nrides: 1}]}],
                            schedule: [
                                {start: '12:41', counter: 'A', week_day: 'wed'},
                                {start: '12:41', counter: '0', week_day: 'sat'},
                            ],
                        },
                        currency: 'RUB',
                        rule_type: 'goal',
                        tariff_class: 'business',
                        branding_type: 'sticker_and_lightbox',
                        activity_points: 1,
                        unique_driver_id: '123',
                    },
                ],
            },
            mode: 'push',
            change_doc_id: '/br_root/br_kazakhstan/br_astana:45a05e2b-7a74-4e7f-907c-1f0734b191b7',
            tickets: ['TAXIRATE-53'],
            summary: {},
            errors: [],
            headers: {},
            query_params: {},
            summoned_users: [],
            reapply_allowed_for_failed: false,
            ticket: 'TAXIRATE-53',
            object_id: 'billing-subventions-x:subventions_x_v2_create',
        };

        const EXPECTED_GOAL_MODEL: GoalRuleVM = {
            budget: {daily: '4', weekly: '2', rolling: true, threshold: 3},
            start: {date: moment('2021-03-16T18:00:00.000Z'), time: '21:00'},
            end: {date: moment('2021-03-26T18:00:00.000Z'), time: '21:00'},
            id: '141841',
            rule_type: 'goal',
            zone: ['/br_root/br_kazakhstan/br_astana'],
            tariff_class: ['business'],
            activity_points: 1,
            branding_type: 'sticker_and_lightbox',
            ticketData: {},
            geoarea: ['11111'],
            tag: 'reposition_district_extracoms_8',
            old_rule_ids: [],
            offset: 6,
            $view: {
                start: {date: moment('2021-03-16T18:00:00.000Z'), time: '21:00'},
                end: {date: moment('2021-03-26T18:00:00.000Z'), time: '21:00'},
            },
            draft_id: '141841',
            window: 1,
            currency: 'RUB',
            rates: [{bonus_amount: 'A', start: '12:41', weekDayStart: 'wed', weekDayEnd: 'sat', end: '12:41'}],
            counters: {
                steps: [{id: 'A', steps: [{amount: '2', nrides: 1}]}],
            },
            unique_driver_id: '123',
            goalMode: GoalMode.Common,
        };
        const TIMEZONE_SETTINGS: Array<TariffSettingsZone> = [
            {
                zone: 'astana',
                tariff_settings: {
                    tariff_settings_id: '59030c4018ad17f49565b183',
                    home_zone: 'astana',
                    is_disabled: false,
                    timezone: 'Asia/Omsk',
                    city_id: 'Астана',
                    country: 'kaz',
                    hide_dest_for_driver: true,
                    client_exact_order_round_minutes: 1,
                    client_exact_order_times: [600],
                },
            },
        ];

        return expectSaga(getCurrModel, DraftModes.ShowDraft, '141727')
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: GEO_NODES,
                },
            })
            .provide([
                [call(getSmartRuleDraft, '141727'), GOAL_DRAFT],
                [call(SmartSubventionService.requestGeoNodes), GEO_NODES],
                [call(geoHierarchyApiInstance.request, GEO_HIERARCHY_REQUEST_DATA), []],
                [call(tariffsApiInstance.getTariffSettings, 'astana'), TIMEZONE_SETTINGS],
            ])
            .run()
            .then(res => {
                expectRule(res.returnValue, EXPECTED_GOAL_MODEL);
            });
    });

    it('должна возвращать goal модель при подтягивагии goal правила', () => {
        const API_GOAL_RULE = {
            id: '5ab39d47-0021-4f07-9e64-708010a9eaff',
            tariff_class: 'express',
            geonode: '/br_root/br_kazakhstan/br_astana',
            counters: {
                schedule: [
                    {week_day: 'wed', start: '12:31', counter: 'A'},
                    {week_day: 'sat', start: '12:31', counter: '0'},
                ],
                steps: [{id: 'A', steps: [{nrides: 1, amount: '3'}]}],
            },
            global_counters: [{local: 'A', global: '141961:A'}],
            window: 1,
            currency: 'RUB',
            start: '2021-03-16T18:00:00+00:00',
            end: '2021-03-20T18:00:00+00:00',
            updated_at: '2021-03-16T17:42:31.894644+00:00',
            budget_id: 'bc4e9db6-0987-4e27-9640-60f00d5b685c',
            draft_id: '141961',
            tag: 'kek',
            branding_type: 'no_full_branding',
            activity_points: 1,
            geoarea: '11111',
            unique_driver_id: '1',
            rule_type: 'goal',
        };

        const SUBGMV_BUDGET = {
            id: 'b6a4b28f-2d4c-4306-8d11-a3386e79c03d',
            weekly: false,
            daily: true,
            threshold: '10',
        };

        const TIMEZONE_SETTINGS: Array<TariffSettingsZone> = [
            {
                zone: 'astana',
                tariff_settings: {
                    tariff_settings_id: '59030c4018ad17f49565b183',
                    home_zone: 'astana',
                    is_disabled: false,
                    timezone: 'Asia/Omsk',
                    city_id: 'Астана',
                    country: 'kaz',
                    hide_dest_for_driver: true,
                    client_exact_order_round_minutes: 1,
                    client_exact_order_times: [600],
                },
            },
        ];
        const LIMITS = {
            currency: 'RUB',
            label: '/br_root/br_kazakhstan/br_astana',
            windows: [
                {
                    type: 'tumbling',
                    value: '1.0000',
                    size: 86400,
                    label: 'Дневной',
                    threshold: 200,
                    tumbling_start: '2021-03-16T18:00:00.000000+00:00',
                },
                {type: 'sliding', value: '1.0000', size: 604800, label: '7-дневный', threshold: 2},
            ],
            tickets: ['TAXIRATE-53'],
            ref: 'bc4e9db6-0987-4e27-9640-60f00d5b685c',
            approvers: ['mikhail-kilin'],
        };
        const EXPECTED_GOAL_RULE_MODEL: Partial<GoalRuleVM> = {
            budget: {
                weekly: '1',
                threshold: 2,
                rolling: true,
                daily: '1',
                subgmv: SUBGMV_BUDGET.threshold,
                daily_validation: SUBGMV_BUDGET.daily,
                weekly_validation: SUBGMV_BUDGET.weekly,
            },
            start: {date: moment('2021-03-16T18:00:00.000Z'), time: '00:00'},
            end: {date: moment('2021-03-20T18:00:00.000Z'), time: '00:00'},
            id: '5ab39d47-0021-4f07-9e64-708010a9eaff',
            rule_type: 'goal',
            zone: ['/br_root/br_kazakhstan/br_astana'],
            tariff_class: ['express'],
            activity_points: 1,
            branding_type: 'no_full_branding',
            ticketData: {},
            geoarea: ['11111'],
            tag: 'kek',
            old_rule_ids: [],
            offset: 6,
            $view: {
                start: {date: moment('2021-03-16T18:00:00.000Z'), time: '00:00'},
                end: {date: moment('2021-03-20T18:00:00.000Z'), time: '00:00'},
            },
            draft_id: '141961',
            window: 1,
            currency: 'RUB',
            rates: [{bonus_amount: 'A', start: '12:31', weekDayStart: 'wed', weekDayEnd: 'sat', end: '12:31'}],
            counters: {
                steps: [{id: 'A', steps: [{nrides: 1, amount: '3'}]}],
            },
            unique_driver_id: '1',
        };

        return expectSaga(getCurrModel, DraftModes.Show, '123')
            .withState({
                asyncOperations: {
                    [GEONODES_OPERATION]: GEO_NODES,
                },
            })
            .provide([
                [call(smartSubventionsApiInstance.get, '123'), {rule: API_GOAL_RULE, budget: SUBGMV_BUDGET}],
                [call(SmartSubventionService.requestGeoNodes), GEO_NODES],
                [call(tariffsApiInstance.getTariffSettings, 'astana'), TIMEZONE_SETTINGS],
                [call(budgetApiInstance.get, 'bc4e9db6-0987-4e27-9640-60f00d5b685c'), LIMITS],
            ])
            .run()
            .then(res => {
                expectRule(res.returnValue, EXPECTED_GOAL_RULE_MODEL);
            });
    });
});

describe('getBudget', () => {
    it('При нулевом пороге исчерпания в режиме просмотра должна возвращать "не применимо"', () => {
        const BUDGET = {daily: '4', weekly: '2', rolling: true, threshold: 0};
        const {threshold} = getBudget(BUDGET, DraftModes.Show);
        return expect(threshold).toEqual('smart_subventions.not_applicable');
    });
});
