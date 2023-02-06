/**
 * Проверяет, что текущий url имеет тот же префикс, что и требуемый url, или полностью совпадает с требуемым
 *
 * @param {String} expectedUrl - Ожидаемый url
 * @param {String} [message] - Сообщение об ошибке
 * @param {Boolean} [isExactMatch] - Проверить, что url полностью полностью совпадает
 */

module.exports.yaShouldBeAtUrl = async function(expectedUrl, message, isExactMatch, timeout) {
    const getMessage = async function(browser) {
        message = (message ? message + '. ' : '') + `Текущий url "${await browser.getUrl()}"`;
        if (isExactMatch) {
            return message + ` не совпадает с "${expectedUrl}"`;
        } else {
            return message + ` не начинается с "${expectedUrl}"`;
        }
    };

    return await this.yaWaitUntil(
        await getMessage(this),
        async function() {
            const currentUrl = await this.getUrl();

            if (isExactMatch) {
                return currentUrl === expectedUrl;
            } else {
                return currentUrl.startsWith(expectedUrl);
            }
        },
        timeout
    );
};
