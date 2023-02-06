const {createStrategyDefiner} = require('../createStrategyDefiner');

const MOCK_STRATEGIES = {
    POST: new Map([
        [/any_url\/any_method/, {isMockeStrategies: true}]
    ])
};

const MOCK_REQ = {
    method: 'POST',
    originalUrl: 'any_url/any_method'
};

describe('createStrategyDefiner', () => {
    test('valid', () => {
        const strategy = createStrategyDefiner(MOCK_STRATEGIES)(MOCK_REQ);

        expect(strategy.isMockeStrategies).toBe(true);
    });

    test('invalid', () => {
        const strategy = createStrategyDefiner(MOCK_STRATEGIES)({method: 'POST', originalUrl: 'qazqwsxwsx/wfscsc'});

        expect(strategy).toBeUndefined();
    });
});
