const PO = require('../../../../page-objects/auth/reg');
const {getRandomPassword} = require('../../../../utils/utils');
const {setInputValue} = require('../../../../helpers/ui');

const WAIT_ELEMENT_TIMEOUT = 500;

async function processPasswordScreen(browser) {
    await browser.yaWaitForVisible(PO.passwordSignUpInDaHouse(), WAIT_ELEMENT_TIMEOUT);

    const password = getRandomPassword(12);

    await setInputValue(browser, PO.passwordSignUpInDaHouse.passwordInput(), password);

    await browser.yaWaitForVisible(PO.passwordSignUpInDaHouse.nextButton());
    await browser.click(PO.passwordSignUpInDaHouse.nextButton());
}

module.exports = {
    processPasswordScreen
};
