const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Prerender e2e test', function () {
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .timeoutsImplicitWait(2000);
    });

    it('should send pq and pr', function () {
        const prerenderUrl = `${e2eUtils.baseUrl}/test/prerender/prerender.hbs`;
        const pageUrl = `${e2eUtils.baseUrl}/test/prerender/page.hbs`;

        return (
            this.browser
                .url(prerenderUrl)
                // Таймаут на загрузку ресурсов в фоне
                .pause(2000)
                /*
                При использовании api webdriver (url, window) вкладка загружается
                заново, а не использует предзагруженную.
                */
                .click('.nextPage')
                /*
                Переход по ссылке не меняет активную вкладку в объекте браузера,
                необходимо выставить вручную
                */
                .getTabIds()
                .then((result) => {
                    return this.browser.switchTab(result[1]);
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            serverHelpers.collectRequests(
                                1000,
                                done,
                                options.regexp.defaultRequestRegEx,
                            );
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: requests }) => {
                    chai.expect(requests.length).to.eq(2);
                    const { brInfo: pqBrInfo, params: pqParams } =
                        e2eUtils.getRequestParams(requests[0]);
                    chai.expect(pqBrInfo.pq).to.eq('1');
                    chai.expect(pqBrInfo.ar).to.eq('1');
                    chai.expect(pqParams['page-url']).to.eq(pageUrl);
                    chai.expect(pqParams['page-ref']).to.eq(prerenderUrl);
                    const { brInfo: prBrInfo, params: prParams } =
                        e2eUtils.getRequestParams(requests[1]);
                    chai.expect(prBrInfo.pr).to.eq('1');
                    chai.expect(prParams['page-url']).to.eq(pageUrl);
                    chai.expect(prParams['page-ref']).to.eq(prerenderUrl);
                })
                // Закрыть лишнюю вкладку
                .getTabIds()
                .then((result) => {
                    return this.browser.close(result[0]);
                })
        );
    });
});
