const baseUrl = 'test/webvisor2/';

const findNodeBySnapshot = (page, snapshot) => {
    return page.data.content.find((nodeInfo) =>
        Object.keys(snapshot).every((key) => nodeInfo[key] === snapshot[key]),
    );
};

const findNodeWithAttribute = (page, value, attribute = 'id') => {
    return page.data.content.find(
        (nodeInfo) => (nodeInfo.attributes || {})[attribute] === value,
    );
};

const clearBrowser = (browser) => {
    return browser
        .deleteCookie()
        .timeoutsAsyncScript(15000)
        .url(baseUrl)
        .executeAsync(function (done) {
            // eslint-disable-next-line no-undef
            localStorage.clear();
            done();
        });
};

module.exports = {
    clearBrowser,
    baseUrl,
    findNodeBySnapshot,
    findNodeWithAttribute,
};
