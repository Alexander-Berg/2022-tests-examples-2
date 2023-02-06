const request = require('requestretry');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER} = require('../../../testEnvironmentConfig');
const {getRegistrationHeaders} = require('./common');

async function createTrack() {
    const res = await request({
        url: `${QA_PROXY_HOST}/1/track/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);

    return res['id'];
}

async function readTrack(track) {
    return await request({
        url: `${QA_PROXY_HOST}/1/bundle/test/track/?consumer=${PASSPORT_API_CONSUMER}&track_id=${track}`,
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);
}

module.exports = {
    createTrack,
    readTrack
};
