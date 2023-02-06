const El = require('@yandex-int/bem-page-object').Entity;

const elems = {};

elems.submitButton = new El('[data-t*="button:action"]');
elems.trackIdField = new El('[name="track_id"]');

elems.auth = new El('.passp-auth');
elems.auth.title = new El('.passp-title');
elems.auth.loginInput = new El('input[name=login]');
elems.auth.passwordInput = new El('[data-t="field:input-password"], [data-t="field:input-passwd"]');
elems.auth.passwordEyeToggle = new El('.Password-toggler');
elems.auth.passwordConfirmInput = new El('[data-t="field:input-password_confirm"]');
elems.auth.captchaImage = new El('.captcha img');
elems.auth.captchaInput = new El('[data-t="field:input-captcha_answer"]');
elems.auth.captchaKey = new El('[name="captcha_key"]');
elems.auth.controlAnswerInput = new El('[data-t="field:input-answer"]');
elems.auth.phoneInput = new El('[data-t="field:input-phone"]');
elems.auth.phoneCodeInput = new El('[data-t="field:input-phone-code"]');
elems.auth.emailInput = new El('[data-t="field:input-email"]');
elems.auth.errorField = new El('.Textinput-Hint_state_error');
elems.auth.firstnameInput = new El('[data-t="field:input-firstname"]');
elems.auth.lastnameInput = new El('[data-t="field:input-lastname"]');

elems.challenge = new El('[data-t="challenge"]');
elems.challenge.phoneCodeInput = new El('[data-t="field:input-phoneCode"]');

elems.profile = new El('.profile');

module.exports = elems;
