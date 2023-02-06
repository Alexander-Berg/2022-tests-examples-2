import {DISPLAY_FALLBACK, PRICE_TEMPLATE_CURRENCY_SPLITTER, PRICE_TEMPLATE_SIGN_SPLITTER} from '_pkg/consts/common';

import {
    amountCheckIsParsable,
    defaultCheckIsFormatable,
    defaultCheckIsParsable,
    defaultFormat,
    formatAmountPrice,
    formatedCheckIsParsable,
    formatFormatedPrice,
    formatTemplatePrice,
    templateCheckIsParsable,
    templateParse
} from '../price';

const PRICE_TEMPLATE_SPLITTER = `${PRICE_TEMPLATE_SIGN_SPLITTER}${PRICE_TEMPLATE_CURRENCY_SPLITTER}`;

const FAILED = {
    type: 'failed',
    value: DISPLAY_FALLBACK
};

const PASSED = {
    type: 'passed'
};

const RUB = 'RUB';

const RU = 'RU';

describe('defaultPrice', () => {
    test('defaultCheckIsParsable', () => {
        expect(defaultCheckIsParsable('', '', '')).toEqual(FAILED);
        expect(defaultCheckIsParsable('0', '', '')).toEqual(FAILED);
        expect(defaultCheckIsParsable('0', RUB, '')).toEqual(FAILED);
        expect(defaultCheckIsParsable('0', RUB, RU)).toEqual(PASSED);
    });

    test('defaultCheckIsFormatable', () => {
        expect(defaultCheckIsFormatable('')).toEqual(FAILED);
        expect(defaultCheckIsFormatable('x')).toEqual(FAILED);
        expect(defaultCheckIsFormatable('00,12')).toEqual(FAILED);
        expect(defaultCheckIsFormatable('  0')).toEqual(PASSED);
        expect(defaultCheckIsFormatable('0')).toEqual(PASSED);
        expect(defaultCheckIsFormatable('00.12')).toEqual(PASSED);
        expect(defaultCheckIsFormatable(0)).toEqual(PASSED);
        expect(defaultCheckIsFormatable(0.12)).toEqual(PASSED);
    });

    test('defaultFormat', () => {
        expect(defaultFormat('0', RUB, RU)).toEqual('RUB 0.00');
        expect(defaultFormat('0.12', RUB, RU)).toEqual('RUB 0.12');
        expect(defaultFormat('0,12', RUB, RU)).toEqual('RUB 0.00');
        expect(defaultFormat(0, RUB, RU)).toEqual('RUB 0.00');
        expect(defaultFormat(0.12, RUB, RU)).toEqual('RUB 0.12');
    });
});

