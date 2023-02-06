const PO = require('../../../../page-objects/auth/reg');
const {randomAlphanumeric} = require('../../../../utils/utils');

async function processSqSaScreen(browser) {
    await browser.yaSetValue(PO.securityQuestionSecurityAnswerScreen.answerInput(), randomAlphanumeric(6));
    await browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());
}

module.exports = {
    processSqSaScreen
};
