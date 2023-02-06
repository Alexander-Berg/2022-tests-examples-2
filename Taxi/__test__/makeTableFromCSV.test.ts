import {makeTableFromCSV} from '../utils';

describe('makeTableFromCSV', () => {

    it('Парсинг CSV со всеми заполненными значениями', () => {
        const CSV = ' LoyaltyName ,   kids uber_kids  , econom  econom_uber  \n   moscow,  89  , 10\n  baku, 78   , 9 ';
        const table = makeTableFromCSV(CSV);
        expect(table).toEqual({
            ruleName: 'LoyaltyName',
            header: ['kids', 'uber_kids', 'econom', 'econom_uber'],
            nextRows: {
                moscow: ['89', '89', '10', '10'],
                baku: ['78', '78', '9', '9'],
            },
        });
    });
});
