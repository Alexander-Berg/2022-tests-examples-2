const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('First party method test', function () {
    const baseUrl =
        'https://yandex.ru/test/firstPartyMethod/firstPartyMethod.hbs';
    const counterId = 26302566;

    function testFirstPartyMethod(browser, data) {
        return browser
            .timeoutsAsyncScript(6000)
            .url(`${baseUrl}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('FirstPartyMethod page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        options.data.forEach((entry) => {
                            counter.firstPartyParams(entry.toSend);
                        });
                    },
                    counterId,
                    data,
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(({ value: request }) => {
                chai.expect(request).to.be.lengthOf(data.length + 1);
                const parsedRequests = request.map(e2eUtils.getRequestParams);
                const [, ...receivedParams] = parsedRequests;
                receivedParams.forEach((params, i) => {
                    chai.expect(params.brInfo.pa).to.be.eq('1');
                    const paramsInfo = params.siteInfo;
                    chai.expect(paramsInfo).to.be.deep.eq(data[i].toExpect);
                });
            });
    }

    it('send encoded data', function () {
        return testFirstPartyMethod(this.browser, [
            {
                toSend: {
                    first_name: 'first Name',
                    last_name: 'smith',
                    phone_number: '123123',
                    email: 'smith@mail.ru',
                    yandex_cid: '123123',
                    obj: {
                        yandex_cid: '123123',
                    },
                },
                toExpect: {
                    __ym: {
                        fpp: [
                            [
                                'email',
                                'nHYT6qT52DDtkW24n4dTAGVypof4JxFpouc+L4tg6Cs=',
                            ],
                            [
                                'first_name',
                                'wCI+WaiSmEmwGinYfVzcZBBZT1ggPTDPubNDg+fN91M=',
                            ],
                            [
                                'last_name',
                                'ZieDX5iOLF5QUz1JEWMHLT9PQfXIsEYwFQ3rs3Isot0=',
                            ],
                            [
                                'obj',
                                [
                                    [
                                        'yandex_cid',
                                        'lsrjXOipsCRBeL8o5JZsLOG4OFcjqWprg4hYzdbKCh4=',
                                    ],
                                ],
                            ],
                            [
                                'phone_number',
                                'lsrjXOipsCRBeL8o5JZsLOG4OFcjqWprg4hYzdbKCh4=',
                            ],
                            ['yandex_cid', '123123'],
                        ],
                    },
                },
            },
        ]);
    });

    it('normalize arbitrary phones then send encoded', function () {
        const phonesData = [
            ' 8(123) 12-3 ',
            '8-12-31-23',
            '+7 (12) 31 23',
            '7123123',
        ].map((phone) => ({
            toSend: { phone_number: phone },
            toExpect: {
                __ym: {
                    fpp: [
                        [
                            'phone_number',
                            'l2Ix4jrQpdItPokF/6R5yoJWP2Lu0hpFsMrd2w6YQbg=',
                        ],
                    ],
                },
            },
        }));

        return testFirstPartyMethod(this.browser, phonesData);
    });

    it('for emails replace yandex domains with "yandex.ru" and send encoded', function () {
        const yandexEmailData = ['ya.ru', 'yandex.com', 'yandex.com.tr'].map(
            (domain) => ({
                toSend: { email: `smith@${domain}` },
                toExpect: {
                    __ym: {
                        fpp: [
                            [
                                'email',
                                'bCTW0/Qge17uQzbnmu4QLVZ6LczL7j1jvPBXFxu8DBg=',
                            ],
                        ],
                    },
                },
            }),
        );

        return testFirstPartyMethod(this.browser, yandexEmailData);
    });

    it('for emails replace google domains with "gmail.com" and send encoded', function () {
        const googleEmailData = ['googlemail.com', 'gmail.com'].map(
            (domain) => ({
                toSend: { email: `smith@${domain}` },
                toExpect: {
                    __ym: {
                        fpp: [
                            [
                                'email',
                                'JV/3SiHjyKRmEcG3w7Le9AXiHicbS5/HPiB7qIWn7uQ=',
                            ],
                        ],
                    },
                },
            }),
        );

        return testFirstPartyMethod(this.browser, googleEmailData);
    });

    it('for emails with yandex domains replace dots in name with dashes and send encoded', function () {
        const yandexEmailData = ['ryan.smith', 'ryan-smith'].map((name) => ({
            toSend: { email: `${name}@yandex.ru` },
            toExpect: {
                __ym: {
                    fpp: [
                        [
                            'email',
                            '88ws7ui7D7NFuqm7EkNFbjpAdVErwiDnMvc8Pgd2LaE=',
                        ],
                    ],
                },
            },
        }));

        return testFirstPartyMethod(this.browser, yandexEmailData);
    });

    it('for emails with google domains remove dots and suffix in name and send encoded', function () {
        const googleEmailData = [
            'ryan.smith',
            'ryansmith',
            'ryansmith+commercial',
        ].map((name) => ({
            toSend: { email: `${name}@gmail.com` },
            toExpect: {
                __ym: {
                    fpp: [
                        [
                            'email',
                            'N3UmOyVN4vGfs3sdvD2c4zMFZl0dgrj4vgAON0hlqt8=',
                        ],
                    ],
                },
            },
        }));

        return testFirstPartyMethod(this.browser, googleEmailData);
    });
});
