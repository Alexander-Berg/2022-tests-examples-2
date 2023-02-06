const expect = require('chai').expect;
const pages = require('../../../utils/passportPages');
const PO = require('../../../page-objects/auth/reg');
const {randomAlphanumeric, delay} = require('../../../utils/utils');
const {tryDeleteAccountAfterRun} = require('../../../helpers/api/passport/delete');
const {
    processCaptchaScreen,
    processLoginScreen,
    processPasswordScreen,
    processPersonalDataScreen
} = require('./screens');

const WAIT_ELEMENT_TIMEOUT = 5000;
const WAIT_BEFORE_CLICK_TIMEOUT = 500;

async function processEulaScreen(browser) {
    await browser.yaWaitForVisible(PO.eulaSignUp(), WAIT_ELEMENT_TIMEOUT);
    await browser.yaWaitForVisible(PO.eulaSignUp.nextButton());
    await browser.click(PO.eulaSignUp.nextButton());
}

async function processSQSAScreen(browser) {
    await browser.yaSetValue(PO.securityQuestionSecurityAnswerScreen.answerInput(), randomAlphanumeric(6));
    await browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());
}

async function checkIsProfilePage(browser) {
    await browser.yaWaitForVisible('[data-page-type="profile.passportv2"]');
    await browser.yaShouldBeAtUrl(pages.PROFILE);
}

