const {expect} = require('chai');
const {getRandomFreeLogin} = require('../../../../utils/utils');
const PO = require('../../../../page-objects/auth/reg');
const {setInputValue} = require('../../../../helpers/ui');

async function processLoginScreen(browser) {
    await browser.yaWaitForVisible(PO.loginSignUp());
    await browser.yaWaitForVisible(PO.loginSignUp.loginInput());
    expect(await browser.isVisible(PO.loginSignUp.loginInputError())).to.equal(false);

    const login = await getRandomFreeLogin('yndx-');

    await setInputValue(browser, PO.loginSignUp.loginInput(), login);

    // TODO найти гарантированный способ проверить что поле валидно перед нажатием далее
    // await delay(2000); // ждём валидацию
    // expect(await browser.isVisible(PO.loginSignUp.loginInputError())).to.equal(false);
    await browser.click(PO.loginSignUp.nextButton());
}

module.exports = {
    processLoginScreen
};
