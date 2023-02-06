import {parseLegalForm} from './BelarusSuggestService';

test('parseLegalForm', () => {
    expect(parseLegalForm('', 'ЗАО "БКК"')).toBe('ЗАО');
    expect(parseLegalForm('', 'Самарское ЗАО "БКК"')).toBe('ЗАО');
    expect(parseLegalForm('', 'СИЗАО "БКК"')).toBe(undefined);
    expect(parseLegalForm('Самарское закрытое акционерное общество "БКК"', '')).toBe(
        'закрытое акционерное общество',
    );
    expect(parseLegalForm('Закрытое акционерное общество "БКК"', '')).toBe(
        'закрытое акционерное общество',
    );
});
