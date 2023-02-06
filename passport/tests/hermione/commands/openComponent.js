module.exports = (browser) => async (id) => browser.url(`/iframe.html?id=${id}`);
