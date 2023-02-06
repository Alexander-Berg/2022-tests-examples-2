import moment from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {DATE_FORMAT} from '../../../consts';
import {BrandingType, Budget, DailyGuaranteeDraft, DailyGuaranteeDraftViewModel} from '../../../types';
import {convertDraftToModel, convertGuaranteeToModel, prepareDailyGuarantiesBudget, preSave} from '../sagas/converters';

function omitIds(data: any) {
    return data.rules?.map(({id, budget: {id: budgetId, ...budget}, ...rule}: {id: any; budget: any}) => ({
        ...rule,
        budget,
    }));
}

function makeDraftModel(
    draft: Draft<DailyGuaranteeDraft>,
    rulesData: {steps_csv: Array<Array<string | number>>; branding_type: BrandingType}[],
): DailyGuaranteeDraftViewModel {
    return {
        $view: {
            commonFields: {
                description: 'description',
            },
            draftInfo: draft,
        },
        start: DRAFT_MOMENT_START_DATE_2020_06_19,
        end: DRAFT_MOMENT_END_DATE_2020_07_25,
        week_days: [1, 2, 3, 4, 6, 7],
        budget: {
            id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
            daily: '500',
            weekly: '5000',
            rolling: true,
            threshold: 100,
        },
        has_commission: true,
        zone: 'moscow',
        tags: 'some_tag',
        tariff_classes: ['econom', 'business'],
        hours: '0-23',
        driver_points: 10,
        is_net: false,
        rules: rulesData,
    };
}

const draftCommonFields = {
    id: 631,
    status: DraftStatusEnum.NeedApproval,
    description: 'description',
};

const DRAFT_START_DATE_2020_06_19 = '2020-06-19';
const DRAFT_MOMENT_START_DATE_2020_06_19 = moment(DRAFT_START_DATE_2020_06_19, DATE_FORMAT);
const DRAFT_END_DATE_2020_07_25 = '2020-07-25';
const DRAFT_MOMENT_END_DATE_2020_07_25 = moment(DRAFT_END_DATE_2020_07_25, DATE_FORMAT);

