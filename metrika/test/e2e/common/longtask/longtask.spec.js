const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe.skip('Longtask e2e test', function () {
    const baseUrl = 'test/longtask/longtask.hbs';
    const counterId = 26302566;

    it('should send lt brinfo flag', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            5000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        setTimeout(() => {
                            const container =
                                document.querySelector('#container');
                            for (let i = 0; i < 3000; i += 1) {
                                const el = document.createElement('div');
                                el.innerText = 'Something something';
                                container.appendChild(el);
                            }
                            counter.params([{ param1: 1 }, { param2: 2 }]);
                        }, 1000);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                let success = false;
                requests.forEach((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    success = success || typeof brInfo.lt === 'number';
                });
                chai.assert(success);
            });
    });
});
