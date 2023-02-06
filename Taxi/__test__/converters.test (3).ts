import moment from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {DATE_TIME_FORMAT, TIME_FORMAT} from '../../../consts';
import {RuleEnum} from '../../../enums';
import {
    BrandingType,
    SingleOrderRule,
    SingleOrderRules,
    SingleOrderViewModel,
} from '../../../types';
import {convertDraftToModel, convertGuaranteeToModel, preCreate, preUpdateDraft} from '../sagas/converters';

function omitIds(data: any) {
    return data.rules?.map(({id, budget: {id: budgetId, ...budget}, ...rule}: {id: any; budget: any}) => ({
        ...rule,
        budget,
    }));
}

const draftCommonFields = {
    id: 631,
    status: DraftStatusEnum.NeedApproval,
    description: 'description',
};

const DRAFT_BEGIN_AT = '2020-06-27T01:00:00';
const DRAFT_END_AT = '2020-06-30T00:00:00';
const CONVERTED_DRAFT_BEGIN_AT = moment(DRAFT_BEGIN_AT);
const CONVERTED_DRAFT_START_TIME = moment.utc(DRAFT_BEGIN_AT, DATE_TIME_FORMAT).format(TIME_FORMAT);
const CONVERTED_DRAFT_END_AT = moment.utc(DRAFT_END_AT, DATE_TIME_FORMAT);
const CONVERTED_DRAFT_END_TIME = CONVERTED_DRAFT_END_AT.format(TIME_FORMAT);

const draftRuleCommonFields = {
    budget: {
        id: '960d74aa-29ed-4ffa-b4f8-3a7dd223ea57',
        daily: '670',
        weekly: '4000',
        rolling: true,
        threshold: 100
    },
    begin_at: DRAFT_BEGIN_AT,
    end_at: DRAFT_END_AT,
    is_additive: false,
    has_commission: true,
    tariff_classes: ['econom'],
    visible_to_driver: true,
    order_payment_type: 'card' as const
};

const rule1: SingleOrderRule = {
    ...draftRuleCommonFields,
    kind: RuleEnum.SingleOrder,
    payment_type: 'guarantee' as const,
    tags: ['rule1Tag'],
    bonus_amount: '500',
    week_days: [] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 4, 5, 6, 7],
    geoareas: ['geoarea1', 'geoarea2'],
    zone: 'zone1',
    id: 'rule1',
};

const convertedRule1 = {
    geoareas: ['geoarea1', 'geoarea2'],
    hours: '1-7',
    tags: 'rule1Tag',
    bonus_amount: 500,
    week_days: [] as number[],
};

const rule2: SingleOrderRule = {
    ...draftRuleCommonFields,
    kind: RuleEnum.SingleOrder,
    payment_type: 'guarantee' as const,
    tags: ['rule2Tag'],
    bonus_amount: '600',
    week_days: ['mon', 'tue', 'wed', 'fri', 'sat', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 5, 6, 7],
    geoareas: [],
    zone: 'zone1',
    id: 'rule2',
};

const convertedRule2 = {
    geoareas: [] as string[],
    hours: '1-3,5-7',
    tags: 'rule2Tag',
    bonus_amount: 600,
    week_days: [1, 2, 3, 5, 6, 7],
};

const rule3: TaxiBillingSubventionsDefinitionsYaml.SingleOrderRule = {
    ...rule1,
    zone: 'zone2',
};

const rule4: TaxiBillingSubventionsDefinitionsYaml.SingleOrderRule = {
    ...rule2,
    zone: 'zone2',
};

const addRule = {
    ...draftRuleCommonFields,
    kind: RuleEnum.SingleOrder,
    branding_type: 'sticker',
    days_span: 1,
    trips_lower_bound: 12,
    activity_points: 2,
    payment_type: 'add',
    tags: ['rule2Tag'],
    bonus_amount: '600',
    week_days: ['mon', 'tue', 'wed', 'fri', 'sat', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 5, 6, 7],
    geoareas: ['geoarea1'],
    zone: 'zone1',
    id: 'rule2',
};

