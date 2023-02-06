const request = require('requestretry');
const xmlParser = require('xml2json-light');
const {QA_PROXY_HOST, PASSPORT_API_CONSUMER} = require('../../../testEnvironmentConfig');
const {userWithLoginPassword, userWithUid} = require('../../user');
const {createTrack, readTrack} = require('./track');
const {submitConfirmPhone, commitConfirmPhone} = require('./phone');
const {
    getRandomFreeLogin,
    getRandomPassword,
    getRandomFakePhoneInE164,
    getRandomFakePhoneForCalls,
    randomAlphanumeric,
    DEFAULT_CONTROL_ANSWER,
    passCaptcha,
    confirmPhone
} = require('../../../utils/utils');
const {getRegistrationHeaders, X_TOKEN_CLIENT_ID, X_TOKEN_CLIENT_SECRET} = require('./common');
const {authPasswordMultiStepStart, authPasswordSubmit} = require('./auth');
const {initCreationOTP, getOTPSecret, generateOTP, enableOTP, checkOTP} = require('./otp');

async function createEmptyUser({login, password, firstname, lastname, language = 'ru', country = 'ru'} = {}) {
    login = login || (await getRandomFreeLogin());
    password = password || getRandomPassword();
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;

    const formArgs = {
        login: login || (await getRandomFreeLogin()),
        password: password || getRandomPassword(),
        firstname: firstname || `Имя-${randomAlphanumeric(6)}`,
        lastname: lastname || `Фамилия ${randomAlphanumeric(6)}`,
        language: language,
        country: country
    };

    const res = await request({
        url: `${QA_PROXY_HOST}/1/bundle/account/register/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: formArgs,
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw new Error(JSON.stringify(body));
    }

    // TODO: save to tus?
    return userWithLoginPassword(login, password).update({
        uid: body['uid'].toString(),
        firstname: firstname,
        lastname: lastname
    });
}

async function createUserWithOPT({login, password, firstname, lastname, language = 'ru', country = 'ru'} = {}) {
    const user = await createUserWithPhone({login, password, firstname, lastname, language, country});
    const {cookies, track_id} = await authPasswordSubmit(user.login, user.password);
    const cookie = cookies[0];

    await initCreationOTP(cookie, track_id);
    await confirmPhone(track_id, user.phonesValue.secure);

    const secret = await getOTPSecret(cookie, track_id);
    const otp = await generateOTP(secret.pin, secret.app_secret);

    await checkOTP(otp, track_id, cookie);
    await enableOTP(track_id, cookie);

    return {
        user,
        secret
    };
}

async function createUserWithControlQuestion({
    login,
    password,
    firstname,
    lastname,
    language = 'ru',
    country = 'ru',
    controlQuestionId = '1',
    controlAnswer = DEFAULT_CONTROL_ANSWER
} = {}) {
    login = login || (await getRandomFreeLogin());
    password = password || getRandomPassword();
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;

    const trackId = await createTrack();

    await passCaptcha(trackId);

    const formArgs = {
        login: login,
        password: password,
        firstname: firstname,
        lastname: lastname,
        language: language,
        country: country,
        hint_question_id: controlQuestionId,
        hint_answer: controlAnswer,
        eula_accepted: true,
        validation_method: 'captcha',
        display_language: 'ru',
        track_id: trackId
    };
    const res = await request({
        url: `${QA_PROXY_HOST}/1/account/register/alternative/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: formArgs,
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    })
        .then((response = {}) => response.body)
        .catch((error = {}) => error);

    // TODO: save to tus?
    const user = userWithLoginPassword(login, password).update({
        uid: res['uid'].toString(),
        firstname: firstname,
        lastname: lastname
    });

    user.controlAnswer = controlAnswer;
    return user;
}

