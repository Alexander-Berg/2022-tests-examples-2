const {getCaptchaAnswer} = require('../helpers/api/captcha/answer');

/**
 * Команда для прохождения капчи.
 * Делает запрос в апи, чтобы получить ответ на капчу, и сабмитит его
 */
module.exports.yaPassCaptcha = async function(PO, captchaInput, submitButton) {
    let captchaKeyElement;

    if (arguments.length === 3) {
        captchaKeyElement = PO;
    } else {
        captchaKeyElement = PO.auth.captchaKey();
        captchaInput = PO.auth.captchaInput();
        submitButton = PO.submitButton();
    }

    const captchaKey = await this.yaWaitUntil(
        'Ключ капчи должен быть не пустым',
        async () => await this.getValue(captchaKeyElement),
        5000
    );

    await this.setMeta('captcha_key', captchaKey);

    const captchaAnswer = await getCaptchaAnswer(captchaKey);

    await this.setMeta('captcha_answer', captchaAnswer);

    await this.yaSetValue(captchaInput, captchaAnswer);
    await this.yaWaitForVisible(submitButton);
    await this.click(submitButton);
};
