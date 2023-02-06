const {lint} = require('stylelint');

const CONFIG = {
    plugins: ['./stylelint-rules/no-top-level-global/index.js'],
    rules: {
        'custom-rules/no-top-level-global': true
    },
    configBaseDir: '/services/tef-campaign-management/stylelint-rules'
};

const AT_RULE_INVALID_CODE =
`@media (min-width: 1000px) {
    :global(.test) {}
}`;

describe('Valid cases', () => {
    it('One level depth with nested selector', async () => {
        const {results: [{warnings, parseErrors}]} = await lint({
            code: '.test { :global { .test {} } }',
            config: CONFIG
        });

        expect(parseErrors).toHaveLength(0);
        expect(warnings).toHaveLength(0);
    });

    it('One level depth with parenthesis', async () => {
        const {results: [{warnings, parseErrors}]} = await lint({
            code: '.test { :global(.test) {} }',
            config: CONFIG
        });

        expect(parseErrors).toHaveLength(0);
        expect(warnings).toHaveLength(0);
    });
});

describe('Invalid cases', () => {
    it('Top level without parenthesis', async () => {
        const {results: [{warnings}]} = await lint({
            code: ':global {}',
            config: CONFIG
        });
        const [{line, text, column}] = warnings;

        expect(text).toBe('Unexpected global on top level (custom-rules/no-top-level-global)');
        expect(line).toBe(1);
        expect(column).toBe(1);
    });

    it('Top level with parenthesis', async () => {
        const {results: [{warnings}]} = await lint({
            code: ':global(.test) {}',
            config: CONFIG
        });
        const [{line, text, column}] = warnings;

        expect(text).toBe('Unexpected global on top level (custom-rules/no-top-level-global)');
        expect(line).toBe(1);
        expect(column).toBe(1);
    });

    it('Top level inside at-rule', async () => {
        const {results: [{warnings}]} = await lint({
            code: AT_RULE_INVALID_CODE,
            config: CONFIG
        });
        const [{line, text, column}] = warnings;

        expect(text).toBe('Unexpected global on top level (custom-rules/no-top-level-global)');
        expect(line).toBe(2);
        expect(column).toBe(5);
    });
});
