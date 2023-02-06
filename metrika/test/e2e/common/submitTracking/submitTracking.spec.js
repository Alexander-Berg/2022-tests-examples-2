const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Submit tracking test', function () {
    const baseUrl = 'test/submitTracking/submitTracking.hbs';
    const firstCounterId = 26302566;
    const secondCounterId = 26302567;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(6000).deleteCookie();
    });

    it('should send form goals', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.requests = [];
                        serverHelpers.onRequest(function (request) {
                            window.requests.push(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });
                        done(true);
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .click('#button1')
            .click('#button2')
            .click('#span3')
            .pause(1000)
            .execute(function () {
                return window.requests;
            })
            .then(({ value: requests }) => {
                const check = (data, counter = firstCounterId) => {
                    const form = e2eUtils.querystring(data);
                    chai.assert(
                        e2eUtils.findHit(
                            requests,
                            counter,
                            `${e2eUtils.formUrl}/?${form}`,
                        ),
                        `no form: ${form}`,
                    );
                };

                check({ i: 'form1', n: 'searchForm', p: 'F' });
                check({ i: 'form1', n: 'searchForm', p: 'F' }, secondCounterId);

                check({ i: 'form2', p: 'FA1' });

                check({ i: 'form3', p: 'FA2' });
            });
    });
});
