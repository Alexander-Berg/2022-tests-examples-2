const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('MetrikaPlayer e2e test', function () {
    const playerUrl =
        'https://mm.mtproxy.yandex.net/test/metrikaPlayer/metrikaPlayer.hbs';
    const randomUrl = 'https://yandex.ru/test/metrikaPlayer/randomPage.hbs';
    const counterId = 12345;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('should send http request from a random page', function () {
        return this.browser
            .url(randomUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    'Random page for MetrikaPlayer',
                    'check if it is a random page',
                ).to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2(options.counterId);
                        serverHelpers.collectRequests(1000, null);
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests).is.not.empty;
            });
    });

    it('should not send http request if opened inside a Media Player frame', function () {
        return this.browser
            .url(playerUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    'Metrika player page',
                    'check if it is a special page',
                ).to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2(options.counterId);
                        serverHelpers.collectRequests(1000, null);
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests).is.empty;
            });
    });
});
