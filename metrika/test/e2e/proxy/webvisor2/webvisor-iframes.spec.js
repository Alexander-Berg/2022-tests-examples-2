const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    const baseUrl = 'https://yandex.ru/test/webvisor2/';
    const counterId = 123;

    const checkVisorData = (visorData) => {
        const page = visorData.find(
            ({ type, data }) => type === 'page' && !data.frameId,
        );
        const iframePages = visorData.filter(
            ({ type, data }) => type === 'page' && data.frameId,
        );
        chai.expect(page, 'regular page').to.be.ok;
        chai.expect(iframePages.length, 'has 3 frames').to.equal(3);

        const blankIframeNodeId = page.data.content.find(
            (nodeInfo) =>
                nodeInfo.name === 'iframe' &&
                (nodeInfo.attributes || {}).id === 'blank',
        ).id;
        const sameDomainIframeNodeId = page.data.content.find(
            (nodeInfo) =>
                nodeInfo.name === 'iframe' &&
                (nodeInfo.attributes || {}).id === 'same',
        ).id;
        const trustedDomainIframeNodeId = page.data.content.find(
            (nodeInfo) =>
                nodeInfo.name === 'iframe' &&
                (nodeInfo.attributes || {}).id === 'trusted',
        ).id;

        chai.expect(
            iframePages.find(
                (iframePage) => iframePage.data.frameId === blankIframeNodeId,
            ),
            'blank iframe id corresponds to the correct node',
        ).to.be.ok;
        chai.expect(
            iframePages.find(
                (iframePage) =>
                    iframePage.data.frameId === sameDomainIframeNodeId,
            ),
            'same domain iframe id corresponds to the correct node',
        ).to.be.ok;
        chai.expect(
            iframePages.find(
                (iframePage) =>
                    iframePage.data.frameId === trustedDomainIframeNodeId,
            ),
            'trusted domain iframe id corresponds to the correct node',
        ).to.be.ok;
    };

    function checkFramesFromMultipleSources(proto) {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(`${baseUrl}webvisor2-frames.hbs?${proto ? '' : '_ym_debug=1'}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        if (options.proto) {
                            document.cookie = '_ym_debug=""';
                        }

                        serverHelpers.collectRequestsForTime(8000, '.*');
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                            childIframe: true,
                            trustedDomains: ['example.com'],
                        });
                    },
                    counterId,
                    proto,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then(checkVisorData);
    }

    it('Records frames (json)', function () {
        return checkFramesFromMultipleSources.call(this, false);
    });

    it('Records frames (proto)', function () {
        return checkFramesFromMultipleSources.call(this, true);
    });
});
