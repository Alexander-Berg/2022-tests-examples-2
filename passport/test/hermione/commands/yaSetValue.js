/**
 * Меняет значение элемента, проверив что он видим.
 */
module.exports.yaSetValue = async function(selector, value) {
    await this.yaWaitForVisible(selector, `Не нашли элемент ${selector} для ввода "${value}"`);
    await this.click(selector);
    await this.setValue(selector, value);
};