async function createUserWithPhone({
    login,
    password,
    phone,
    firstname,
    lastname,
    language = 'ru',
    country = 'ru'
} = {}) {
    login = login || (await getRandomFreeLogin());
    password = password || getRandomPassword();
    phone = phone || getRandomFakePhoneInE164();
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;

    const trackId = await createTrack();

    await confirmPhone(trackId, phone);

    const formArgs = {
        login: login,
        password: password,
        firstname: firstname,
        lastname: lastname,
        language: language,
        country: country,
        eula_accepted: true,
        validation_method: 'phone',
        display_language: 'ru',
        track_id: trackId
    };
    const res = await request({
        url: `${QA_PROXY_HOST}/1/account/register/alternative/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: formArgs,
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'createUserWithPhone' + JSON.stringify(body);
    }

    // TODO: save to tus?
    const user = userWithLoginPassword(login, password).update({
        uid: body['uid'].toString(),
        firstname: firstname,
        lastname: lastname
    });

    user.setSecurePhone(phone);
    return user;
}

async function createLiteUser({firstname, lastname, password, login} = {}) {
    login = login || (await getRandomFreeLogin());
    password = password || getRandomPassword();
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;
    login = `${login}@test.ru`;

    const res = await request({
        url: `${QA_PROXY_HOST}/1/bundle/test/register_lite/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            firstname,
            lastname,
            password,
            login
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'createLiteUser' + JSON.stringify(body);
    }

    // TODO: save to tus?
    const user = userWithLoginPassword(login, password).update({
        uid: body['uid'].toString(),
        firstname,
        lastname
    });

    return user;
}

async function createSuperLiteUser({firstname, lastname, login} = {}) {
    login = login || `${await getRandomFreeLogin()}@test.ru`;
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;

    const resMobileRegStart = await request({
        url: `${QA_PROXY_HOST}/2/bundle/mobile/start/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            login,
            display_language: 'ru',
            x_token_client_id: X_TOKEN_CLIENT_ID,
            x_token_client_secret: X_TOKEN_CLIENT_SECRET
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const resultMobileRegStart = await resMobileRegStart.toJSON();
    const bodyMobileRegStart = resultMobileRegStart.body;

    if (bodyMobileRegStart.can_register == false) {
        throw 'createSuperLiteUser:mobileRegStart:' + JSON.stringify(bodyMobileRegStart);
    }

    const resMobileRegMagicLink = await request({
        url: `${QA_PROXY_HOST}/1/bundle/mobile/magic_link/send/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: bodyMobileRegStart.track_id
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const resultMobileRegMagicLink = await resMobileRegMagicLink.toJSON();
    const bodyMobileRegMagicLink = resultMobileRegMagicLink.body;

    if (bodyMobileRegMagicLink.status !== 'ok') {
        throw 'createSuperLiteUser:mobileRegMagicLink:' + JSON.stringify(bodyMobileRegMagicLink);
    }

    const {magic_link_secret} = await readTrack(bodyMobileRegStart.track_id);
    const path = '/1/bundle/auth/password/multi_step/magic_link/commit_registration/';
    const resCommitRegistration = await request({
        url: `${QA_PROXY_HOST}${path}?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            track_id: bodyMobileRegStart.track_id,
            secret: magic_link_secret,
            language: 'ru'
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const resultCommitRegistration = await resCommitRegistration.toJSON();
    const bodyCommitRegistration = resultCommitRegistration.body;

    if (bodyCommitRegistration.status !== 'ok') {
        throw 'createSuperLiteUser:commit_registration:' + JSON.stringify(bodyCommitRegistration);
    }

    const resMobileRegisterLite = await request({
        url: `${QA_PROXY_HOST}/1/bundle/mobile/register/lite/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            firstname,
            lastname,
            eula_accepted: true,
            track_id: bodyMobileRegStart.track_id
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const resultMobileRegisterLite = await resMobileRegisterLite.toJSON();
    const bodyMobileRegisterLite = resultMobileRegisterLite.body;

    if (bodyMobileRegisterLite.status !== 'ok') {
        throw 'createSuperLiteUser:mobileRegisterLite:' + JSON.stringify(bodyMobileRegisterLite);
    }

    // TODO: save to tus?
    const user = userWithUid(bodyMobileRegisterLite['uid'].toString()).update({
        login,
        firstname,
        lastname
    });

    return user;
}

async function createNeophonishUser({firstname, lastname, phone} = {}) {
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;
    phone = phone || getRandomFakePhoneForCalls();

    const {track_id} = await authPasswordMultiStepStart(phone);

    await submitConfirmPhone(track_id, phone);

    const {phone_confirmation_code} = await readTrack(track_id);

    await commitConfirmPhone(track_id, phone_confirmation_code);

    const res = await request({
        url: `${QA_PROXY_HOST}/1/bundle/account/register/neophonish/?consumer=${PASSPORT_API_CONSUMER}`,
        method: 'POST',
        form: {
            firstname,
            lastname,
            eula_accepted: true,
            track_id
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = result.body;

    if (body.status !== 'ok') {
        throw 'createNeophonishUser:' + JSON.stringify(body);
    }

    // TODO: save to tus?
    const user = userWithUid(body['uid'].toString()).update({
        firstname,
        lastname
    });

    user.setSecurePhone(phone);

    return user;
}

async function createAutoregisteredUser({firstname, lastname, login, password} = {}) {
    login = login || (await getRandomFreeLogin());
    password = password || getRandomPassword();
    firstname = firstname || `Имя-${randomAlphanumeric(6)}`;
    lastname = lastname || `Фамилия ${randomAlphanumeric(6)}`;

    const res = await request({
        url: `${QA_PROXY_HOST}/passport/?mode=admreg`,
        method: 'POST',
        form: {
            fname: firstname,
            passwd: password,
            login: login,
            passwd2: password,
            iname: lastname
        },
        headers: await getRegistrationHeaders(),
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = xmlParser.xml2json(result.body).page;

    if (body.status !== 'ok') {
        throw 'createAutoregisteredUser:' + JSON.stringify(body);
    }

    // TODO: save to tus?
    const user = userWithLoginPassword(login, password).update({
        uid: body['uid'].toString(),
        firstname,
        lastname
    });

    return user;
}

module.exports = {
    createEmptyUser,
    createUserWithControlQuestion,
    createUserWithPhone,
    createUserWithOPT,
    createLiteUser,
    createSuperLiteUser,
    createNeophonishUser,
    createAutoregisteredUser
};
