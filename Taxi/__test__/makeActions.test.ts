import {sortBy} from 'lodash';
import {ActionType} from '../../common/enums';
import {ActionsItem} from '../../common/types';
import {TAG_SEPARATOR, TARIFF_PREFIX} from '../consts';
import {makeActions} from '../utils';

describe('makeActions', () => {
    it('Конвертация строчек в список ActionItem', () => {
        const tariffRow = ['econom', 'kids', 'uber'];
        const values = ['67', '33', '9', '90_days', 'order', 'complete'];
        const expectedValue: ActionsItem[] = sortBy([
            {
                tags: `'${TARIFF_PREFIX}econom'`,
                action: [
                    {type: ActionType.Loyalty, value: 67},
                ]
            },
            {
                tags: `'${TARIFF_PREFIX}kids'`,
                action: [
                    {type: ActionType.Loyalty, value: 33},
                ]
            },
            {
                tags: `'${TARIFF_PREFIX}uber'`,
                action: [
                    {type: ActionType.Loyalty, value: 9},
                ]
            },
        ], m => m.tags);
        expect(sortBy(makeActions(tariffRow, values), m => m.tags)).toEqual(expectedValue);
    });

    it('Группировка одинаковых значений при конвертация строчек в список ActionItem', () => {
        const tariffRow = ['econom', 'kids', 'uber'];
        const values = ['67', '9', '9', '90_days', '', ''];
        const expectedValue: ActionsItem[] = sortBy([
            {
                tags: `'${TARIFF_PREFIX}econom'`,
                action: [
                    {type: ActionType.Loyalty, value: 67},
                ]
            },
            {
                tags: `'${TARIFF_PREFIX}kids'${TAG_SEPARATOR}'${TARIFF_PREFIX}uber'`,
                action: [
                    {type: ActionType.Loyalty, value: 9},
                ]
            },
        ], m => m.tags);
        expect(sortBy(makeActions(tariffRow, values), m => m.tags)).toEqual(expectedValue);
    });
});
