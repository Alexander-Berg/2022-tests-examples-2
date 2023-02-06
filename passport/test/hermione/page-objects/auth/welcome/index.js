const El = require('@yandex-int/bem-page-object').Entity;

const welcomeScreen = new El('[data-t="page:welcome"]');

welcomeScreen.currentAccount = new El('.CurrentAccount');

welcomeScreen.authPasswordForm = new El('.AuthPasswordForm');
welcomeScreen.authPasswordForm.hiddenTrackId = new El('[name="track_id"]');
welcomeScreen.authBySMS = new El('[data-t="button:default:auth-by-sms"]');
welcomeScreen.authLetterButton = new El('[data-t="button:default:auth-letter"]');

const PhoneConfirmationCode = new El('.PhoneConfirmationCode');

PhoneConfirmationCode.phoneCodeInput = new El('[data-t="field:input-phoneCode"]');

PhoneConfirmationCode.nextButton = new El('[data-t="button:action"]');

module.exports = {
    welcomeScreen,
    PhoneConfirmationCode
};
