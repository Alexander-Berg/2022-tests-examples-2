import {ActionType} from '../../common/enums';
import {RuleItem} from '../../common/types';
import {EVENT_NAME_CELL_NAME, EVENT_TOPIC_CELL_NAME, GLOBAL_TAGS_CELL_NAME} from '../consts';
import {convertRuleItemToRow} from '../utils';

describe('convertRuleItemToRow', () => {
    it('Конвертация RuleItem в строку', () => {
        const tariffRow = [
            'kids',
            'cargo',
            'cargo_uber',
            'econom',
            GLOBAL_TAGS_CELL_NAME,
            EVENT_TOPIC_CELL_NAME,
            EVENT_NAME_CELL_NAME,
        ];
        const rule: RuleItem = {
            additional_params: {
                tags: '\'tags::90_days\' OR \'tags::80_days\'',
            },
            events: [{
                name: 'complete',
                topic: 'order',
            }],
            actions: [
                {
                    tags: '\'event::tariff_kids\' OR \'event::tariff_econom\'', action: [
                        {type: ActionType.Loyalty, value: 78},
                    ]
                },
                {
                    tags: '\'event::tariff_cargo\' OR \'event::tariff_cargo_uber\'', action: [
                        {type: ActionType.Loyalty, value: 33},
                    ]
                },
            ],
        };

        expect(convertRuleItemToRow(tariffRow, rule)).toEqual(['78', '33', '33', '78', '90_days 80_days', 'order', 'complete']);
    });
});
