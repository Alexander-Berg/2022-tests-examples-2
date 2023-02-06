/**
 * Проверяет, что элемент видим в данный момент.
 * Если показа нужно ждать, лучше использовать yaWaitForVisible.
 * Если по селектору выберется несколько элементов, выбросит ошибку.
 *
 * @param {String} selector - Селектор элемента
 * @param {String} [message] - Сообщение об ошибке
 */

module.exports.yaShouldBeVisible = async function(selector, message) {
    const isVisible = await this.isVisible(selector);

    if (Array.isArray(isVisible)) {
        throw new Error(
            'Найдено более одного элемента. ' +
                `Пожалуйста, используйте более конкретный селектор. Исходный селектор - ${selector}`
        );
    }
    assert.isTrue(isVisible, (message ? message + '. ' : '') + `Элемент с селектором ${selector} не виден!`);
};
