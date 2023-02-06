import {createProcessor} from '../text-processor';

const FORMATTER_SQUARE_BRACKETS = {
    regExp: /\[(.+?)\]/,
    factory: ([full, text], process) => `<s>${process(text)}</s>`
};

const FORMATTER_ROUND_BRACKETS = {
    regExp: /\((.+?)\)/,
    factory: ([full, text], process) => `<r>${process(text)}</r>`
};

const sanitizer = text => text.replace(/<\/?[sr]>/g, '');

describe('utils:text-processor', () => {
    test('formats by formatter', () => {
        const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
        const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
        const SOURCE = `This is [${TEXT_1}] and [${TEXT_2}]`;
        const TARGET = `This is <s>${TEXT_1}</s> and <s>${TEXT_2}</s>`;

        const process = createProcessor([FORMATTER_SQUARE_BRACKETS], sanitizer);

        expect(process(SOURCE)).toBe(TARGET);
    });

    test('formats by multiple formatters', () => {
        const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
        const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
        const SOURCE = `This is (${TEXT_1}) and [${TEXT_2}]`;
        const TARGET = `This is <r>${TEXT_1}</r> and <s>${TEXT_2}</s>`;

        const process = createProcessor([FORMATTER_SQUARE_BRACKETS, FORMATTER_ROUND_BRACKETS], sanitizer);

        expect(process(SOURCE)).toBe(TARGET);
    });

    test('formats nested tokens', () => {
        const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
        const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
        const SOURCE = `This is [(${TEXT_1})] and ([${TEXT_2}])`;
        const TARGET = `This is <s><r>${TEXT_1}</r></s> and <r><s>${TEXT_2}</s></r>`;

        const process = createProcessor([FORMATTER_ROUND_BRACKETS, FORMATTER_SQUARE_BRACKETS], sanitizer);

        expect(process(SOURCE)).toBe(TARGET);
    });

    test('sanitize works in text that is not markup', () => {
        const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
        const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
        const SOURCE = `This is <s>I AM BAD</s> [(${TEXT_1})] and ([${TEXT_2}])`;
        const TARGET = `This is I AM BAD <s><r>${TEXT_1}</r></s> and <r><s>${TEXT_2}</s></r>`;

        const process = createProcessor([FORMATTER_ROUND_BRACKETS, FORMATTER_SQUARE_BRACKETS], sanitizer);

        expect(process(SOURCE)).toBe(TARGET);
    });

    test('sanitize works in matches of markup', () => {
        const TEXT_1 = '</s>SOME<s>BAD</s>TEXT<s>';
        const SOURCE = `This is [${TEXT_1}]`;
        const TARGET = 'This is <s>SOMEBADTEXT</s>';

        const process = createProcessor([FORMATTER_SQUARE_BRACKETS], sanitizer);

        expect(process(SOURCE)).toBe(TARGET);
    });
});