const convertedAddRule = {
    geoareas: ['geoarea1'],
    hours: '1-3,5-7',
    tags: 'rule2Tag',
    bonus_amount: 600,
    week_days: [1, 2, 3, 5, 6, 7],
};

type TypeFields = {
    payment_type: 'add' | 'guarantee';
    zones: Array<string>,
    trips_lower_bound?: number;
    days_span?: number;
    branding_type?: BrandingType;
    activity_points?: number;
};

function makeDraftModel(
    convertedRules: Array<SingleOrderRules>,
    typeFields: TypeFields,
    draft?: Draft
): SingleOrderViewModel {
    return {
        ...typeFields,
        $view: {commonFields: {description: 'description'}, draftInfo: draft},
        begin_at: CONVERTED_DRAFT_BEGIN_AT,
        start_time: CONVERTED_DRAFT_START_TIME,
        end_at: CONVERTED_DRAFT_END_AT,
        end_time: CONVERTED_DRAFT_END_TIME,
        budget: {
            id: '960d74aa-29ed-4ffa-b4f8-3a7dd223ea57',
            daily: '670',
            weekly: '4000',
            rolling: true,
            threshold: 100
        },
        tariff_classes: ['econom'],
        has_commission: true,
        is_additive: false,
        visible_to_driver: true,
        order_payment_type: 'card' as const,
        rules: convertedRules,
    };
}

const TIMEZONE_OFFSET = '+03:00';
const START = '2020-06-26T22:00:00.000000+00:00';
const END = '2020-06-29T21:00:00.000000+00:00';
const MOMENT_START = moment(START).utcOffset(TIMEZONE_OFFSET);
const MOMENT_END = moment(END).utcOffset(TIMEZONE_OFFSET);

