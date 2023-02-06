const {QA_PROXY_HOST, PASSPORT_API_CONSUMER, getPassportFrontendHost} = require('../../../testEnvironmentConfig');
const pages = require('../../../utils/passportPages');
const {createSession} = require('../blackbox/createSession');
const request = require('requestretry');
const {getRegistrationHeaders} = require('./common');
const {readTrack} = require('./track');

module.exports.authPasswordSubmit = async function(login, password) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const response = await request({
        url: `${QA_PROXY_HOST}/1/bundle/auth/password/submit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            login,
            password,
            policy: 'long'
        },
        headers: {
            ...(await getRegistrationHeaders()),
            Accept: '*/*',
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            'Ya-Client-Cookie': ';',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const result = await response.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'authPasswordSubmit: ' + JSON.stringify(body);
    }

    return body;
};

module.exports.authPasswordMultiStepCommitMagic = async function(track_id, csrf_token) {
    const frontendHost = getPassportFrontendHost().split('//')[1];
    const responseMagic = await request({
        url: `${QA_PROXY_HOST}/2/bundle/auth/password/commit_magic/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id,
            csrf_token
        },
        headers: {
            ...(await getRegistrationHeaders()),
            Accept: '*/*',
            'Ya-Client-Host': frontendHost,
            'Ya-Consumer-Client-Scheme': 'https',
            'Ya-Client-Cookie': ';',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        json: true
    });
    const resultMagic = await responseMagic.toJSON();
    const bodyMagic = resultMagic.body;

    if (bodyMagic.status !== 'ok') {
        throw 'Magic' + JSON.stringify(bodyMagic);
    }

    return bodyMagic;
};

module.exports.authPasswordMultiStepStart = async function(login) {
    const frontendHost = getPassportFrontendHost().split('//')[1];

    const responseStart = await request({
        url: `${QA_PROXY_HOST}/1/bundle/auth/password/multi_step/start/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            login
        },
        headers: {
            ...(await getRegistrationHeaders()),
            'Ya-Client-Host': frontendHost,
            'Ya-Client-Cookie': ';'
        },
        json: true
    });
    const resultStart = await responseStart.toJSON();
    const bodyStart = resultStart.body;

    if (bodyStart.status !== 'ok') {
        throw 'start' + JSON.stringify(bodyStart);
    }

    return bodyStart;
};

module.exports.authOtpPrepare = async function(login, otp, track_id) {
    const responsePrepare = await request({
        url: `${QA_PROXY_HOST}/1/bundle/auth/otp/prepare/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: track_id,
            login,
            otp
        },
        headers: {
            ...(await getRegistrationHeaders())
        },
        json: true
    });
    const resultPrepare = await responsePrepare.toJSON();
    const bodyPrepare = resultPrepare.body;

    if (bodyPrepare.status !== 'ok') {
        throw 'authOtpPrepare' + JSON.stringify(bodyPrepare);
    }

    return bodyPrepare;
};

module.exports.authPhone = async function authPhone(phone) {
    const {track_id} = await module.exports.authPasswordMultiStepStart(phone);

    const responseSubmit = await request({
        url: `${QA_PROXY_HOST}/1/bundle/phone/confirm_tracked_secure/submit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id,
            display_language: 'ru'
        },
        headers: {
            ...(await getRegistrationHeaders())
        },
        json: true
    });
    const resultSubmit = await responseSubmit.toJSON();
    const bodySubmit = resultSubmit.body;

    if (bodySubmit.status !== 'ok') {
        throw 'authPhone:phone/confirm_tracked_secure/submit:' + JSON.stringify(bodySubmit);
    }
    const {phone_confirmation_code} = await readTrack(bodySubmit.track_id);

    const responseCommit = await request({
        url: `${QA_PROXY_HOST}/1/bundle/phone/confirm_tracked_secure/commit/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id,
            code: phone_confirmation_code
        },
        headers: {
            ...(await getRegistrationHeaders())
        },
        json: true
    });
    const resultCommit = await responseCommit.toJSON();
    const bodyCommit = resultCommit.body;

    if (bodyCommit.status !== 'ok') {
        throw 'authPhone:phone/confirm_tracked_secure/commit:' + JSON.stringify(bodyCommit);
    }

    return track_id;
};

module.exports.setAuthCookies = async function setAuthCookies(browser, uid) {
    await browser.url(pages.AUTH.getUrl());
    const responseSession = await createSession(uid);
    const cookiesData = {
        Session_id: {...responseSession['new-session'], name: 'Session_id'}
    };

    await browser.setCookie(cookiesData['Session_id']);
};
