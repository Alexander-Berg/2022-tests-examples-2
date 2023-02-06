/**
 * Притормозить тест
 * @param {number} ms - время в мс
 * @returns {Promise}
 */
const pause = ms => new Promise(resolve => {
    setTimeout(() => {
        resolve();
    }, ms);
});

module.exports = {
    pause,
};
