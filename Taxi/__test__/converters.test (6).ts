import {omit} from 'lodash';
import moment from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {DATE_TIME_FORMAT} from '../../../consts';
import {RuleEnum} from '../../../enums';
import {DoxGetyAnyRule, DoxGetyRule, DoxGetyRuleViewModel} from '../../../types';
import {convertDoXGetYToModel, convertDraftToModel, preCreateDraft, preEditDraft} from '../sagas/converters';

const DRAFT_BEGIN_AT = '2019-01-01';
const DRAFT_END_AT = '2019-01-02';
const DRAFT_MOMENT_BEGIN_AT = moment.utc(DRAFT_BEGIN_AT, DATE_TIME_FORMAT);
const DRAFT_MOMENT_END_AT = moment.utc(DRAFT_END_AT, DATE_TIME_FORMAT);

const TIMEZONE_OFFSET = '+03:00';
const START = '2020-05-27T21:00:00.000000+00:00';
const END = '2020-07-18T21:00:00.000000+00:00';
const MOMENT_BEGIN_AT = moment(START).utcOffset(TIMEZONE_OFFSET);
const MOMENT_END_AT = moment(END).utcOffset(TIMEZONE_OFFSET).subtract(1, 'seconds');

const CASH = 'cash' as const;
const CARD = 'card' as const;

const draftRuleCommonFields = {
    id: 'rule1',
    kind: 'do_x_get_y',
    begin_at: DRAFT_BEGIN_AT,
    end_at: DRAFT_END_AT,
    tariff_classes: ['1', '2'],
    order_payment_type: CASH,
    geoareas: ['3', 'sdg'],
    tags: ['4'],
    activity_points: 123421,
    branding_type: 'full_branding' as TaxiBillingSubventionsDefinitionsYaml.BrandingType,
    days_span: 1,
    budget: {
        id: '1',
        weekly: '123',
    },
    week_days: ['mon', 'tue', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 5, 6, 7, 10, 14, 15],
    trips_bounds: [
        {
            lower_bound: 1123,
            bonus_amount: '1321',
        },
        {
            lower_bound: 2123,
            bonus_amount: '2321',
        },
    ],
};

const rule1: TaxiBillingSubventionsDefinitionsYaml.GoalRule = {
    ...draftRuleCommonFields,
    zone: 'zone1',
    id: 'rule1',
};

const rule2: TaxiBillingSubventionsDefinitionsYaml.GoalRule = {
    ...draftRuleCommonFields,
    zone: 'zone2',
    id: 'rule2',
};

const rule3: TaxiBillingSubventionsDefinitionsYaml.GoalRule = {
    ...draftRuleCommonFields,
    zone: 'zone2',
    id: 'rule3',
};

type OriginAnyRule = TaxiBillingSubventionsSelectRulesYaml.AnyRule;

const commonFields = {
    tariff_zones: ['moscow'],
    status: 'enabled' as OriginAnyRule['status'],
    start: START,
    end: END,
    type: 'add' as OriginAnyRule['type'], // так возвращается субсидия DoXGetY
    is_personal: false,
    taxirate: 'taxirate-53',
    subvention_rule_id: '_id/5ecd3298a11531e403edc220',
    cursor: '2020-07-18T21:00:00.000000+00:00/5ecd3298a11531e403edc220',
    tags: ['testTag'],
    time_zone: {id: 'Europe/Moscow', offset: '+03:00'},
    currency: 'RUB',
    updated: '2020-05-26T15:15:43.678000+00:00',
    visible_to_driver: true,
    week_days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 5],
    log: [
        {
            login: 'russhakirov',
            ticket: 'taxirate-53',
            updated: '2020-05-26T15:15:36.916000+00:00',
            start: '2020-05-27T21:00:00.000000+00:00',
            end: '2020-07-18T21:00:00.000000+00:00',
        },
    ],
    budget: {
        rolling: true,
        id: '86a43cca-0bcf-44b8-92d9-f10a9919e0ed',
        threshold: 100,
        daily: (null as unknown) as string,
        weekly: '1',
    },
    geoareas: ['test'],
    payment_type: 'add' as OriginAnyRule['payment_type'],
    days_span: 1,
    trips_bounds: [{lower_bound: 4, bonus_amount: '50.0'}],
    tariff_classes: ['econom'],
    has_commission: false,
};

const doXGetY1: OriginAnyRule = {
    ...commonFields,
    order_payment_type: null,
};

const doXGetY2: OriginAnyRule = {
    ...commonFields,
    order_payment_type: CASH,
    branding_type: 'no_full_branding',
    min_activity_points: 100,
};

const doXGetY3: OriginAnyRule = {
    ...commonFields,
    order_payment_type: CARD,
    branding_type: 'no_branding',
    min_activity_points: 100,
};

const doXGetY4: OriginAnyRule = {
    ...commonFields,
    order_payment_type: CARD,
    branding_type: 'sticker',
    min_activity_points: 100,
};

function changeType(rule: OriginAnyRule): DoxGetyAnyRule {
    return {...rule, type: 'do_x_get_y'};
}

