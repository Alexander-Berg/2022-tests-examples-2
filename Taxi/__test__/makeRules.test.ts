import {RuleType, ServiceName} from '../../common/enums';
import {RuleItem} from '../../common/types';
import {
    DEFAULT_BULK_EVENT,
    EVENT_NAME_CELL_NAME,
    EVENT_TOPIC_CELL_NAME,
    GLOBAL_TAGS_CELL_NAME,
    TAG_PREFIX,
    TAG_SEPARATOR,
} from '../consts';
import {DiffTableModel} from '../types';
import {makeRules} from '../utils';

describe('makeRules', () => {
    it('Корректная генерация правил', () => {
        const diffTable: DiffTableModel = {
            ruleName: 'LoyaltyRule',
            header: [GLOBAL_TAGS_CELL_NAME, EVENT_TOPIC_CELL_NAME, EVENT_NAME_CELL_NAME],
            nextRows: {
                moscow: ['90_days 80_days', 'order', 'complete'],
            },
            previousRows: {},
        };
        const zoneList: Record<string, RuleItem[]> = {
            moscow: [
                {
                    name: 'LoyaltyRule',
                    zone: 'moscow',
                    id: '80_80_80',
                    actions: [],
                },
            ],
        };

        const expectedValue: RuleItem[] = [
            {
                name: 'LoyaltyRule',
                zone: 'moscow',
                additional_params: {
                    tags: `'${TAG_PREFIX}90_days'${TAG_SEPARATOR}'${TAG_PREFIX}80_days'`,
                },
                previous_revision_id: '80_80_80',
                events: [DEFAULT_BULK_EVENT],
                actions: [],
                type: RuleType.Loyalty,
                service_name: ServiceName.Driver,
                disabled: false,
                protected: false,
                delayed: false,
            },
        ];

        expect(makeRules(diffTable, zoneList)).toEqual(expectedValue);
    });

    it('Корректная генерация правил при наличии правил с другим именем или из другой зоны', () => {
        const diffTable: DiffTableModel = {
            ruleName: 'LoyaltyRule',
            header: [],
            nextRows: {
                moscow: [],
            },
            previousRows: {},
        };
        const zoneList: Record<string, RuleItem[]> = {
            moscow: [
                {
                    name: 'LoyaltyRule2',
                    zone: 'moscow',
                    id: '100_80_80',
                    actions: [],
                },
                {
                    name: 'LoyaltyRule',
                    zone: 'default',
                    id: '200_80_80',
                    actions: [],
                },
                {
                    name: 'LoyaltyRule',
                    zone: 'moscow',
                    id: '80_80_80',
                    actions: [],
                },
            ],
        };

        const expectedValue: RuleItem[] = [
            {
                name: 'LoyaltyRule',
                zone: 'moscow',
                previous_revision_id: '80_80_80',
                actions: [],
                events: [DEFAULT_BULK_EVENT],
                type: RuleType.Loyalty,
                service_name: ServiceName.Driver,
                disabled: false,
                protected: false,
                delayed: false,
            },
        ];

        expect(makeRules(diffTable, zoneList)).toEqual(expectedValue);
    });

    it('Пропуск правил без изменений при генерации правил из таблицы', () => {
        const diffTable: DiffTableModel = {
            ruleName: 'LoyaltyRule',
            header: [GLOBAL_TAGS_CELL_NAME, EVENT_TOPIC_CELL_NAME, EVENT_NAME_CELL_NAME],
            nextRows: {
                moscow: ['90_days 80_days', 'order', 'complete'],
                piter: ['90_days 80_days', 'order', 'complete'],
            },
            previousRows: {
                piter: ['90_days 80_days', 'order', 'complete'],
            },
        };

        const zoneList: Record<string, RuleItem[]> = {
            moscow: [
                {
                    name: 'LoyaltyRule',
                    zone: 'moscow',
                    id: '80_80_80',
                    actions: [],
                },
            ],
            piter: [
                {
                    name: 'LoyaltyRule',
                    zone: 'piter',
                    id: '80_80_80',
                    actions: [],
                },
            ],
        };

        const expectedValue: RuleItem[] = [
            {
                name: 'LoyaltyRule',
                zone: 'moscow',
                additional_params: {
                    tags: `'${TAG_PREFIX}90_days'${TAG_SEPARATOR}'${TAG_PREFIX}80_days'`,
                },
                previous_revision_id: '80_80_80',
                events: [DEFAULT_BULK_EVENT],
                actions: [],
                type: RuleType.Loyalty,
                service_name: ServiceName.Driver,
                disabled: false,
                protected: false,
                delayed: false,
            },
        ];

        expect(makeRules(diffTable, zoneList)).toEqual(expectedValue);
    });
});