describe('templatePrice', () => {
    test('templateCheckIsParsable', () => {
        expect(templateCheckIsParsable('', '', '')).toEqual(FAILED);
        expect(templateCheckIsParsable('0', '', '')).toEqual(FAILED);
        expect(templateCheckIsParsable('0', RUB, '')).toEqual(FAILED);
        expect(templateCheckIsParsable('0', RUB, RU)).toEqual(FAILED);
        expect(templateCheckIsParsable(0, RUB, RU)).toEqual(FAILED);
        expect(templateCheckIsParsable(`0 ${PRICE_TEMPLATE_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(`x ${PRICE_TEMPLATE_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(PRICE_TEMPLATE_SPLITTER, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(`0 ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(`x ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(PRICE_TEMPLATE_CURRENCY_SPLITTER, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(`0 ${PRICE_TEMPLATE_SIGN_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(`x ${PRICE_TEMPLATE_SIGN_SPLITTER}`, RUB, RU)).toEqual(PASSED);
        expect(templateCheckIsParsable(PRICE_TEMPLATE_SIGN_SPLITTER, RUB, RU)).toEqual(PASSED);
        expect(
            templateCheckIsParsable(`${PRICE_TEMPLATE_CURRENCY_SPLITTER} 0 ${PRICE_TEMPLATE_SIGN_SPLITTER}`, RUB, RU)
        ).toEqual(PASSED);
        expect(
            templateCheckIsParsable(`${PRICE_TEMPLATE_CURRENCY_SPLITTER} x ${PRICE_TEMPLATE_SIGN_SPLITTER}`, RUB, RU)
        ).toEqual(PASSED);
        expect(
            templateCheckIsParsable(`${PRICE_TEMPLATE_SIGN_SPLITTER} ${PRICE_TEMPLATE_CURRENCY_SPLITTER} 0`, RUB, RU)
        ).toEqual(PASSED);
        expect(
            templateCheckIsParsable(`${PRICE_TEMPLATE_SIGN_SPLITTER} ${PRICE_TEMPLATE_CURRENCY_SPLITTER} x`, RUB, RU)
        ).toEqual(PASSED);
    });

    test('templateParse', () => {
        expect(templateParse(0)).toEqual('0');
        expect(templateParse(0.12)).toEqual('0.12');
        expect(templateParse('')).toEqual('');
        expect(templateParse('x')).toEqual('x');
        expect(templateParse('0')).toEqual('0');
        expect(templateParse(' 0 ')).toEqual('0');
        expect(templateParse('0.12')).toEqual('0.12');
        expect(templateParse('0,12')).toEqual('0.12');
    });

    test('formatTemplatePrice', () => {
        expect(formatTemplatePrice({value: '', currency: ''})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: '', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: '0', currency: ''})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: 'x', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: '0', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: 0, currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: PRICE_TEMPLATE_SPLITTER, currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: `x ${PRICE_TEMPLATE_SPLITTER}`, currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: `0 ${PRICE_TEMPLATE_SPLITTER}`, currency: RUB})).toEqual('RUB 0.00');
        expect(formatTemplatePrice({value: `0.12 ${PRICE_TEMPLATE_SPLITTER}`, currency: RUB})).toEqual('RUB 0.12');
        expect(formatTemplatePrice({value: `0,12 ${PRICE_TEMPLATE_SPLITTER}`, currency: RUB})).toEqual('RUB 0.12');
        expect(formatTemplatePrice({value: PRICE_TEMPLATE_CURRENCY_SPLITTER, currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: `x ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, currency: RUB})).toEqual(
            DISPLAY_FALLBACK
        );
        expect(formatTemplatePrice({value: `0 ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, currency: RUB})).toEqual(
            'RUB 0.00'
        );
        expect(formatTemplatePrice({value: `0.12 ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, currency: RUB})).toEqual(
            'RUB 0.12'
        );
        expect(formatTemplatePrice({value: `0,12 ${PRICE_TEMPLATE_CURRENCY_SPLITTER}`, currency: RUB})).toEqual(
            'RUB 0.12'
        );
        expect(formatTemplatePrice({value: PRICE_TEMPLATE_SIGN_SPLITTER, currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatTemplatePrice({value: `x ${PRICE_TEMPLATE_SIGN_SPLITTER}`, currency: RUB})).toEqual(
            DISPLAY_FALLBACK
        );
        expect(formatTemplatePrice({value: `0 ${PRICE_TEMPLATE_SIGN_SPLITTER}`, currency: RUB})).toEqual('RUB 0.00');
        expect(formatTemplatePrice({value: `0.12 ${PRICE_TEMPLATE_SIGN_SPLITTER}`, currency: RUB})).toEqual('RUB 0.12');
        expect(formatTemplatePrice({value: `0,12 ${PRICE_TEMPLATE_SIGN_SPLITTER}`, currency: RUB})).toEqual('RUB 0.12');
        expect(
            formatTemplatePrice({
                value: `${PRICE_TEMPLATE_CURRENCY_SPLITTER} x ${PRICE_TEMPLATE_SIGN_SPLITTER}`,
                currency: RUB
            })
        ).toEqual(DISPLAY_FALLBACK);
        expect(
            formatTemplatePrice({
                value: `${PRICE_TEMPLATE_CURRENCY_SPLITTER} 0 ${PRICE_TEMPLATE_SIGN_SPLITTER}`,
                currency: RUB
            })
        ).toEqual('RUB 0.00');
        expect(
            formatTemplatePrice({
                value: `${PRICE_TEMPLATE_CURRENCY_SPLITTER} 0.12 ${PRICE_TEMPLATE_SIGN_SPLITTER}`,
                currency: RUB
            })
        ).toEqual('RUB 0.12');
        expect(
            formatTemplatePrice({
                value: `${PRICE_TEMPLATE_CURRENCY_SPLITTER} 0,12 ${PRICE_TEMPLATE_SIGN_SPLITTER}`,
                currency: RUB
            })
        ).toEqual('RUB 0.12');
    });
});

describe('amountPrice', () => {
    test('amountCheckIsParsable', () => {
        expect(amountCheckIsParsable('', '', '')).toEqual(FAILED);
        expect(amountCheckIsParsable('0', '', '')).toEqual(FAILED);
        expect(amountCheckIsParsable('0', RUB, '')).toEqual(FAILED);
        expect(amountCheckIsParsable('x', RUB, '')).toEqual(FAILED);
        expect(amountCheckIsParsable('0,12', RUB, RU)).toEqual(FAILED);
        expect(amountCheckIsParsable('0', RUB, RU)).toEqual(PASSED);
        expect(amountCheckIsParsable('0.12', RUB, RU)).toEqual(PASSED);
        expect(amountCheckIsParsable(0, RUB, RU)).toEqual(PASSED);
        expect(amountCheckIsParsable(0.12, RUB, RU)).toEqual(PASSED);
    });

    test('formatAmountPrice', () => {
        expect(formatAmountPrice({value: '', currency: ''})).toEqual(DISPLAY_FALLBACK);
        expect(formatAmountPrice({value: '', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatAmountPrice({value: '0', currency: ''})).toEqual(DISPLAY_FALLBACK);
        expect(formatAmountPrice({value: 'x', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatAmountPrice({value: '0,12', currency: RUB})).toEqual(DISPLAY_FALLBACK);
        expect(formatAmountPrice({value: '0', currency: RUB})).toEqual('RUB 0.00');
        expect(formatAmountPrice({value: ' 0 ', currency: RUB})).toEqual('RUB 0.00');
        expect(formatAmountPrice({value: '0.12', currency: RUB})).toEqual('RUB 0.12');
        expect(formatAmountPrice({value: 0, currency: RUB})).toEqual('RUB 0.00');
        expect(formatAmountPrice({value: 0.12, currency: RUB})).toEqual('RUB 0.12');
    });
});

describe('formatedPrice', () => {
    test('formatedCheckIsParsable', () => {
        expect(formatedCheckIsParsable('')).toEqual(FAILED);
        expect(formatedCheckIsParsable('x')).toEqual(PASSED);
        expect(formatedCheckIsParsable('0')).toEqual(PASSED);
        expect(formatedCheckIsParsable(0)).toEqual(PASSED);
    });

    test('formatFormatedPrice', () => {
        expect(formatFormatedPrice({value: '', currency: ''})).toEqual(DISPLAY_FALLBACK);
        expect(formatFormatedPrice({value: 'x'})).toEqual('x');
        expect(formatFormatedPrice({value: '0'})).toEqual('0');
        expect(formatFormatedPrice({value: '0,12'})).toEqual('0,12');
        expect(formatFormatedPrice({value: 0})).toEqual('0');
    });
});
