const request = require('requestretry');
const {QA_PROXY_HOST, getBlackboxHost} = require('../../../testEnvironmentConfig');
const tvm = require('../../tvmTicketsProvider');

async function checkLoginAvailability(login, isPdd) {
    const queryArgs = {
        method: 'loginoccupation',
        userip: '127.0.0.1',
        format: 'json',
        logins: login,
        is_pdd: isPdd || false,
        ignore_stoplist: true
    };

    const res = await request({
        url: `${QA_PROXY_HOST}`,
        qs: queryArgs,
        headers: {
            'Ya-Proxy-Target-Url': getBlackboxHost(),
            'Ya-Proxy-TVM-Ticket': await tvm.getQAProxyTicket(),
            'X-Ya-Service-Ticket': await tvm.getBlackboxTicket()
        },
        retryDelay: 1000,
        json: true,
        logID: '000000'
    });

    const result = await res.toJSON();
    const body = result.body;

    return body && body.logins && body.logins[login] ? body.logins[login].status === 'free' : false;
}

module.exports = {
    checkLoginAvailability
};