const commonFields = {
    tariff_zones: ['moscow'],
    status: 'enabled' as const,
    start: '2020-06-26T22:00:00.000000+00:00',
    end: '2020-06-29T21:00:00.000000+00:00',
    type: 'guarantee' as const,
    is_personal: false,
    taxirate: 'taxirate-53',
    subvention_rule_id: '_id/5ef5ed708f93716a1223d857',
    cursor: '2020-06-29T21:00:00.000000+00:00/5ef5ed708f93716a1223d857',
    tags: ['test1'],
    time_zone: {id: 'Europe/Moscow', offset: '+03:00'},
    currency: 'RUB',
    updated: '2020-06-26T12:46:14.371000+00:00',
    visible_to_driver: true,
    order_payment_type: 'card' as const,
    week_days: ['mon', 'tue', 'wed', 'fri', 'sat', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [1, 2, 3, 5, 6, 7],
    log: [{
        login: 'russhakirov',
        ticket: 'taxirate-53',
        updated: '2020-06-26T12:43:28.613000+00:00',
        start: '2020-06-26T22:00:00.000000+00:00',
        end: '2020-06-29T21:00:00.000000+00:00'
    }],
    budget: {
        rolling: true,
        threshold: 100,
        daily: '670',
        id: '095be21d-f88f-48c9-934a-93016df3a8a6',
        weekly: '4000'
    },
    geoareas: ['Jerusalem-Test'],
    tariff_classes: ['econom', 'express'],
    has_commission: true,
    bonus_amount: '700.0',
};

const guarantee = {
    ...commonFields,
    payment_type: 'guarantee' as const,
};

const add = {
    ...commonFields,
    payment_type: 'add' as const,
    days_span: 1,
    branding_type: 'sticker' as const,
    min_activity_points: 2,
    trips_lower_bound: 12,
};

type AddOrGuaranteeDraft = Draft<{
    rules: Array<SingleOrderRule>
}>;

function makeModel(typeFields: TypeFields): SingleOrderViewModel {
    return {
        ...typeFields,
        $view: {},
        rules: [
            {
                bonus_amount: 700,
                week_days: [1, 2, 3, 5, 6, 7],
                hours: '1-3,5-7',
                geoareas: ['Jerusalem-Test'],
                tags: 'test1'
            }
        ],
        payment_type: 'guarantee' as const,
        order_payment_type: 'card' as const,
        tariff_classes: ['econom', 'express'],
        has_commission: true,
        visible_to_driver: true,
        trips_lower_bound: undefined,
        is_additive: false,
        budget: {
            id: '095be21d-f88f-48c9-934a-93016df3a8a6',
            daily: '670',
            weekly: '4000',
            rolling: true,
            threshold: 100
        },
        begin_at: MOMENT_START,
        start_time: '01:00',
        end_at: MOMENT_END,
        end_time: '00:00',
    };
}

const guaranteeDraft: AddOrGuaranteeDraft = {
    ...draftCommonFields,
    data: {
        rules: [rule1, rule2, rule3, rule4] as Array<SingleOrderRule>
    }
};

const addDraft: AddOrGuaranteeDraft = {
    ...draftCommonFields,
    data: {
        rules: [addRule] as Array<SingleOrderRule>
    }
};

const guaranteeDraftModel = makeDraftModel(
    [convertedRule1, convertedRule2],
    {
        payment_type: 'guarantee' as const,
        zones: ['zone1', 'zone2'],
    },
    guaranteeDraft);
const addDraftModel = makeDraftModel(
    [convertedAddRule],
    {
        payment_type: 'add' as const,
        trips_lower_bound: 12,
        days_span: 1,
        branding_type: 'sticker',
        activity_points: 2,
        zones: ['zone1'],
    },
    addDraft
);

describe('AddOrGuarantee converters', () => {
    test('convertDraftToModel', () => {
        const guaranteeDraft: AddOrGuaranteeDraft = {
            ...draftCommonFields,
            data: {
                rules: [rule1, rule2, rule3, rule4] as Array<SingleOrderRule>
            }
        };

        const addDraft: AddOrGuaranteeDraft = {
            ...draftCommonFields,
            data: {
                rules: [addRule] as Array<SingleOrderRule>
            }
        };

        const convertedGuaranteeDraft = convertDraftToModel(guaranteeDraft);
        const convertedAddDraft = convertDraftToModel(addDraft);
        const guaranteeDraftModel = makeDraftModel(
            [convertedRule1, convertedRule2],
            {
                payment_type: 'guarantee' as const,
                zones: ['zone1', 'zone2'],
            },
            guaranteeDraft);
        const addDraftModel = makeDraftModel(
            [convertedAddRule],
            {
                payment_type: 'add' as const,
                trips_lower_bound: 12,
                days_span: 1,
                branding_type: 'sticker',
                activity_points: 2,
                zones: ['zone1'],
            },
            addDraft
        );
        expect(convertedGuaranteeDraft).toEqual(guaranteeDraftModel);
        expect(convertedAddDraft).toEqual(addDraftModel);
    });

    test('convertGuaranteeToModel', () => {
        const convertedGuarantee = convertGuaranteeToModel(guarantee);
        const convertedAdd = convertGuaranteeToModel(add);
        const guaranteeModel = makeModel({
            zones: ['moscow'],
            payment_type: 'guarantee' as const,
            branding_type: undefined,
            days_span: undefined,
        });
        const addModel = makeModel({
            zones: ['moscow'],
            payment_type: 'add' as const,
            days_span: 1,
            branding_type: 'sticker',
            activity_points: 2,
            trips_lower_bound: 12,
        });
        expect(convertedGuarantee).toEqual(guaranteeModel);
        expect(convertedAdd).toEqual(addModel);
    });

    test('preCreate', () => {
        const preparedGuaranteeDraft = preCreate(guaranteeDraftModel, 100);
        const preparedAddDraft = preCreate(addDraftModel, 100);

        expect(omitIds(preparedGuaranteeDraft.data)).toEqual(omitIds(guaranteeDraft.data));
        expect(omitIds(preparedAddDraft.data)).toEqual(omitIds(addDraft.data));
    });

    test('preUpdateDraft', () => {
        const preparedGuaranteeDraft = preUpdateDraft(guaranteeDraftModel, 100);
        const preparedAddDraft = preUpdateDraft(addDraftModel, 100);

        expect(omitIds(preparedGuaranteeDraft.data)).toEqual(omitIds(guaranteeDraft.data));
        expect(omitIds(preparedAddDraft.data)).toEqual(omitIds(addDraft.data));
    });
});
