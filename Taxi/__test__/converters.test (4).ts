import moment from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {BookingRate, DATE_FORMAT} from '../../../consts';
import {PaymentValue} from '../../../enums';
import {BookingRule, GeoBookingDraft, GeoBookingGuaranteeDraftViewModel} from '../../../types';
import {convertBookingGuaranteeToModel, convertDraftToModel, preSave} from '../sagas/converters';

function omitIds(data: any) {
    return data.rules?.map(({id, budget: {id: budgetId, ...budget}, ...rule}: {id: any; budget: any}) => ({
        ...rule,
        budget,
    }));
}

function makeDraftModel(
    draft: Draft<GeoBookingDraft>,
    paymentMethod: BookingRate,
    ticket: string = '',
): GeoBookingGuaranteeDraftViewModel {
    return {
        $view: {
            commonFields: {
                description: 'description',
                ticket,
            },
            draftInfo: draft,
            paymentMethod,
        },
        start: DRAFT_MOMENT_START_DATE_2020_06_19,
        end: DRAFT_MOMENT_END_DATE_2020_07_25,
        budget: {
            id: '0b6459c4-171f-46c7-b8cf-6b36d52f7c47',
            daily: '10',
            weekly: '10000',
            rolling: true,
            threshold: 100,
        },
        geoarea: 'north-butovo-1',
        payment_type: 'guarantee' as const,
        has_commission: false,
        tariff_classes: ['econom', 'vip'],
        min_activity_points: 95,
        is_relaxed_income_matching: false,
        is_relaxed_order_time_matching: false,
        profile_payment_type_restrictions: PaymentValue.Cash,
        rules: [
            {
                week_days: [1, 2, 3, 4, 5, 6, 7],
                workshift: {end: '23:00', start: '10:00'},
                min_online_minutes: 3,
                rate_free_per_minute: '11',
            },
            {
                week_days: [1, 3, 4, 6, 7],
                workshift: {end: '22:00', start: '11:00'},
                min_online_minutes: 2,
                rate_free_per_minute: '10',
            },
        ],
        tags: 'driver_fix_20191225',
        zone: 'mozhaysk',
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
    kind: 'geo_booking',
    tags: ['driver_fix_20191225'],
    zone: 'mozhaysk',
    end_at: DRAFT_END_DATE_2020_07_25,
    begin_at: DRAFT_START_DATE_2020_06_19,
    budget: {
        id: '0b6459c4-171f-46c7-b8cf-6b36d52f7c47',
        daily: '10',
        weekly: '10000',
        rolling: true,
        threshold: 100,
    },
    ticket: 'taxirate-53',
    geoarea: 'north-butovo-1',
    payment_type: 'guarantee' as const,
    has_commission: false,
    tariff_classes: ['econom', 'vip'],
    min_activity_points: 95,
    is_relaxed_income_matching: false,
    is_relaxed_order_time_matching: false,
    profile_payment_type_restrictions: PaymentValue.Cash,
};

const TIMEZONE_OFFSET = '+03:00';
const START = '2020-05-27T21:00:00.000000+00:00';
const END = '2020-07-18T21:00:00.000000+00:00';
const MOMENT_START = moment(START).utcOffset(TIMEZONE_OFFSET);
const MOMENT_END = moment(END).utcOffset(TIMEZONE_OFFSET).subtract(1, 'd');

const commonFields = {
    tariff_zones: ['moscow'],
    status: 'enabled' as const,
    start: START,
    end: END,
    type: 'geo_booking' as const,
    is_personal: false,
    taxirate: 'taxirate-53',
    subvention_rule_id: '_id/5edfad53e80ad0da1e9fd82f',
    cursor: '2020-07-06T21:00:00.000000+00:00/5edfad53e80ad0da1e9fd82f',
    tags: ['driver_fix_20191225'],
    time_zone: {id: 'Europe/Moscow', offset: TIMEZONE_OFFSET},
    currency: 'RUB',
    updated: '2020-06-09T15:40:19.482000+00:00',
    visible_to_driver: true,
    order_payment_type: 'card',
    week_days: ['mon', 'sun'] as TaxiBillingSubventionsDefinitionsYaml.WeekDays,
    hours: [] as number[],
    log: [
        {
            login: 'russhakirov',
            ticket: 'taxirate-53',
            updated: '2020-06-09T15:40:03.804000+00:00',
            start: '2020-06-10T21:00:00.000000+00:00',
            end: '2020-07-06T21:00:00.000000+00:00',
        },
    ],
    budget: {
        daily: (null as unknown) as string,
        weekly: '10000',
        threshold: 100,
        id: '7e31c935-a8d6-45ff-a848-bd3f6b292e5d',
        rolling: false,
    },
    driver_points: 95,
    geoareas: ['north-butovo-1'],
    min_activity_points: 95,
    payment_type: 'guarantee' as const,
    tariff_classes: ['econom'],
    has_commission: false,
    workshift: {start: '10:00', end: '23:00'},
    min_online_minutes: 3,
    profile_payment_type_restrictions: PaymentValue.Cash,
    is_relaxed_order_time_matching: false,
    is_relaxed_income_matching: false,
    rate_free_per_minute: '11',
};

const guarantee1: BookingRule = {
    ...commonFields,
    rate_on_order_per_minute: '11',
};

const guarantee2: BookingRule = {
    ...commonFields,
    rate_on_order_per_minute: '12',
};

function makeModel(
    guarantee: BookingRule,
    paymentMethod: BookingRate,
    rate_on_order_per_minute: string,
): GeoBookingGuaranteeDraftViewModel {
    return {
        $view: {
            paymentMethod,
            commonFields: {
                ticket: '',
            },
        },
        start: MOMENT_START,
        end: MOMENT_END,
        geoarea: 'north-butovo-1',
        tags: 'driver_fix_20191225',
        zone: 'moscow',
        profile_payment_type_restrictions: PaymentValue.Cash,
        budget: {
            daily: (null as unknown) as string,
            weekly: '10000',
            threshold: 100,
            id: '7e31c935-a8d6-45ff-a848-bd3f6b292e5d',
            rolling: false,
        },
        min_activity_points: 95,
        payment_type: 'guarantee' as const,
        tariff_classes: ['econom'],
        has_commission: false,
        is_relaxed_order_time_matching: false,
        is_relaxed_income_matching: false,
        rate_on_order_per_minute,
        rules: [
            {
                min_online_minutes: 3,
                week_days: [1, 7],
                workshift: {start: '10:00', end: '23:00'},
                rate_free_per_minute: '11',
            },
        ],
    };
}

describe('BookingGuarantee converters', () => {
    test('convertDraftToModel', () => {
        const draftOnOrder: Draft<GeoBookingDraft> = {
            ...draftCommonFields,
            data: {
                rules: [
                    {
                        ...draftRuleCommonFields,
                        id: 'f32c07a0-2a92-4484-8fd6-45c975f42b67',
                        week_days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                        workshift: {end: '23:00', start: '10:00'},
                        min_online_minutes: 3,
                        rate_free_per_minute: '11',
                        rate_on_order_per_minute: '11',
                    },
                    {
                        ...draftRuleCommonFields,
                        id: '44bf97bf-40ea-4aa1-84e4-5c2c6524304f',
                        week_days: ['mon', 'wed', 'thu', 'sat', 'sun'],
                        workshift: {end: '22:00', start: '11:00'},
                        min_online_minutes: 2,
                        rate_free_per_minute: '10',
                        rate_on_order_per_minute: '10',
                    },
                ],
            },
        };

        const draftOnFree: Draft<GeoBookingDraft> = {
            ...draftCommonFields,
            data: {
                rules: [
                    {
                        ...draftRuleCommonFields,
                        id: 'f32c07a0-2a92-4484-8fd6-45c975f42b67',
                        week_days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                        workshift: {end: '23:00', start: '10:00'},
                        min_online_minutes: 3,
                        rate_free_per_minute: '11',
                    },
                    {
                        ...draftRuleCommonFields,
                        id: '44bf97bf-40ea-4aa1-84e4-5c2c6524304f',
                        week_days: ['mon', 'wed', 'thu', 'sat', 'sun'],
                        workshift: {end: '22:00', start: '11:00'},
                        min_online_minutes: 2,
                        rate_free_per_minute: '10',
                    },
                ],
            },
        };

        const convertedOnOrderDraft = convertDraftToModel(draftOnOrder);
        const convertedOnFreeDraft = convertDraftToModel(draftOnFree);
        const draftModelOnOrder = makeDraftModel(draftOnOrder, BookingRate.OnOrder);
        const draftModelOnFree = makeDraftModel(draftOnFree, BookingRate.Free);
        expect(convertedOnOrderDraft).toEqual(draftModelOnOrder);
        expect(convertedOnFreeDraft).toEqual(draftModelOnFree);
    });

    test('convertBookingGuaranteeToModel', () => {
        const convertedGuarantee1 = convertBookingGuaranteeToModel(guarantee1);
        const convertedGuarantee2 = convertBookingGuaranteeToModel(guarantee2);
        const modelOnOrder = makeModel(guarantee1, BookingRate.OnOrder, '11');
        const modelFree = makeModel(guarantee2, BookingRate.Free, '12');
        expect(convertedGuarantee1).toEqual(modelOnOrder);
        expect(convertedGuarantee2).toEqual(modelFree);
    });

    test('preSave', () => {
        const draft: Draft<GeoBookingDraft> = {
            ...draftCommonFields,
            data: {
                rules: [
                    {
                        ...draftRuleCommonFields,
                        id: 'f32c07a0-2a92-4484-8fd6-45c975f42b67',
                        week_days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                        workshift: {end: '23:00', start: '10:00'},
                        min_online_minutes: 3,
                        rate_free_per_minute: '11',
                        rate_on_order_per_minute: '11',
                    },
                    {
                        ...draftRuleCommonFields,
                        id: '44bf97bf-40ea-4aa1-84e4-5c2c6524304f',
                        week_days: ['mon', 'wed', 'thu', 'sat', 'sun'],
                        workshift: {end: '22:00', start: '11:00'},
                        min_online_minutes: 2,
                        rate_free_per_minute: '10',
                        rate_on_order_per_minute: '10',
                    },
                ],
            },
        };
        const draftModel = makeDraftModel(draft, BookingRate.OnOrder, 'taxirate-53');
        const preparedDraft = preSave(draftModel, 100);

        expect(omitIds(preparedDraft.data)).toEqual(omitIds(draft.data!));
    });
});
