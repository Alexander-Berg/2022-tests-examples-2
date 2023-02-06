import {ActionType, RuleType, ServiceName} from '../../common/enums';
import {
    DEFAULT_BULK_EVENT,
    EVENT_NAME_CELL_NAME,
    EVENT_TOPIC_CELL_NAME,
    GLOBAL_TAGS_CELL_NAME,
    TAG_PREFIX,
    TAG_SEPARATOR,
} from '../consts';
import {DiffBulkItem, DiffTableModel, RuleItem} from '../types';
import {makeTableFromRules} from '../utils';

const PREV_MOSCOW_RULE: RuleItem = {
        name: 'LoyaltyRule',
        zone: 'moscow',
        additional_params: {
            tags: `'${TAG_PREFIX}90_days'${TAG_SEPARATOR}'${TAG_PREFIX}80_days'`,
        },
        previous_revision_id: '80_80_80',
        events: [DEFAULT_BULK_EVENT],
        actions: [
            {
                action: [{
                    type: ActionType.Loyalty,
                    value: 10,
                }],
                tags: '\'event::tariff_express\' OR \'event::tariff_courier\'',
            },
            {
                action: [{
                    type: ActionType.Loyalty,
                    value: 20,
                }],
                tags: '\'event::tariff_premium_suv\' OR \'event::tariff_suv\'',
            }
        ],
        type: RuleType.Loyalty,
        service_name: ServiceName.Driver,
        disabled: false,
        protected: false,
        delayed: false,
};
const NEXT_MOSCOW_RULE: RuleItem = {
    ...PREV_MOSCOW_RULE,
    actions: [
        {
            action: [{
                type: ActionType.Loyalty,
                value: 15,
            }],
            tags: '\'event::tariff_express\' OR \'event::tariff_courier\'',
        },
        {
            action: [{
                type: ActionType.Loyalty,
                value: 25,
            }],
            tags: '\'event::tariff_premium_suv\' OR \'event::tariff_suv\'',
        }
    ],
};
const PREV_EKB_RULE: RuleItem = {
    ...PREV_MOSCOW_RULE,
    zone: 'ekb',
    actions: [
        {
            action: [{
                type: ActionType.Loyalty,
                value: 40,
            }],
            tags: '\'event::tariff_express\' OR \'event::tariff_courier\'',
        },
        {
            action: [{
                type: ActionType.Loyalty,
                value: 50,
            }],
            tags: '\'event::tariff_premium_suv\' OR \'event::tariff_suv\'',
        }
    ],
};
const NEXT_EKB_RULE: RuleItem = {
    ...PREV_EKB_RULE,
    zone: 'ekb',
    actions: [
        {
            action: [{
                type: ActionType.Loyalty,
                value: 45,
            }],
            tags: '\'event::tariff_express\' OR \'event::tariff_courier\'',
        },
        {
            action: [{
                type: ActionType.Loyalty,
                value: 55,
            }],
            tags: '\'event::tariff_premium_suv\' OR \'event::tariff_suv\'',
        }
    ],
};

const SUMMARY: DiffBulkItem = {
    new: {
        data: [PREV_MOSCOW_RULE, PREV_EKB_RULE],
    },
    current: {
        data: [NEXT_MOSCOW_RULE, NEXT_EKB_RULE],
    },
};

const DIFF_TABLE: DiffTableModel = {
    ruleName: 'LoyaltyRule',
    header: [
        'courier', 'express', 'premium_suv', 'suv', GLOBAL_TAGS_CELL_NAME, EVENT_TOPIC_CELL_NAME, EVENT_NAME_CELL_NAME,
    ],
    nextRows: {
        ekb: ['40', '40', '50', '50', '90_days 80_days', 'order', 'complete'],
        moscow: ['10', '10', '20', '20', '90_days 80_days', 'order', 'complete'],
    },
    previousRows: {
        ekb: ['45', '45', '55', '55', '90_days 80_days', 'order', 'complete'],
        moscow: ['15', '15', '25', '25', '90_days 80_days', 'order', 'complete'],
    },
};

describe('makeTableFromRules', () => {
    it('Преобразование диффа правил в таблицу для отображения в драфте', () => {
        const table = makeTableFromRules(SUMMARY);
        expect(table).toEqual(DIFF_TABLE);
    });
});
