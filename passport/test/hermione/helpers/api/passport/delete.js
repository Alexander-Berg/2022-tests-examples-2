const request = require('requestretry');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER, isProd} = require('../../../testEnvironmentConfig');
const {getRegistrationHeaders} = require('./common');
const {readTrack} = require('../../../helpers/api/passport/track');

async function deleteAccount(uid) {
    try {
        const response = await request({
            url: `${QA_PROXY_HOST}/1/bundle/account/${uid}/?consumer=${PASSPORT_API_CONSUMER}`,
            method: 'DELETE',
            headers: await getRegistrationHeaders(),
            json: true
        });
        const result = await response.toJSON();
        const body = result.body;

        if (body.status !== 'ok') {
            throw 'deleteAccount:' + JSON.stringify(body);
        }

        return body;
    } catch (error) {
        if (!isProd()) {
            throw error;
        }
    }
}

async function getUserId(browser) {
    const trackId = await browser.yaGetTrackId();
    const trackData = await readTrack(trackId);

    try {
        const userId = trackData.uid || JSON.parse(trackData.social_task_data).profile.userid;

        return userId;
    } catch (error) {
        // console.log('getUserId error', trackId, trackData);
    }
}

async function safeDeleteAccount(browser) {
    const userId = await getUserId(browser);

    await deleteAccount(userId);
}

function tryDeleteAccountAfterRun(testRunFunc) {
    return async function() {
        let savedError;

        try {
            await testRunFunc.call(this);
        } catch (error) {
            savedError = error;
        }

        try {
            await safeDeleteAccount(this.browser);
        } catch (error) {
            if (!savedError) {
                throw error;
            }
        }

        if (savedError) {
            throw savedError;
        }
    };
}

module.exports = {
    deleteAccount,
    safeDeleteAccount,
    tryDeleteAccountAfterRun,
    getUserId
};
