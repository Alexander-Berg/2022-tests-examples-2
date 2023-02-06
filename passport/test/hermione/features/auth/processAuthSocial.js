const pages = require('../../utils/passportPages');
const {
    authSocialBlock,
    authSocialBlockSecondaryProviders,
    SocialSuggestRegisterSocial,
    socialModeChoose
} = require('../../page-objects/auth');
const {mailOAuth} = require('../../page-objects/social');
const {setInputValue} = require('../../helpers/ui');
// const {deleteAccount} = require('../../helpers/api/passport/delete');
const {getMailAccountData} = require('../../helpers/social');
const {delay} = require('../../utils/utils');

async function processAuthSocial(browser) {
    const mailAccountData = await getMailAccountData();

    await browser.url(`${pages.AUTH.getUrl()}`);
    await browser.yaWaitForVisible(authSocialBlock());
    await browser.click(authSocialBlock.moreBtn());
    await browser.yaWaitForVisible(authSocialBlockSecondaryProviders());
    await browser.click(authSocialBlockSecondaryProviders.moreBtn());

    const tabIds = await browser.getTabIds();

    await browser.switchTab(tabIds[1]);
    await browser.yaWaitForVisible(mailOAuth.form());
    await setInputValue(browser, mailOAuth.loginInput(), mailAccountData.login);
    await setInputValue(browser, mailOAuth.passwordInput(), mailAccountData.password);
    await browser.click(mailOAuth.submit());
    await browser.switchTab(tabIds[0]);
    await delay(2000);

    if (await browser.isVisible(socialModeChoose())) {
        // TODO воспроизвести этот кейс и разобраться как брать uid

        // const users = await browser.findElements('css selector', socialModeChoose.profile());

        // for (const user of users) {
        //     console.log(await user.getAttribute('data-uid'));
        //     await deleteAccount(user.uid);
        // }

        throw new Error('cleanup after last run');
    } else {
        if (await browser.isVisible(SocialSuggestRegisterSocial())) {
            await browser.yaWaitForVisible(SocialSuggestRegisterSocial());
            await browser.click(SocialSuggestRegisterSocial.registerButton());
        }
    }

    await delay(3000);
    await browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
}

module.exports = {
    processAuthSocial
};
