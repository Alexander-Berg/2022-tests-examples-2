import {formatCurrency} from '../formatter';

describe('utils:formatter', () => {
    describe('formatCurrency', () => {
        it('Цена верно форматируется', () => {
            expect(formatCurrency('100 $SIGN$$CURRENCY$', 'RUB')).toBe('100 ₽');
            expect(formatCurrency('100 $SIGN$$CURRENCY$', 'ПОПУГАЕВ')).toBe('100 ПОПУГАЕВ');
        });

        it('Если price нет - возвращает пустую строку', () => {
            expect(formatCurrency(undefined, 'RUB')).toBe('');
        });
    });
});
