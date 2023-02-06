const _ = require('lodash');

/**
 * @callback yaWaitUntilMessageCallback
 * @returns {string}
 */

/**
 *
 * Команда для того, чтобы в случае падения waitUntil бросать своё сообщение об ошибке.
 *
 * @param {String|yaWaitUntilMessageCallback} getMessage - Сообщение об ошибке
 * @param {Function|Promise} condition - Условие
 * @param {Number} [timeout] - Таймаут в миллисекундах
 * @param {Number} [interval] - Интервал между проверками условия
 *
 * @returns {Promise.<void>}
 *
 * @example
 * await this.browser.yaGoUrl({ text: 'ip' });
 * await this.browser.yaWaitUntil('не дождались появления IPv4', async () => {
 *     const result = await this.execute(function() {
 *         return $('.z-fact__fact_version_v4').text().length !== 0;
 *     });
 *
 *     return result.state === 'success' && result.value === true;
 * });
 */
module.exports.yaWaitUntil = async function(getMessage, condition, timeout, interval) {
    try {
        return await this.waitUntil(condition, timeout, interval);
    } catch (e) {
        const message = _.isFunction(getMessage) ? getMessage() : getMessage;

        e.message = `${message}\n(Original error: ${e.message})`;
        throw e;
    }
};
