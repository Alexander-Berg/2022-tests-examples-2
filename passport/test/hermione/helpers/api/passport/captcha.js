const request = require('requestretry');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER} = require('../../../testEnvironmentConfig');
const {getRegistrationHeaders} = require('./common');

async function generateCaptcha(trackId) {
    const res = await request({
        url: `${QA_PROXY_HOST}/1/captcha/generate/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: trackId,
            display_language: 'ru'
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);

    return res['key'];
}

async function checkCaptcha(trackId, answer) {
    const res = await request({
        url: `${QA_PROXY_HOST}/1/captcha/check/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: trackId,
            answer: answer
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);

    return res['correct'] === 'true';
}

module.exports = {
    generateCaptcha,
    checkCaptcha
};
