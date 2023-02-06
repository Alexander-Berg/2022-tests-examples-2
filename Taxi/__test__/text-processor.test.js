import {createProcessor} from '../text-processor';

const FORMATTER_SQUARE_BRACKETS = {
    regExp: /\[(.+?)\]/,
    factory: ([, text], process) => `<s>${process(text)}</s>`,
    tooltip: 'FORMATTER_SQUARE_BRACKETS'
};

const FORMATTER_ROUND_BRACKETS = {
    regExp: /\((.+?)\)/,
    factory: ([, text], process) => `<r>${process(text)}</r>`,
    tooltip: 'FORMATTER_ROUND_BRACKETS'
};

const FORMATTER_BAD_BRACKETS = {
    regExp: /\[(.+?)\[/,
    factory: () => '',
    tooltip: 'FORMATTER_BAD_BRACKETS'
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

    describe('utils:text-processor:renderer', () => {
        test('should render', () => {
            const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
            const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
            const SOURCE = `This is [${TEXT_1}] and [${TEXT_2}]`;
            const TARGET = `This is <s>${TEXT_1}</s> and <s>${TEXT_2}</s>`;
            const process = createProcessor([FORMATTER_SQUARE_BRACKETS], sanitizer);
            const renderer = process.getRenderer(SOURCE);

            expect(renderer.render()).toBe(TARGET);
        });

        test('values should be equal', () => {
            const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
            const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
            const SOURCE = `This is [${TEXT_1}] and [${TEXT_2}]`;
            const process = createProcessor([FORMATTER_SQUARE_BRACKETS], sanitizer);
            const renderer = process.getRenderer(SOURCE);

            expect(renderer.values).toEqual([`<s>${TEXT_1}</s>`, `<s>${TEXT_2}</s>`]);
        });

        test('tooltips should be equal', () => {
            const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
            const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
            const SOURCE = `This is (${TEXT_1}) and [${TEXT_2}]`;
            const process = createProcessor([FORMATTER_SQUARE_BRACKETS, FORMATTER_ROUND_BRACKETS], sanitizer);
            const renderer = process.getRenderer(SOURCE);

            expect(renderer.tooltips).toEqual([FORMATTER_SQUARE_BRACKETS.tooltip, FORMATTER_ROUND_BRACKETS.tooltip]);
        });

        test('tooltips should be equal', () => {
            const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
            const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
            const SOURCE = `This is (${TEXT_1}) and [${TEXT_2}]`;
            const process = createProcessor([FORMATTER_SQUARE_BRACKETS, FORMATTER_ROUND_BRACKETS], sanitizer);
            const renderer = process.getRenderer(SOURCE);

            expect(renderer.tooltips).toEqual([FORMATTER_SQUARE_BRACKETS.tooltip, FORMATTER_ROUND_BRACKETS.tooltip]);
        });

        test('should hasEmptyValues', () => {
            const TEXT_1 = 'TEXT WITHOUT BRACKETS 1';
            const TEXT_2 = 'TEXT WITHOUT BRACKETS 2';
            const TEXT_3 = 'TEXT WITHOUT BRACKETS 3';
            const SOURCE = `This is (${TEXT_1}) and [${TEXT_2}] and [${TEXT_3}[`;
            const process = createProcessor(
                [FORMATTER_SQUARE_BRACKETS, FORMATTER_ROUND_BRACKETS, FORMATTER_BAD_BRACKETS],
                sanitizer
            );
            const renderer = process.getRenderer(SOURCE);

            expect(renderer.hasEmptyValues).toBe(true);
        });
    });
});
