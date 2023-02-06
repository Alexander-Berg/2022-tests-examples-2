const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yandex gdpr skip bot test', function () {
    const location = 'https://yandex.ru/test/gdprSkipBot/';
    const baseUrl = `${location}gdprSkipBot.hbs`;
    const counterId = 20302;
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .execute(function () {
                localStorage.clear();
                localStorage.setItem('_ym_synced', '{"SYNCED_ADM":9999999999}');
            });
    });
    it('should skip bot', function () {
        return this.browser
            .url(baseUrl)
            .deleteCookie('gdpr')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options) {
                        serverHelpers.collectRequests(1000);

                        new Ya.Metrika2(options.counterId);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const req = requests.map(e2eUtils.getRequestParams);
                const counters = req.map((e) => e.counterId);
                const pageViews = req
                    .map((e) => e.brInfo && e.brInfo.pv)
                    .filter(Boolean);
                chai.expect(counters).to.include(`${counterId}`);
                chai.expect(pageViews).lengthOf(1);
                req.forEach((e) => {
                    if (e.counterId === `${counterId}`) {
                        chai.expect(e.brInfo.gdpr).to.be.equal('28');
                    }
                });
            });
    });
});
