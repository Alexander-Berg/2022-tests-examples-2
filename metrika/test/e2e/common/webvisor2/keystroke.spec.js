const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    const baseUrl = 'test/webvisor2/webvisor2-keystroke.hbs';
    const counterId = 123;
    beforeEach(function () {
        this.browser.timeoutsAsyncScript(15000);
    });

    it('send pressed keys', function () {
        return (
            this.browser
                .url(baseUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.req = [];
                            serverHelpers.onRequest(function (request) {
                                if (request.url.match(/webvisor\//)) {
                                    window.req.push(request);
                                    done();
                                }
                            });
                            new Ya.Metrika2({
                                id: options.counterId,
                                webvisor: true,
                            });
                        },
                        counterId,
                    }),
                )
                // ignore simple key
                .keys('a')
                .pause(100)
                // ignore password + ym-disable-keys
                .click('#ignored')
                .keys('ArrowLeft')
                .pause(100)
                // ignore input with shift
                .click('#input')
                .keys(['Shift'])
                .keys(['Control'])
                .keys(['Control'])
                .keys(['Shift'])
                // single special key
                .click('#button')
                .keys('ArrowRight')
                .pause(100)
                // ctrl + shift
                .keys(['Shift'])
                .keys(['Control'])
                .keys(['Control'])
                .keys(['Shift'])
                .pause(3000)
                .execute(function () {
                    return {
                        reqs: window.req,
                        macOs:
                            window.navigator.appVersion.indexOf('Mac') !== -1,
                    };
                })
                .then(({ value: { reqs: requests, macOs } }) => {
                    const requestsInfo = requests.map(
                        e2eUtils.getRequestParams,
                    );
                    const bufferData = requestsInfo.reduce((acc, item) => {
                        return acc.concat(item.body);
                    }, []);
                    const keystrokeData = bufferData.reduce((acc, event) => {
                        if (
                            event.type === 'event' &&
                            event.data.type === 'keystroke'
                        ) {
                            return acc.concat(event.data.meta.keystrokes);
                        }

                        return acc;
                    }, []);
                    const expectedData = [
                        { id: 39, isMeta: false, key: '&rarr;' },
                        {
                            id: 16,
                            isMeta: macOs,
                            key: macOs ? '&#8679;' : 'Shift',
                            modifier: 'shift',
                        },
                        {
                            id: 17,
                            isMeta: macOs,
                            key: macOs ? '&#8963;' : 'Ctrl',
                            modifier: 'ctrl',
                        },
                    ];
                    chai.expect(keystrokeData).to.deep.equal(expectedData);
                })
        );
    });

    it('keystroke captor / send keystrokes - json serialize', function () {
        return this.browser
            .url(`${baseUrl}?_ym_debug=1`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.req = [];
                        serverHelpers.onRequest(function (request) {
                            if (request.url.match(/webvisor\//)) {
                                window.req.push(request);
                                done();
                            }
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                    },
                    counterId,
                }),
            )
            .keys('ArrowLeft')
            .pause(3000)
            .execute(function () {
                return window.req;
            })
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const keystrokeData = visorData.reduce(
                    (acc, { data: { type, meta } }) => {
                        if (type === 'keystroke') {
                            acc.push(meta);
                        }
                        return acc;
                    },
                    [],
                );

                chai.expect(keystrokeData).to.have.lengthOf(1);
                chai.expect(keystrokeData[0]).to.deep.equal([
                    { id: 37, isMeta: false, key: '&larr;' },
                ]);
            });
    });
});
