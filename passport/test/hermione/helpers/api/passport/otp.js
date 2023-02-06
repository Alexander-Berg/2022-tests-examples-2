const {QA_PROXY_HOST, PASSPORT_API_CONSUMER, getPassportFrontendHost} = require('../../../testEnvironmentConfig');
const request = require('requestretry');
const {getRegistrationHeaders} = require('./common');

module.exports.initCreationOTP = async function(clientCookie, track_id) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const response = await request({
        url: `${QA_PROXY_HOST}/2/bundle/otp/enable/submit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id
        },
        headers: {
            ...(await getRegistrationHeaders()),
            'Ya-Client-Cookie': clientCookie,
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            Accept: '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'initCreationOTP' + JSON.stringify(body);
    }

    return body;
};

module.exports.getOTPSecret = async function(clientCookie, trackId) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/otp/enable/get_secret/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: trackId
        },
        headers: {
            ...(await getRegistrationHeaders()),
            Accept: '*/*',
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            'Ya-Client-Cookie': clientCookie,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'otpGetSecret' + JSON.stringify(body);
    }

    return body;
};

module.exports.generateOTP = async function(pin, b32AppSecret) {
    const response = await request({
        url: `${QA_PROXY_HOST}/generate?pin=${pin}&b32_app_secret=${b32AppSecret}`,
        method: 'GET',
        headers: {
            ...(await getRegistrationHeaders()),
            Accept: '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Ya-Proxy-Target-Url': 'http://totp2.passportdev.yandex.ru'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    return body;
};

module.exports.enableOTP = async function(track_id, clientCookie) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/otp/enable/commit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id
        },
        headers: {
            ...(await getRegistrationHeaders()),
            'Ya-Client-Cookie': clientCookie,
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            Accept: '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'enableOTP: ' + JSON.stringify(body);
    }

    return body;
};

module.exports.checkOTP = async function(otp, track_id, clientCookie) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/otp/enable/check_otp/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id,
            otp
        },
        headers: {
            ...(await getRegistrationHeaders()),
            'Ya-Client-Cookie': clientCookie,
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            Accept: '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'checkOTP: ' + JSON.stringify(body);
    }

    return body;
};
