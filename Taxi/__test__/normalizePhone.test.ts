import normalizePhone from '../normalizePhone';

describe.each([
    ['89991234567', '+79991234567'],
    ['89991234567', '+79991234567', {isInternationalPhone: false}],
    ['89991234567', '+79991234567', {isInternationalPhone: true}],
    ['8619993180123', '+7619993180123'],
    ['8619993180123', '+7619993180123', {isInternationalPhone: false}],
    ['8619993180123', '+8619993180123', {isInternationalPhone: true}],

])(
    '%p %p %p',
    (value, expected, options?) => {
        test('правильно нормализует телефон', () => {
            expect(normalizePhone(value, options)).toEqual(expected);
        });
    },
    0
);