describe('/auth/reg', function() {
    describe('ENTRY_REGISTER_PROCESS', function() {
        beforeEach(async function() {
            await this.browser.url(pages.AUTH_REG.getUrl());
        });
        it('should not show NO PHONE button', async function() {
            expect(await this.browser.isVisible(PO.phoneScreen.switchButton())).to.equal(false);
        });
    });
    describe('ENTRY_REGISTER_NO_PHONE_PROCESS', function() {
        beforeEach(async function() {
            await this.browser.url(`${pages.AUTH_REG.getUrl()}?test-id=488389`);
        });
        it('should show NO PHONE button', async function() {
            await this.browser.yaShouldBeVisible(PO.phoneScreen.switchButton());
            await this.browser.yaShouldHaveVisibleText(PO.phoneScreen.switchButton());
        });
        it('should show "security question security answer" screen by click on "no phone" button', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());
            await this.browser.yaShouldBeVisible(PO.securityQuestionSecurityAnswerScreen());
        });
        it(
            'should Complete registration with default question',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.click(PO.phoneScreen.switchButton());

                await this.browser.yaSetValue(
                    PO.securityQuestionSecurityAnswerScreen.answerInput(),
                    randomAlphanumeric(6)
                );

                await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

                await processCaptchaScreen(this.browser);
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await processPasswordScreen(this.browser);
                await processEulaScreen(this.browser);
                await checkIsProfilePage(this.browser);
            })
        );
        for (let i = 0; i <= 8; i++) {
            it(
                `should Complete registration with question number ${i}`,
                tryDeleteAccountAfterRun(async function() {
                    await this.browser.click(PO.phoneScreen.switchButton());
                    await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
                    const questions = await this.browser.findElements(
                        'css selector',
                        PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
                    );

                    const question = questions[i];

                    await this.browser.click(question);
                    await this.browser.yaSetValue(
                        PO.securityQuestionSecurityAnswerScreen.answerInput(),
                        randomAlphanumeric(6)
                    );

                    await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

                    await processCaptchaScreen(this.browser);
                    await processPersonalDataScreen(this.browser);
                    await processLoginScreen(this.browser);
                    await processPasswordScreen(this.browser);
                    await processEulaScreen(this.browser);
                    await checkIsProfilePage(this.browser);
                })
            );
        }
        it(
            'Should complete registration with custom question',
            tryDeleteAccountAfterRun(async function() {
                await this.browser.click(PO.phoneScreen.switchButton());
                await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
                const questions = await this.browser.findElements(
                    'css selector',
                    PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
                );

                const question = questions[questions.length - 1];

                await this.browser.click(question);
                await this.browser.yaSetValue(
                    PO.securityQuestionSecurityAnswerScreen.questionInput(),
                    randomAlphanumeric(6)
                );
                await this.browser.yaSetValue(
                    PO.securityQuestionSecurityAnswerScreen.answerInput(),
                    randomAlphanumeric(6)
                );

                await delay(WAIT_BEFORE_CLICK_TIMEOUT);
                await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

                await processCaptchaScreen(this.browser);
                await processPersonalDataScreen(this.browser);
                await processLoginScreen(this.browser);
                await processPasswordScreen(this.browser);
                await processEulaScreen(this.browser);
                await checkIsProfilePage(this.browser);
            })
        );
        for (let i = 0; i <= 8; i++) {
            it(`should show SA error if answer is not wrote with question number ${i}`, async function() {
                await this.browser.click(PO.phoneScreen.switchButton());
                await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
                const questions = await this.browser.findElements(
                    'css selector',
                    PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
                );

                const question = questions[i];

                await this.browser.click(question);

                await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

                await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.answerErrorText());
            });
        }
        it('should show SA error if answer is not wrote with default question', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

            await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.answerErrorText());
        });
        it('should show SQ error if question is not wrote with custom security question', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
            const questions = await this.browser.findElements(
                'css selector',
                PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
            );

            const question = questions[questions.length - 1];

            await this.browser.click(question);

            await this.browser.yaSetValue(PO.securityQuestionSecurityAnswerScreen.answerInput(), randomAlphanumeric(6));

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

            const questionErrorTexts = await this.browser.findElements(
                'css selector',
                PO.securityQuestionSecurityAnswerScreen.answerErrorText()
            );

            expect(questionErrorTexts.length).to.equal(0);
            await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.questionErrorText());
        });
        it('should show SA error if answer is not wrote with custom security question', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
            const questions = await this.browser.findElements(
                'css selector',
                PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
            );

            const question = questions[questions.length - 1];

            await this.browser.click(question);

            await this.browser.yaSetValue(
                PO.securityQuestionSecurityAnswerScreen.questionInput(),
                randomAlphanumeric(6)
            );

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());

            const questionErrorTexts = await this.browser.findElements(
                'css selector',
                PO.securityQuestionSecurityAnswerScreen.questionErrorText()
            );

            expect(questionErrorTexts.length).to.equal(0);
            await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.answerErrorText());
        });
        it('should show SQ SA errors if answer and question is not wrote', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.select());
            const questions = await this.browser.findElements(
                'css selector',
                PO.securityQuestionSecurityAnswerScreen.securityQuestionSelector.option()
            );

            const question = questions[questions.length - 1];

            await this.browser.click(question);

            await this.browser.click(PO.securityQuestionSecurityAnswerScreen.nextButton());
            await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.questionErrorText());
            await this.browser.yaShouldHaveVisibleText(PO.securityQuestionSecurityAnswerScreen.answerErrorText());
        });
        it('should show SecurityQuestionSecurityAnswerScreen when click back on captcha', async function() {
            await this.browser.click(PO.phoneScreen.switchButton());
            await processSQSAScreen(this.browser);
            await this.browser.yaWaitForVisible(PO.captchaScreen());
            await this.browser.yaWaitForVisible(PO.previousStepButton());
            await this.browser.click(PO.previousStepButton());
            await processSQSAScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await this.browser.yaWaitForVisible(PO.personalDataSignUpInDaHouse());
            await this.browser.yaWaitForVisible(PO.previousStepButton());
            await this.browser.click(PO.previousStepButton());
            await this.browser.yaWaitForVisible(PO.captchaScreen());
            await this.browser.yaWaitForVisible(PO.previousStepButton());
            await this.browser.click(PO.previousStepButton());
            await processSQSAScreen(this.browser);
            await processCaptchaScreen(this.browser);
            await this.browser.yaWaitForVisible(PO.personalDataSignUpInDaHouse());
        });
    });
});
