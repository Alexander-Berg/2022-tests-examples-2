const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe.skip('Input collector', function () {
    const baseUrl = 'https://yandex.ru/test/inputCollector/inputCollector.hbs';
    const counterId = 26302566;

    const phonesData = {
        elementId: 'telTestInput',
        validValues: ['8(123) 123-22-33', '8(12345) 123-22-33'],
        invalidValues: [
            '+7 (12) 31 23',
            '7123123',
            '8(abc) 123-22-33',
            '8(12345) 12345-222-333',
            'a@yandex.ru',
        ],
        matchRegex: /a\(0\)b\(P\)c\(.+\)/,
    };

    const emailData = {
        elementId: 'emailTestInput',
        validValues: [
            'a@b.c',
            'a@ya.ru',
            'a@yandex.ru',
            'a@yandex.com.tr',
            'vasily_pupkin@yandex.ru',
        ],
        invalidValues: ['a@b', `vasily${'_pupkin'.repeat(15)}@yandex.ru`],
        matchRegex: /a\(1\)b\(P1\)c\(.+\)/,
    };

    function testFirstPartyMethod(browser, data) {
        const { elementId, validValues, invalidValues, matchRegex } = data;
        const allValues = validValues.concat(invalidValues);
        return browser
            .timeoutsAsyncScript(8000)
            .url(`${baseUrl}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Input collector page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 1,
                                    body: {
                                        settings: {
                                            cf: 1,
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            () => {
                                window.req = [];
                                serverHelpers.onRequest(function (request) {
                                    if (request.url.match(/watch\//)) {
                                        window.req.push(request);
                                    }
                                });

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });

                                done();
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(() =>
                allValues.reduce(
                    (acc, item) =>
                        acc.setValue(`#${elementId}`, item).click('h1'),
                    browser,
                ),
            )
            .pause(6000)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        done(window.req);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(({ value: request }) => {
                const parsedRequests = request.map(e2eUtils.getRequestParams);
                const [, ...receivedParams] = parsedRequests;
                chai.expect(receivedParams).to.be.lengthOf(validValues.length);
                receivedParams.forEach((params) => {
                    chai.expect(params.brInfo.pa).to.eq('1');
                    const paramsInfo = params.siteInfo.__ym.fi;
                    chai.expect(paramsInfo).to.match(matchRegex);
                });
            });
    }

    it('sends encoded phones for inputs with type "tel"', function () {
        return testFirstPartyMethod(this.browser, phonesData);
    });

    it('sends encoded emails for inputs with type other than "tel"', function () {
        return testFirstPartyMethod(this.browser, emailData);
    });

    it('sends encoded emails and phones for inputs with type other than "tel"', function () {
        const data = {
            elementId: 'emailTestInput',
            validValues: [...phonesData.validValues, ...emailData.validValues],
            invalidValues: [
                ...phonesData.invalidValues.filter(
                    (item) => !item.includes('@'),
                ),
                ...emailData.invalidValues,
            ],
            matchRegex: /a\((0|1)\)b\(P1\)c\(.+\)/,
        };

        return testFirstPartyMethod(this.browser, data);
    });
});
