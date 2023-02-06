const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { findNodeWithAttribute, baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 1203432;

    const checkInputsData = function (browser, isProto, isEu) {
        return browser
            .url(`${baseUrl}input.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Inputs page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            webvisor: {
                                                forms: 1,
                                            },
                                            eu: options.isEu ? '1' : undefined,
                                        },
                                        userData: {},
                                    },
                                },
                            ],
                            () => {
                                if (options.isProto) {
                                    document.cookie = '_ym_debug=""';
                                }
                                window.req = [];
                                serverHelpers.onRequest(function (request) {
                                    if (request.url.match(/webvisor\//)) {
                                        window.req.push(request);
                                    }
                                });
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    webvisor: true,
                                });
                                done();
                            },
                        );
                    },
                    counterId,
                    isProto,
                    isEu,
                }),
            )
            .pause(1000)
            .setValue('#normalInput', 'value')
            .setValue('#password', 'pwd')
            .setValue('#card', '123')
            .click('#checkbox')
            .click('#button')
            .pause(4000)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        done(window.req);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const page = visorData.find((event) => event.type === 'page');
                const events = visorData.filter(
                    (event) => event.type === 'event',
                );
                const normalInput = findNodeWithAttribute(page, 'normalInput');
                const password = findNodeWithAttribute(page, 'password');
                const progInput = findNodeWithAttribute(page, 'progInput');
                const checkbox = findNodeWithAttribute(page, 'checkbox');
                const creditCardInput = findNodeWithAttribute(page, 'card');

                const normalInputChanges = events
                    .filter(
                        (event) =>
                            event.data.type === 'change' &&
                            event.data.target === normalInput.id,
                    )
                    .map((event) => event.data.meta.value);
                chai.expect(normalInputChanges).to.deep.equal([
                    'v',
                    'va',
                    'val',
                    'valu',
                    'value',
                ]);

                const progInputChange = events.find(
                    (event) =>
                        event.data.type === 'change' &&
                        event.data.target === progInput.id,
                );
                chai.expect(progInputChange.data.meta.value).to.deep.equal(
                    '123',
                );

                const passwordInputChanges = events
                    .filter(
                        (event) =>
                            event.data.type === 'change' &&
                            event.data.target === password.id,
                    )
                    .map((event) => event.data.meta.value);
                chai.expect(passwordInputChanges).to.deep.equal([
                    '•',
                    '••',
                    '•••',
                ]);

                const creditCardInputChanges = events
                    .filter(
                        (event) =>
                            event.data.type === 'change' &&
                            event.data.target === creditCardInput.id,
                    )
                    .map((event) => {
                        chai.expect(
                            event.data.meta.hidden,
                            'private info field',
                        ).to.equal(true);
                        return event.data.meta.value;
                    });
                chai.expect(creditCardInputChanges).to.deep.equal(
                    isEu ? ['•', '••', '•••'] : ['1', '12', '123'],
                );

                const checkboxChangeEvents = events.filter(
                    (event) =>
                        event.data.type === 'change' &&
                        event.data.target === checkbox.id,
                );
                chai.expect(checkboxChangeEvents.length).to.equal(2);
                chai.expect(
                    checkboxChangeEvents[0].data.meta.checked,
                    'checkbox click',
                ).to.equal(false);
                chai.expect(
                    checkboxChangeEvents[1].data.meta.checked,
                    'checkbox programmical',
                ).to.equal(true);
            });
    };

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    it('records inputs (proto)', function () {
        return checkInputsData(this.browser, true, false);
    });

    it('records inputs (proto/eu)', function () {
        return checkInputsData(this.browser, true, true);
    });

    it('records inputs (json)', function () {
        return checkInputsData(this.browser, false, false);
    });

    it('records inputs (json/eu)', function () {
        return checkInputsData(this.browser, false, true);
    });
});
