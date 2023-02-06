import {preSavePriceModifier} from '../matchers';

describe('preSavePriceModifier', () => {
    it('Корректное преобразование', () => {
        expect(preSavePriceModifier({
            modifiers: [{
                id: 'id_1',
                type: 'type',
                is_enabled: false,
                pay_subventions: undefined,
                tariff_categories: ['tar_1', 'tar_2'],
                value: '89',
            }],
            country: 'rus',
            ticket: 'ticket',
        })).toEqual({
            modifiers: [{
                id: 'id_1',
                type: 'type',
                is_enabled: false,
                pay_subventions: false,
                tariff_categories: ['tar_1', 'tar_2'],
                value: '89',
            }],
            country: 'rus',
            ticket: 'ticket',
        });
    });
});
