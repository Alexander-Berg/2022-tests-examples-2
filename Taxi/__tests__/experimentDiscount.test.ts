import moment from 'moment';

import {PriorityType} from '_pkg/utils/makePriorityOptions';

import {ALL, ANY} from '../../consts';
import {HierarchyDescriptionName, TimeType, ZoneType} from '../../enums';
import {RuleCondition} from '../../types';
import {makeCommonExperimentFields} from '../../utils';
import {prepareExperimentDiscountDataToCommonModel} from '../experimentDiscount';

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
    experimentLabel: {
        priorityType: PriorityType.String,
        value: 'exp',
        exclusions: [],
    },
    tags: {
        priorityType: PriorityType.All,
        values: [],
        exclusions: ['tag1', 'tag2'],
    },
    paymentMethod: {
        priorityType: PriorityType.Any,
        values: [],
        exclusions: ['pay', 'pay_2'],
    },
    applicationName: {
        priorityType: PriorityType.String,
        values: ['app'],
        exclusions: [],
    },
    applicationBrand: {
        priorityType: PriorityType.String,
        values: ['brand'],
        exclusions: [],
    },
    applicationPlatform: {
        priorityType: PriorityType.String,
        values: ['platform'],
        exclusions: [],
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
    geoareaSetA: ['geo_1', 'geo_2'],
    geoareaSetB: ['geo_3', 'geo_4'],
    surgeRange: {
        start: '1.3',
        end: '9',
    },
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
    {condition_name: HierarchyDescriptionName.GeoareaSetA, values: [['geo_1', 'geo_2']]},
    {condition_name: HierarchyDescriptionName.GeoareaSetB, values: [['geo_3', 'geo_4']]},
    {
        condition_name: HierarchyDescriptionName.SurgeRange,
        values: [
            {
                start: '1.3',
                end: '9.0',
            },
        ],
    },
    {condition_name: HierarchyDescriptionName.IsSetPointB, values: ANY},
    {condition_name: HierarchyDescriptionName.LabelExperiment, values: ['exp']},
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
    {condition_name: HierarchyDescriptionName.PaymentMethod, values: ANY, exclusions: ['pay', 'pay_2']},
    {condition_name: HierarchyDescriptionName.ApplicationType, values: ['app']},
    {condition_name: HierarchyDescriptionName.ApplicationBrand, values: ['brand']},
    {condition_name: HierarchyDescriptionName.ApplicationPlatform, values: ['platform']},
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

describe('Конвертация ExperimentDiscount', () => {
    it('prepareDiscountDataToModel', () => {
        const result = prepareExperimentDiscountDataToCommonModel({
            rules: RULES,
            discount: {
                name: '',
                values_with_schedules: [],
                timezone: 'UTC',
            },
            tickets: [],
        });

        expect(result).toEqual({
            ...makeCommonExperimentFields(),
            ...RULES_VIEW,
        });
    });
});
