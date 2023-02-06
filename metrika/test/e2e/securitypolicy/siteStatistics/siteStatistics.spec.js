const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('site statistics test', function () {
    const counterId = 26302;

    it('should init metrika iframe', async function () {
        const baseUrl =
            'https://example.com/test/siteStatistics/siteStatistics.hbs';
        await this.browser.url(baseUrl).then(
            e2eUtils.provideServerHelpers(this.browser, {
                cb(serverHelpers, options, done) {
                    serverHelpers.addRule(
                        {
                            regex: `/watch/${options.counterId}`,
                            body: {
                                settings: {
                                    sm: 1,
                                },
                            },
                        },
                        () => {
                            new Ya.Metrika2(options.counterId);
                            done();
                        },
                    );
                },
                counterId,
            }),
        );

        await this.browser.waitForVisible('#__ym_wv_ign__opener', 3000);

        await this.browser.click('#__ym_wv_ign__opener');

        await this.browser.waitForVisible('.__ym_wv_ign iframe', 2000);
        await this.browser.waitForVisible('#__ym_wv_ign__closer', 2000);

        await this.browser.click('#__ym_wv_ign__closer');

        await this.browser.waitForVisible('.__ym_wv_ign iframe', 2000, true);
        await this.browser.waitForVisible('#__ym_wv_ign__closer', 2000, true);
    });

    it('should destruct metrika iframe', async function () {
        const baseUrl =
            'https://example.com/test/siteStatistics/disabledFrameSrc.hbs';
        await this.browser.url(baseUrl).then(
            e2eUtils.provideServerHelpers(this.browser, {
                cb(serverHelpers, options, done) {
                    serverHelpers.addRule(
                        {
                            regex: `/watch/${options.counterId}`,
                            body: {
                                settings: {
                                    sm: 1,
                                },
                            },
                        },
                        () => {
                            window.addEventListener(
                                'securitypolicyviolation',
                                (e) => {
                                    window.__blockedFrameURI = e.blockedURI;
                                },
                            );
                            new Ya.Metrika2(options.counterId);
                            done();
                        },
                    );
                },
                counterId,
            }),
        );
        await this.browser.waitForExist('.__ym_wv_ign', 1000, true);

        // проверяем что iframe вообще был на странице
        // через .waitForExist не получается, так-как код отрабатывает слишком быстро и проверка не успевает отрабатывать
        const { value: blockedFrameURI } = await this.browser.execute(
            function () {
                return window.__blockedFrameURI;
            },
        );
        chai.expect(blockedFrameURI).equal('https://metrika.yandex.ru');
    });
});
