const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('External and download links', function () {
    const pathToTestPage = 'test/logExternalLinks/logExternalLinks.hbs';
    const baseUrl = `https://yandex.ru/${pathToTestPage}?_ym_debug=1`;

    const extLinkUrl = 'https://yandex.com/test/logExternalLinks/extPage.hbs';
    const extDownloadLinkUrl =
        'https://yandex.com/test/logExternalLinks/music.mp3';
    const intDownloadLinkUrl =
        'https://yandex.ru/test/logExternalLinks/music.mp3';

    const counterId = 20302;

    const EXT_LINK_MESSAGE = `Ext link. Counter ${counterId}. Url: ${extLinkUrl}`;
    const EXT_DOWNLOAD_LINK_MESSAGE = `Ext link - File. Counter ${counterId}. Url: ${extDownloadLinkUrl}`;
    const INT_DOWNLOAD_LINK_MESSAGE = `File. Counter ${counterId}. Url: ${intDownloadLinkUrl}`;

    function checkRequestsInfoContains(requests, key) {
        const watchRequests = requests.filter((req) => {
            return req.headers['x-host'] === 'mc.yandex.ru';
        });
        chai.expect(watchRequests).to.have.lengthOf(2);

        const [pageView, linkTrack] = watchRequests;
        const pageViewRequestParams = e2eUtils.getRequestParams(pageView);
        const linkTrackRequestParams = e2eUtils.getRequestParams(linkTrack);

        chai.expect(pageViewRequestParams.brInfo[key]).to.be.undefined;
        chai.expect(linkTrackRequestParams.brInfo[key]).to.equal('1');
    }

    function checkLogsContain(extra, msg) {
        const extLinkLogs = extra.log
            .map((l) => l.message)
            .filter((message) => message.includes(msg));

        chai.expect(extLinkLogs).to.have.lengthOf(1);
    }

    function testExtLinkWith(args) {
        const {
            ctx,
            buttonSelector,
            buttonText,
            expectedRequestInfo,
            expectedLogMessage,
        } = args;

        return ctx.browser
            .getText(buttonSelector)
            .then((innerText) => {
                chai.expect(buttonText).to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(ctx.browser, {
                    cb(serverHelpers, options, done) {
                        window.requests = [];
                        serverHelpers.onRequest(function (request) {
                            window.requests.push(request);
                        }, options.regexp.defaultRequestRegEx);

                        new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        done(true);
                    },
                    counterId,
                }),
            )
            .click(buttonSelector)
            .pause(1000)
            .execute(function () {
                return window.requests;
            })
            .then(e2eUtils.handleRequest(ctx.browser))
            .then(({ value: requests, extra }) => {
                checkRequestsInfoContains(requests, expectedRequestInfo);
                checkLogsContain(extra, expectedLogMessage);
            });
    }

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Handles external links and logs to console', function () {
        return testExtLinkWith({
            ctx: this,
            buttonSelector: '#ext-link',
            buttonText: 'External link',
            expectedRequestInfo: 'ln',
            expectedLogMessage: EXT_LINK_MESSAGE,
        });
    });

    it('Handles external download links and logs to console', function () {
        return testExtLinkWith({
            ctx: this,
            buttonSelector: '#ext-download-link',
            buttonText: 'External download link',
            expectedRequestInfo: 'dl',
            expectedLogMessage: EXT_DOWNLOAD_LINK_MESSAGE,
        });
    });

    it('Handles internal download links and logs to console', function () {
        return testExtLinkWith({
            ctx: this,
            buttonSelector: '#int-download-link',
            buttonText: 'Internal download link',
            expectedRequestInfo: 'dl',
            expectedLogMessage: INT_DOWNLOAD_LINK_MESSAGE,
        });
    });
});
