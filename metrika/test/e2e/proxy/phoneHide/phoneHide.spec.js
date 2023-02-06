const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Phone hide e2e proxy test', function () {
    // метричный домен нужен, чтобы пройти проверку origin источника postMessage
    const baseUrl = 'https://metrika.yandex.ru/test/phoneHide/phoneHide.hbs';
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('run phones hide twice (interface preview)', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phhide: ['72223334455'],
                                    },
                                },
                            },
                            function () {
                                window.req = [];
                                serverHelpers.collectRequests(
                                    1000,
                                    (requests) => {
                                        window.req =
                                            window.req.concat(requests);
                                    },
                                    options.regexp.defaultRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });

                                // init preview
                                window.postMessage(
                                    JSON.stringify({
                                        action: 'appendremote',
                                        resource:
                                            'https://yastatic.net/s3/metrika/1/form_selector/phone_ru.js',
                                        id: 'form-selector',
                                        inline: true,
                                        version: '2',
                                        data: '*',
                                    }),
                                    '*',
                                );
                                done();
                            },
                        );
                    },
                    counterId,
                }),
            )
            .executeAsync((done) => {
                const phone = document.getElementById('phone2');
                const previousLen = phone.children.length;
                window.Ya._metrika._u.phone.hidePhones();

                setTimeout(() => {
                    done([previousLen, phone.children.length]);
                }, 500);
            })
            .then(({ value: [previous, current] }) => {
                chai.expect(previous).to.be.eq(0);
                // проверяем, что внутри появилась какая-то верстка
                chai.expect(current).to.be.greaterThan(
                    0,
                    'should replace second phone',
                );
            });
    });
});
