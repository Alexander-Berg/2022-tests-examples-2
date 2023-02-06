const request = require('requestretry');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER} = require('../../../testEnvironmentConfig');
const {
    USER_IP_WITH_NO_REGISTRATION_LIMITS,
    X_TOKEN_CLIENT_ID,
    X_TOKEN_CLIENT_SECRET,
    getRegistrationHeaders
} = require('./common');

async function getTrackIdFromQR(element) {
    const styleAttribute = await element.getAttribute('style');
    const trackId = styleAttribute.substring(styleAttribute.indexOf('=') + 1, styleAttribute.lastIndexOf(')') - 1);

    return trackId;
}

async function confirmQR(trackId, username, password) {
    try {
        const responseToken = await request({
            url: `https://oauth-test.yandex.ru/token`,
            method: 'POST',
            form: {
                password,
                username,
                grant_type: 'password',
                client_id: X_TOKEN_CLIENT_ID,
                client_secret: X_TOKEN_CLIENT_SECRET
            },
            headers: {
                Accept: '*/*',
                'content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Ya-Consumer-Client-Ip': USER_IP_WITH_NO_REGISTRATION_LIMITS
            }
        });
        const resultToken = await responseToken.toJSON();
        const tokenBody = JSON.parse(resultToken.body);
        const token = tokenBody.access_token;

        const response = await request({
            url: `${QA_PROXY_HOST}/1/bundle/auth/x_token/prepare/?consumer=${PASSPORT_API_CONSUMER}`,
            method: 'POST',
            form: {
                track_id: trackId
            },
            headers: {
                ...(await getRegistrationHeaders()),
                'Ya-Consumer-Authorization': `OAuth ${token}`
            },
            json: true
        });
        const result = await response.toJSON();
        const body = result.body;

        if (body.status !== 'ok') {
            throw JSON.stringify(body);
        }

        return body;
    } catch (error) {
        throw new Error(error);
    }
}

module.exports = {
    getTrackIdFromQR,
    confirmQR
};