function makeDraftModel(draft?: Draft): DoxGetyRuleViewModel {
    return {
        $view: {commonFields: {description: 'description'}, draftInfo: draft},
        begin_at: DRAFT_MOMENT_BEGIN_AT,
        end_at: DRAFT_MOMENT_END_AT,
        activity_points: 123421,
        branding_type: 'full_branding',
        budget: {id: '1', weekly: '123'},
        days_span: 1,
        geoareas: ['3', 'sdg'],
        id: '631',
        kind: RuleEnum.DoxGety,
        order_payment_type: CASH,
        trips_bounds: [
            {
                lower_bound: 1123,
                bonus_amount: '1321',
            },
            {
                lower_bound: 2123,
                bonus_amount: '2321',
            },
        ],
        hours: '1,5-7,10,14-15',
        week_days: [1, 2, 7],
        tag: '4',
        tariff_classes: ['1', '2'],
        zones: ['zone1', 'zone2'],
    };
}

function omitIds(data: any) {
    return data?.rules?.map((rule: any) => {
        const {id, ...otherRuleProps} = rule;
        const budget = rule.budget;
        return {...omit(otherRuleProps, 'budget'), budget: omit(budget, 'id')};
    });
}

const draftCommonFields = {
    id: 631,
    status: DraftStatusEnum.NeedApproval,
    description: 'description',
};

describe('DoXGetY converters', () => {
    test('convertDraftToModel', () => {
        const draft: Draft<{rules: Array<DoxGetyRule>}> = {
            ...draftCommonFields,
            data: {
                rules: [rule1, rule2, rule3] as Array<DoxGetyRule>,
            },
        };

        const convertedDraft = convertDraftToModel(draft);
        const convertedDraftCopy = convertDraftToModel(draft, true);
        const draftModel = makeDraftModel(draft);
        const draftModelCopy = makeDraftModel();
        expect(convertedDraft).toEqual(draftModel);
        expect(convertedDraftCopy).toEqual(draftModelCopy);
    });

    test('convertDoXGetYToModel', () => {
        const convertedDoXGetY1 = convertDoXGetYToModel(changeType(doXGetY1));
        const convertedDoXGetY2 = convertDoXGetYToModel(changeType(doXGetY2));
        const convertedDoXGetY3 = convertDoXGetYToModel(changeType(doXGetY3));
        const convertedDoXGetY4 = convertDoXGetYToModel(changeType(doXGetY4));

        const commonModelFields = {
            $view: {},
            id: '_id/5ecd3298a11531e403edc220',
            geoareas: ['test'],
            tariff_classes: ['econom'],
            begin_at: MOMENT_BEGIN_AT,
            end_at: MOMENT_END_AT,
            taxirate: 'taxirate-53',
            tag: 'testTag',
            hours: '1-3,5',
            days_span: 1,
            budget: {
                daily: (null as unknown) as string,
                id: '86a43cca-0bcf-44b8-92d9-f10a9919e0ed',
                rolling: true,
                threshold: 100,
                weekly: '1',
            },

            trips_bounds: [{bonus_amount: '50.0', lower_bound: 4}],
            week_days: [1, 2, 3, 4, 5, 6] as number[],
            zones: ['moscow'],
        };
        const model1: DoxGetyRuleViewModel = {
            ...commonModelFields,
            kind: RuleEnum.DoxGety,
            order_payment_type: (null as unknown) as undefined,
            branding_type: undefined,
            activity_points: undefined,
        };
        const model2: DoxGetyRuleViewModel = {
            ...commonModelFields,
            kind: RuleEnum.DoxGety,
            order_payment_type: CASH,
            branding_type: undefined,
            activity_points: 100,
        };
        const model3: DoxGetyRuleViewModel = {
            ...commonModelFields,
            kind: RuleEnum.DoxGety,
            order_payment_type: CARD,
            branding_type: undefined,
            activity_points: 100,
        };
        const model4: DoxGetyRuleViewModel = {
            ...commonModelFields,
            kind: RuleEnum.DoxGety,
            order_payment_type: CARD,
            branding_type: 'sticker',
            activity_points: 100,
        };

        expect(convertedDoXGetY1).toEqual(model1);
        expect(convertedDoXGetY2).toEqual(model2);
        expect(convertedDoXGetY3).toEqual(model3);
        expect(convertedDoXGetY4).toEqual(model4);
    });

    test('preCreateDraft', () => {
        const draft: Draft<{rules: Array<DoxGetyRule>}> = {
            ...draftCommonFields,
            data: {
                rules: [rule1, rule2] as Array<DoxGetyRule>,
            },
        };
        const draftModel = makeDraftModel(draft);
        const draftModelCopy = makeDraftModel();
        const preparedDraft = preCreateDraft(100, draftModel);
        const preparedCopyDraft = preCreateDraft(100, draftModelCopy);

        expect(omitIds(preparedDraft.data)).toEqual(omitIds(draft.data));
        expect(omitIds(preparedCopyDraft.data)).toEqual(omitIds(draft.data));
    });

    test('preEditDraft', () => {
        const draft: Draft<{rules: Array<DoxGetyRule>}> = {
            ...draftCommonFields,
            data: {
                rules: [rule1, rule2] as Array<DoxGetyRule>,
            },
        };
        const draftModel = makeDraftModel(draft);
        const preparedDraft = preEditDraft(100, draftModel);

        expect(omitIds(preparedDraft.data)).toEqual(omitIds(draft.data));
    });
});
