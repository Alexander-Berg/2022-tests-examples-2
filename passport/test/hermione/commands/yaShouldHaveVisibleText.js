/**
 * Проверяет, что элемент видим в данный момент и содержит не пустой текст.
 * Возможна валидация текста по регулярному выражению.
 * Примеры использования:
 * 1) .yaShouldHaveVisibleText(PO.entityCard.title(), 'Нет заголовка')
 * 2) .yaShouldHaveVisibleText(PO.entityCard.video(), /HD/i, 'В тумбе Видео нет метки HD')
 *
 * @param {String} selector - селектор элемента
 * @param {RegExp} [validate] - регулярное выражение, которым нужно провалидировать текст
 * @param {String} [message] - сообщение об ошибке
 */
module.exports.yaShouldHaveVisibleText = async function(selector, validate, message) {
    let regExpValidator = false;

    if (validate instanceof RegExp) {
        regExpValidator = true;
    } else if (!message) {
        message = validate;
    }

    const errorMessage = (details) => `${message ? message + '. ' : ''}${details}`;

    await this.yaWaitForVisible(selector, errorMessage(`Элемент по селектору ${selector} не виден`));
    const text = await this.getText(selector);

    if (regExpValidator) {
        assert.match(
            text,
            validate,
            errorMessage(`В текстовом содержимом по селектору ${selector} нет искомого текста`)
        );
    }
    assert.isAbove(text.length, 0, errorMessage(`Текстовое содержимое по селектору ${selector} пустое`));
};
