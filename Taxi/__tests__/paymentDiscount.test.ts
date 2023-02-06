import moment from 'moment';

import {PriorityType} from '_pkg/utils/makePriorityOptions';

import {ALL, ANY} from '../../consts';
import {HierarchyDescriptionName, TimeType, ZoneType} from '../../enums';
import {RuleCondition} from '../../types';
import {makeCommonPaymentFields} from '../../utils';
import {prepareDiscountDataToModel} from '../paymentDiscount';

const RULES_VIEW = {
    zone: {
        zoneList: ['br_moscow'],
        isPrioritized: true,
    },
    orderType: {
        priorityType: PriorityType.String,
        values: ['air', 'on_air'],
        exclusions: [],
    },
    bins: {
        priorityType: PriorityType.String,
        values: [
            {name: 'bin', values: ''},
            {name: 'bin_set', values: ''},
        ],
        exclusions: [],
    },
    tags: {
        priorityType: PriorityType.All,
        values: [],
        exclusions: ['tag1', 'tag2'],
    },
    paymentMethod: {
        priorityType: PriorityType.String,
        value: 'pay',
        exclusions: [],
    },
    applicationName: {
        priorityType: PriorityType.Any,
        values: [],
        exclusions: ['app'],
    },
    applicationBrand: {
        priorityType: PriorityType.Any,
        values: [],
        exclusions: ['brand'],
    },
    applicationPlatform: {
        priorityType: PriorityType.Any,
        values: [],
        exclusions: ['platform'],
    },
    yaplus: {
        priorityType: PriorityType.String,
        value: 0,
        exclusions: [],
    },
    tariff: {
        priorityType: PriorityType.String,
        values: ['tar_1', 'tar_2'],
        exclusions: [],
    },
    isSetPointB: true,
    activePeriod: {
        start: {
            time: '12:00',
            date: moment('2019-02-10'),
        },
        end: {
            time: '16:38',
            date: moment('2020-04-01'),
        },
        timeType: TimeType.Global,
        updateExistingDiscounts: false,
    },
    applyTripsWithoutPoints: true,
};

const RULES: RuleCondition[] = [
    {condition_name: HierarchyDescriptionName.IsSetPointB, values: ANY},
    {
        condition_name: HierarchyDescriptionName.Zone,
        values: [
            {
                name: 'br_moscow',
                type: ZoneType.Geonode,
                is_prioritized: true,
            },
        ],
    },
    {condition_name: HierarchyDescriptionName.OrderType, values: ['air', 'on_air']},
    {condition_name: HierarchyDescriptionName.Tag, values: ALL, exclusions: ['tag1', 'tag2']},
    {condition_name: HierarchyDescriptionName.PaymentMethod, values: ['pay']},
    {condition_name: HierarchyDescriptionName.Bins, values: ['bin', 'bin_set']},
    {condition_name: HierarchyDescriptionName.ApplicationType, values: ANY, exclusions: ['app']},
    {condition_name: HierarchyDescriptionName.ApplicationBrand, values: ANY, exclusions: ['brand']},
    {condition_name: HierarchyDescriptionName.ApplicationPlatform, values: ANY, exclusions: ['platform']},
    {condition_name: HierarchyDescriptionName.YaPlus, values: [0]},
    {condition_name: HierarchyDescriptionName.Tariff, values: ['tar_1', 'tar_2']},
    {condition_name: HierarchyDescriptionName.IntermediatePoint, values: [0]},
    {
        condition_name: HierarchyDescriptionName.ActivePeriod,
        values: [
            {
                start: '2019-02-10T12:00:00+00:00',
                end: '2020-04-01T16:38:00+00:00',
                is_start_utc: true,
                is_end_utc: true,
            },
        ],
    },
];

describe('Конвертация PaymentDiscount', () => {
    it('prepareDiscountDataToModel', () => {
        const result = prepareDiscountDataToModel({
            rules: RULES,
            discount: {
                name: '',
                values_with_schedules: [],
            },
            tickets: [],
        });

        expect(result).toEqual({
            ...makeCommonPaymentFields(),
            ...RULES_VIEW,
        });
    });
});
