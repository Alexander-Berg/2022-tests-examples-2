const {ErrorHandler} = require('webdriverio');

/**
 * Обёртка над стандартной командой waitForVisible. Позволяет указывать произвольное сообщение об ошибке.
 *
 * @param {String} selector - Селектор для элемента, появление которого нужно ждать
 * @param {Number} [timeout] - Таймаут в миллисекундах
 * @param {String} [message] - Сообщение об ошибке
 *
 * @returns {Promise}
 */
module.exports.yaWaitForVisible = async function(selector, timeout, message) {
    if (typeof timeout === 'string') {
        message = timeout;
    }

    if (typeof timeout !== 'number') {
        timeout = this.options.waitforTimeout;
    }

    let result;

    try {
        result = await this.waitForVisible(selector, timeout);
    } catch (e) {
        if (message && e.type === 'WaitUntilTimeoutError') {
            throw new ErrorHandler('CommandError', message);
        }

        throw e;
    }
    return result;
};
