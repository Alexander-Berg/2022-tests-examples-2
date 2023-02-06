const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Known Error', function () {
    const baseUrl = 'test/knownError/knownError.hbs';
    const counterId = 1234;
    const KNOWN_ERROR_KEY = 'err.kn';
    const HIT_PROVIDER_KEY = 'h';
    const knownErrorRegex = new RegExp(
        [
            '^Uncaught Error:\\s',
            `(${KNOWN_ERROR_KEY})`,
            '\\(\\d*\\)',
            `(${HIT_PROVIDER_KEY})`,
            '\\.(.*)$',
        ].join(''),
    );

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(4000)
            .url(baseUrl);
    });

    it('Should throw verbose error message', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    status: '500',
                                    count: 4,
                                },
                            ],
                            () => {
                                const counter = new Ya.MetrikaDebug({
                                    id: options.counterId,
                                });
                                counter.hit('https://hh.dd.com');
                                window.onerror = done;
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: message }) => {
                const errMessage = 'didnt find known error log';
                const isKnErr = knownErrorRegex.test(message);
                chai.expect(isKnErr, errMessage).to.be.true;
            });
    });
});
