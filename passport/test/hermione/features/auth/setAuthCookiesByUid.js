const pages = require('../../utils/passportPages');
const {setAuthCookies} = require('../../helpers/api/passport/auth');

async function setAuthCookiesByUid(browser, uid) {
    await setAuthCookies(browser, uid);
    await browser.url(`${pages.PROFILE.getUrl()}`);
    await browser.yaShouldBeAtUrl(pages.PROFILE.getUrl());
}

module.exports = {
    setAuthCookiesByUid
};
