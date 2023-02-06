/**
 * Устанавливаем test-id в куку.
 */
module.exports.yaSetTestId = async function(ids) {
    await this.setCookies([{name: 'test-id', value: ids.join('_')}]);
};
