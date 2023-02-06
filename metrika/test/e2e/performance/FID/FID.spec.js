const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('FID', function () {
    const counterId = 123;
    const TOO_BIG_FID = 10;
    const url = `${e2eUtils.baseUrl}/test/FID/FID.hbs`;
    it('is low without webvisor', function () {
        return this.browser
            .timeoutsAsyncScript(1000)
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        done();
                    },
                    counterId,
                }),
            )
            .keys('ArrowLeft')
            .click('#button')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        setTimeout(() => {
                            done(window.FID);
                        }, 100);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value).to.not.be.NaN;
                chai.expect(value).to.be.below(TOO_BIG_FID);
            });
    });

    it('is low for webvisor', function () {
        return this.browser
            .timeoutsAsyncScript(1000)
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                        done();
                    },
                    counterId,
                }),
            )
            .keys('ArrowLeft')
            .click('#button')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        done(window.FID);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value).to.not.be.NaN;
                chai.expect(value).to.be.below(TOO_BIG_FID);
            });
    });
});
