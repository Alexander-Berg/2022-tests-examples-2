import * as application from './application';

const userAgents = {
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-taxi/999.9.9.9999': {
        name: 'yandex-taxi',
        version: '999.9.9.9999'
    },
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-taxi/1patch': {
        name: 'yandex-taxi',
        version: '1patch'
    },
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-taxi/': null,
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)': null,
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-unsupported/999.9.9.9999': null,
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-unsupported/1patch': null,
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) yandex-unsupported/': null,
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) uber-az/999.9.9.9999': {
        name: 'uber-az',
        version: '999.9.9.9999'
    },
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) uber-az/1patch': {
        name: 'uber-az',
        version: '1patch'
    },
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) uber-az/': null
};

describe('application', () => {
    it('parseApplicationFromUserAgent', () => {
        for (const [userAgent, expected] of Object.entries(userAgents)) {
            expect(application.parseApplicationFromUserAgent(userAgent)).toEqual(expected);
        }
    });
});
