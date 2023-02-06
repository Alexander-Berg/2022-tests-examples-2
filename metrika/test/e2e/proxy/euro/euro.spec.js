const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Euro bundle', function () {
    const baseUrl = 'https://yandex.com/test/euro/euro.hbs';
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should find euro page', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect('euro page').to.be.equal(innerText);
            });
    });
    it('should send hit to com domain', function () {
        const sessID = Math.round(Math.random() * 10000);
        return this.browser
            .url(`https://yandex.ru/test/euro/euro.hbs?sessID=${sessID}`)
            .url(`${baseUrl}?sessID=${sessID}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(1000);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hostsDict = requests.reduce((dict, request) => {
                    const host = request.headers['x-host'];
                    if (!dict[host]) {
                        dict[host] = 1;
                    } else {
                        dict[host] += 1;
                    }
                    return dict;
                }, {});
                const hosts = Object.keys(hostsDict);
                chai.expect(hosts).to.be.lengthOf(1);
                const [host] = hosts;
                chai.expect(host).to.be.eq('mc.yandex.com');
            });
    });
});