const draftRuleCommonFields = {
    kind: 'daily_guarantee',
    tags: ['some_tag'],
    zone: 'moscow',
    hours: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    budget: {
        id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
        daily: '500',
        weekly: '5000',
        rolling: true,
        threshold: 100,
    },
    is_net: false,
    begin_at: DRAFT_START_DATE_2020_06_19,
    end_at: DRAFT_END_DATE_2020_07_25,
    week_days: ['mon', 'tue', 'wed', 'thu', 'sat', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    has_commission: true,
    tariff_classes: ['econom', 'business'],
    activity_points: 10,
};

const TIMEZONE_OFFSET = '+03:00';
const START = '2020-05-27T21:00:00.000000+00:00';
const END = '2020-07-18T21:00:00.000000+00:00';
const MOMENT_START = moment(START).utcOffset(TIMEZONE_OFFSET);
const MOMENT_END = moment(END).utcOffset(TIMEZONE_OFFSET);

const guarantee = {
    tariff_zones: ['moscow'],
    status: 'enabled' as const,
    start: START,
    end: END,
    type: 'daily_guarantee' as const,
    is_personal: false,
    taxirate: 'taxirate-53',
    subvention_rule_id: 'group_id/0e49b977-738b-47ae-b00e-34130378eea0',
    cursor: '2021-06-12T21:00:00.000000+00:00/5ee297408f93716a12e40e4d',
    tags: ['some_tag'],
    time_zone: {id: 'Europe/Moscow', offset: '+03:00'},
    currency: 'RUB',
    updated: '2020-06-12T08:49:29.155000+00:00',
    visible_to_driver: true,
    order_payment_type: (null as unknown) as string,
    week_days: ['mon', 'tue', 'wed', 'fri', 'sat', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 4, 5],
    log: [
        {
            login: 'russhakirov',
            ticket: 'taxirate-53',
            updated: '2020-06-11T20:42:40.555000+00:00',
            start: '2020-06-19T21:00:00.000000+00:00',
            end: '2021-06-12T21:00:00.000000+00:00',
        },
    ],
    budget: {
        threshold: 100,
        daily: '500',
        weekly: '5000',
        id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
        rolling: true,
    },
    driver_points: 10,
    geoareas: [] as string[],
    min_activity_points: 10,
    payment_type: 'guarantee' as const,
    days_span: 1,
    trips_bounds: [
        {lower_bound: 1, bonus_amount: '400.0', upper_bound: 1},
        {lower_bound: 2, bonus_amount: '600.0', upper_bound: 2},
        {lower_bound: 3, bonus_amount: '800.0', upper_bound: 3},
        {lower_bound: 4, bonus_amount: '1000.0', upper_bound: 4},
    ],
    is_net: false,
    is_test: false,
    branding_type: 'sticker' as const,
    tariff_classes: ['econom', 'business'],
    has_commission: true,
    steps: [
        {bonus: 400, orders_count: 1},
        {bonus: 600, orders_count: 2},
        {bonus: 800, orders_count: 3},
        {bonus: 1000, orders_count: 4},
    ],
    taximeter_daily_guarantee_tag: 'variator' as const,
};

const rule1 = {
    steps: [
        [1, '400'],
        [2, '600'],
        [3, '800'],
        [4, '1000'],
    ],
    branding_types: ['sticker'] as BrandingType[],
};

const rule2 = {
    steps: [
        [1, '3'],
        [2, '6'],
        [3, '9'],
        [4, '12'],
        [5, '15'],
    ],
    branding_types: ['no_branding'] as BrandingType[],
};

const convertedRules = [rule1, rule2].map(rule => ({
    steps_csv: rule.steps,
    branding_type: rule.branding_types?.[0],
}));

describe('BookingGuarantee converters', () => {
    test('convertDraftToModel', () => {
        const expectedModelBudget: Budget = {
            daily: '500',
            id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
            rolling: true,
            threshold: 100,
            weekly: '5,000',
        };

        const incomingDraft: Draft<DailyGuaranteeDraft> = {
            ...draftCommonFields,
            data: {
                rules: [
                    {
                        ...draftRuleCommonFields,
                        ...rule1,
                        id: '0e49b977-738b-47ae-b00e-34130378eea0',
                    },
                    {
                        ...draftRuleCommonFields,
                        ...rule2,
                        id: 'ab1ffd5a-4f7c-4e59-9680-fb5556e95038',
                    },
                ],
            },
        };

        const convertedDraft = convertDraftToModel(incomingDraft);
        const draftModel = makeDraftModel(incomingDraft, convertedRules);
        const expectedDraft = {
            ...draftModel,
            budget: expectedModelBudget,
        };
        expect(convertedDraft).toEqual(expectedDraft);
    });

    test('convertGuaranteeToModel', () => {
        const convertedGuarantee = convertGuaranteeToModel(guarantee);

        const model: DailyGuaranteeDraftViewModel = {
            $view: {},
            zone: 'moscow',
            start: MOMENT_START,
            end: MOMENT_END,
            subvention_rule_id: 'group_id/0e49b977-738b-47ae-b00e-34130378eea0',
            tags: 'some_tag',
            week_days: [1, 2, 3, 5, 6, 7],
            hours: '1-5',
            budget: {
                threshold: 100,
                daily: '500',
                weekly: '5000',
                id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
                rolling: true,
            },
            driver_points: 10,
            min_activity_points: 10,
            is_net: false,
            is_test: false,
            tariff_classes: ['econom', 'business'],
            has_commission: true,
            rules: [
                {
                    branding_type: 'sticker',
                    steps_csv: [
                        [1, '400'],
                        [2, '600'],
                        [3, '800'],
                        [4, '1000'],
                    ],
                },
            ],
        };

        expect(convertedGuarantee).toEqual(model);
    });

    test('preSave', () => {
        const draft: Draft<DailyGuaranteeDraft> = {
            ...draftCommonFields,
            data: {
                rules: [
                    {
                        ...draftRuleCommonFields,
                        ...rule1,
                        id: '0e49b977-738b-47ae-b00e-34130378eea0',
                    },
                    {
                        ...draftRuleCommonFields,
                        ...rule2,
                        id: 'ab1ffd5a-4f7c-4e59-9680-fb5556e95038',
                    },
                ],
            },
        };
        const draftModel = makeDraftModel(draft, convertedRules);
        const preparedDraft = preSave(100, draftModel);
        expect(omitIds(preparedDraft.data)).toEqual(omitIds(draft.data));
    });

    test('prepareDailyGuarantiesBudget', () => {
        const budget = draftRuleCommonFields.budget;
        const gmv = 0.1;
        const expectedBudgetModel = {
            gmv: 0.1,
            id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
            daily: '500',
            weekly: '5,000',
            rolling: true,
            threshold: 100,
        };

        expect(prepareDailyGuarantiesBudget(budget, gmv)).toEqual(expectedBudgetModel);
    });

    test('prepareDailyGuarantiesBudget, no gmv', () => {
        const budget = draftRuleCommonFields.budget;
        const expectedBudgetModel = {
            id: 'f75e1d1b-de21-4d5c-8e02-e0d1fc2c4e01',
            daily: '500',
            weekly: '5,000',
            rolling: true,
            threshold: 100,
        };

        expect(prepareDailyGuarantiesBudget(budget)).toEqual(expectedBudgetModel);
    });
});
