const {authOtpPrepare} = require('./auth');
const {generateOTP} = require('./otp');

module.exports.processOtpQR = async function(user, secret, trackId) {
    const otp = await generateOTP(secret.pin, secret.app_secret);

    await authOtpPrepare(user.login, otp, trackId);
};
