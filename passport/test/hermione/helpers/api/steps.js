const loginoccupation = require('./blackbox/loginoccupation');
const userinfo = require('./blackbox/userinfo');
const captcha = require('./passport/captcha');
const phone = require('./passport/phone');
const registration = require('./passport/registration');
const track = require('./passport/track');

const blackbox = {
    loginoccupation,
    userinfo
};
const passportApi = {
    captcha,
    phone,
    registration,
    track
};

const steps = {
    blackbox,
    passport: passportApi
};

module.exports = steps;
