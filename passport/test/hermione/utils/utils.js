const {userWithLoginPassword} = require('../helpers/user');
const {checkLoginAvailability} = require('../helpers/api/blackbox/loginoccupation');
const {generateCaptcha, checkCaptcha} = require('../helpers/api/passport/captcha');
const {commitConfirmPhone, submitConfirmPhone} = require('../helpers/api/passport/phone');
const {readTrack} = require('../helpers/api/passport/track');
const {getCaptchaAnswer} = require('../helpers/api/captcha/answer');

function randomAlphanumeric(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;

    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.random() * charactersLength);
    }
    return result;
}

module.exports.randomAlphanumeric = randomAlphanumeric;

const DEFAULT_CONTROL_ANSWER = 'asdf';

module.exports.DEFAULT_CONTROL_ANSWER = DEFAULT_CONTROL_ANSWER;

module.exports.getRandomFakePhoneInE164 = () =>
    `+70000${Math.random()
        .toString()
        .slice(2, 8)}`;

module.exports.getRandomFakePhoneForCalls = () =>
    `+70001${Math.random()
        .toString()
        .slice(2, 8)}`;

module.exports.getRandomFreeLogin = async (prefix) => {
    let attempts = 10;

    let hasFreeLogin = false;

    let login;

    const loginPrefix = prefix || (Math.random() < 0.5 ? 'yandex-team-' : 'yndx-');

    while (attempts > 0 && !hasFreeLogin) {
        login = `${loginPrefix}${randomAlphanumeric(6)}.${randomAlphanumeric(6)}`.slice(0, 30);
        hasFreeLogin = await checkLoginAvailability(login);
    }
    if (hasFreeLogin) {
        return login;
    } else {
        throw new Error('Не смогли найти свободный логин за 10 попыток');
    }
};

module.exports.getRandomPassword = () => {
    return `pWd.${randomAlphanumeric(6)}`;
};

module.exports.passCaptcha = async (trackId, captchaKey) => {
    if (!captchaKey) {
        captchaKey = await generateCaptcha(trackId);
    }
    const answer = await getCaptchaAnswer(captchaKey);

    return await checkCaptcha(trackId, answer);
};

async function getPhoneConfirmationCode(trackId) {
    const trackData = await readTrack(trackId);

    return trackData['phone_confirmation_code'];
}

module.exports.getPhoneConfirmationCode = getPhoneConfirmationCode;

module.exports.confirmPhone = async (trackId, phone) => {
    await submitConfirmPhone(trackId, phone);
    const code = await getPhoneConfirmationCode(trackId);

    await commitConfirmPhone(trackId, code);
};

module.exports.delay = function delay(timeout) {
    return new Promise((resolve) => {
        setTimeout(resolve, timeout);
    });
};

const commonUserUid = process.env.TEST_ENV === 'dev' || process.env.TEST_ENV === 'test' ? '4082444138' : '1487601173';
const commonUserWithControlQuestionUid =
    process.env.TEST_ENV === 'dev' || process.env.TEST_ENV === 'test' ? '4082238104' : '1486527812';

const commonUser = userWithLoginPassword('yndx-common-with-phone', 'Simple123456').update({uid: commonUserUid});

commonUser.setSecurePhone('+70000001234');

const commonWithControlQuestion = userWithLoginPassword('yndx-common-control-q', 'Simple123456').update({
    uid: commonUserWithControlQuestionUid
});

commonWithControlQuestion.controlAnswer = DEFAULT_CONTROL_ANSWER;

module.exports.commonUser = commonUser;
module.exports.commonWithControlQuestion = commonWithControlQuestion;
