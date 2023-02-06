const {expect} = require('chai');
const PO = require('../../../../page-objects/auth/reg');

const WAIT_ELEMENT_TIMEOUT = 500;

async function processCurrentPasswordScreen(browser, user) {
    await browser.yaWaitForVisible(PO.currentPasswordScreen(), WAIT_ELEMENT_TIMEOUT);
    browser.$(PO.currentPasswordScreen.passwordInput()).clearValue();
    await browser.yaSetValue(PO.currentPasswordScreen.passwordInput(), user.password);
    expect(await browser.getValue(PO.currentPasswordScreen.passwordInput())).to.equal(user.password);
    await browser.yaWaitForVisible(PO.currentPasswordScreen.nextButton());
    await browser.click(PO.currentPasswordScreen.nextButton());
}

module.exports = {
    processCurrentPasswordScreen
};
