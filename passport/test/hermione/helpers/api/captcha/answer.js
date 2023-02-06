const request = require('requestretry');
const {QA_PROXY_HOST} = require('../../../testEnvironmentConfig');
const tvm = require('../../tvmTicketsProvider');

async function getCaptchaAnswer(key) {
    const res = await request({
        url: `${QA_PROXY_HOST}/answer?key=${key}&json=1`,
        headers: {
            'Ya-Proxy-Target-Url': 'http://api.captcha.yandex.net',
            'Ya-Proxy-TVM-Ticket': await tvm.getQAProxyTicket()
        },
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);

    return res['answer'];
}

module.exports = {
    getCaptchaAnswer
};
