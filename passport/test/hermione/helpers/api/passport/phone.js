const request = require('requestretry');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER} = require('../../../testEnvironmentConfig');
const {getRegistrationHeaders} = require('./common');

async function submitConfirmPhone(trackId, phone) {
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/phone/confirm/submit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: trackId,
            number: phone,
            display_language: 'ru'
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'submitConfirmPhone: ' + JSON.stringify(body);
    }

    return body;
}

async function commitConfirmPhone(trackId, code) {
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/phone/confirm/commit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: trackId,
            code: code
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'commitConfirmPhone: ' + JSON.stringify(body);
    }

    return body;
}

module.exports = {
    submitConfirmPhone,
    commitConfirmPhone
};
