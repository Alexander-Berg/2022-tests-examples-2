const El = require('@yandex-int/bem-page-object').Entity;

const previousStepButton = new El('.PreviousStepButton');

const phoneScreen = new El('.Phone');

phoneScreen.switchButton = new El('[data-t="button:pseudo:passp:phone:controls:switch"]');
phoneScreen.phoneInput = new El('[data-t="field:input-phone"]');
phoneScreen.nextButton = new El('[data-t="button:action:passp:phone:controls:next"]');
phoneScreen.hint = new El('[data-t="field:input-phone:hint"]');

const phoneConfirmationCodeScreen = new El('.PhoneConfirmationCode');

phoneConfirmationCodeScreen.codeInput = new El('[data-t="field:input-phoneCode"]');

const securityQuestionSecurityAnswerScreen = new El('.SecurityQuestionSecurityAnswerScreen');

securityQuestionSecurityAnswerScreen.securityQuestionSelector = new El('.SecurityQuestionSelector');
securityQuestionSecurityAnswerScreen.securityQuestionSelector.select = new El('[name="hint_question_id"]');
securityQuestionSecurityAnswerScreen.securityQuestionSelector.option = new El('[name="hint_question_id"] > option');
securityQuestionSecurityAnswerScreen.securityQuestionSelector.text = new El('.Button2-Text');
securityQuestionSecurityAnswerScreen.questionInput = new El('[data-t="field:input-hint_question_custom"]');
securityQuestionSecurityAnswerScreen.questionErrorText = new El('[data-t="field:input-hint_question_custom:hint"]');
securityQuestionSecurityAnswerScreen.answerInput = new El('[data-t="field:input-hint_answer"]');
securityQuestionSecurityAnswerScreen.answerErrorText = new El('[data-t="field:input-hint_answer:hint"]');
securityQuestionSecurityAnswerScreen.nextButton = new El('[data-t="button:action"]');

const captchaScreen = new El('.CaptchaScreen');

captchaScreen.input = new El('.CaptchaField-field [data-t="field:input-captcha"');
captchaScreen.captchaKey = new El('[name="captcha_key"]');
captchaScreen.nextButton = new El('[data-t="button:action"]');

const currentPasswordScreen = new El('.CurrentPassword');

currentPasswordScreen.passwordInput = new El('[data-t="field:input-password"]');
currentPasswordScreen.nextButton = new El('[data-t="button:action"]');
currentPasswordScreen.hint = new El('[data-t="field:input-password:hint"]');

const personalDataSignUpInDaHouse = new El('.PersonalDataSignUpInDaHouse');

personalDataSignUpInDaHouse.firstNameInput = new El('[data-t="field:input-firstname"]');
personalDataSignUpInDaHouse.firstNameInputHint = new El('[data-t="field:input-firstname:hint"]');
personalDataSignUpInDaHouse.lastNameInput = new El('[data-t="field:input-lastname"]');
personalDataSignUpInDaHouse.lastNameInputHint = new El('[data-t="field:input-lastname:hint"]');
personalDataSignUpInDaHouse.nextButton = new El('[data-t="button:action"]');

const loginSignUp = new El('.LoginSignUp');

loginSignUp.loginInput = new El('[data-t="field:input-login"]');
loginSignUp.loginInputError = new El('.Field-error');
loginSignUp.suggestButton = new El('[data-t="button:default:passp:Login:suggest"]');
loginSignUp.nextButton = new El('[data-t="button:action:passp:Login:registration"]');

const passwordSignUpInDaHouse = new El('.PasswordSignUpInDaHouse');

passwordSignUpInDaHouse.passwordInput = new El('[data-t="field:input-password"]');
passwordSignUpInDaHouse.nextButton = new El('[data-t="button:action"]');

const registrationSocialButtons = new El('.registration_social-btns');

registrationSocialButtons.registrationFBButton = new El('.registration__fb-btn');

const eulaSignUp = new El('.EulaSignUp');

eulaSignUp.nextButton = new El('[aria-disabled="false"][data-t="button:action"]');

module.exports = {
    captchaScreen,
    currentPasswordScreen,
    eulaSignUp,
    loginSignUp,
    passwordSignUpInDaHouse,
    personalDataSignUpInDaHouse,
    phoneScreen,
    phoneConfirmationCodeScreen,
    previousStepButton,
    registrationSocialButtons,
    securityQuestionSecurityAnswerScreen
};
