const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 9021294;

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    const checkSelect = (browser, isProto) => {
        return (
            browser
                .timeoutsAsyncScript(10000)
                .url(
                    `${baseUrl}webvisor2-chunk.hbs${
                        isProto ? '' : '?_ym_debug=1'
                    }`,
                )
                .getText('h1')
                .then((innerText) => {
                    const text = innerText;
                    chai.expect(text).to.be.equal('Chunk page');
                })
                .then(
                    e2eUtils.provideServerHelpers(browser, {
                        cb(serverHelpers, options, done) {
                            window.req = [];
                            serverHelpers.collectRequests(
                                5000,
                                (requests) => {
                                    window.req = window.req.concat(requests);
                                    done();
                                },
                                options.regexp.webvisorRequestRegEx,
                            );
                            new Ya.Metrika2({
                                id: options.counterId,
                                webvisor: true,
                            });
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(browser))
                .moveToObject('h1', 50, 20)
                .pause(100)
                .doDoubleClick()
                .pause(500)
                .moveToObject('h3', 50, 20)
                .pause(100)
                .doDoubleClick()
                // .saveScreenshot('./test/e2e/report/info.png')
                // TODO stopRecord
                .pause(3000)
                .execute(function () {
                    return {
                        reqs: window.req,
                    };
                })
                .then(e2eUtils.handleRequest(browser))
                .then(({ value: { reqs: requests } }) => {
                    const requestsInfo = requests.map(
                        e2eUtils.getRequestParams,
                    );
                    const bufferData = requestsInfo.reduce((acc, item) => {
                        return acc.concat(item.body);
                    }, []);
                    const selectionData = bufferData.reduce((acc, event) => {
                        if (
                            event.type === 'event' &&
                            event.data.type === 'selection'
                        ) {
                            return acc.concat(event.data);
                        }

                        return acc;
                    }, []);
                    chai.expect(selectionData).to.be.lengthOf(1);
                    const [{ meta: selectionEvent }] = selectionData;
                    chai.expect(selectionEvent.end).to.be.eq(5);
                    chai.expect(selectionEvent.start).to.be.oneOf([
                        0,
                        undefined,
                    ]);
                    chai.expect(selectionEvent.startNode).to.be.eq(
                        selectionEvent.endNode,
                    );
                })
        );
    };

    it.skip('records select (proto)', function () {
        return checkSelect(this.browser, true);
    });

    it.skip('records select (json)', function () {
        return checkSelect(this.browser, false);
    });
});
