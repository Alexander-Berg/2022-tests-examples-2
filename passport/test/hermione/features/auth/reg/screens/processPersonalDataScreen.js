const {expect} = require('chai');
const PO = require('../../../../page-objects/auth/reg');
const {randomAlphanumeric, delay} = require('../../../../utils/utils');
const {setInputValue} = require('../../../../helpers/ui');

const WAIT_BEFORE_CLICK_TIMEOUT = 500;

async function processPersonalDataScreen(browser) {
    await browser.yaWaitForVisible(PO.personalDataSignUpInDaHouse(), 'personalDataSignUpInDaHouse not visible');
    expect(await browser.isVisible(PO.personalDataSignUpInDaHouse.firstNameInputHint())).to.equal(false);
    expect(await browser.isVisible(PO.personalDataSignUpInDaHouse.lastNameInputHint())).to.equal(false);

    const firstName = randomAlphanumeric(6);

    await setInputValue(browser, PO.personalDataSignUpInDaHouse.firstNameInput(), firstName);

    const secondName = randomAlphanumeric(6);

    await setInputValue(browser, PO.personalDataSignUpInDaHouse.lastNameInput(), secondName);

    await delay(WAIT_BEFORE_CLICK_TIMEOUT);
    await browser.yaWaitForVisible(PO.personalDataSignUpInDaHouse.nextButton());
    await browser.click(PO.personalDataSignUpInDaHouse.nextButton());
}

module.exports = {
    processPersonalDataScreen
};
