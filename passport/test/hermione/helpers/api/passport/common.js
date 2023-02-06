const {getPassportInternalHost} = require('../../../testEnvironmentConfig');
const tvm = require('../../tvmTicketsProvider');

const USER_IP_WITH_NO_REGISTRATION_LIMITS = '37.9.101.111';
const getRegistrationHeaders = async () => {
    return {
        'Ya-Proxy-Target-Url': getPassportInternalHost(),
        'Ya-Proxy-TVM-Ticket': await tvm.getQAProxyTicket(),
        'X-Ya-Service-Ticket': await tvm.getPassportInternalTicket(),
        'Ya-Consumer-Client-Ip': USER_IP_WITH_NO_REGISTRATION_LIMITS,
        'Ya-Client-User-Agent': 'passport-web-tests'
    };
};

const X_TOKEN_CLIENT_ID = '1898303434af426282ce7d45c89629c1';
const X_TOKEN_CLIENT_SECRET = 'c09f12fe080c46ca98f19294a06ffa5c';

module.exports = {
    USER_IP_WITH_NO_REGISTRATION_LIMITS,
    getRegistrationHeaders,
    X_TOKEN_CLIENT_ID,
    X_TOKEN_CLIENT_SECRET
};
