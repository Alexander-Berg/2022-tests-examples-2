const request = require('requestretry');
const {QA_PROXY_HOST, getBlackboxHost, getPassportFrontendDomain} = require('../../../testEnvironmentConfig');
const tvm = require('../../tvmTicketsProvider');

async function createSession(uid) {
    const queryArgs = {
        method: 'createsession',
        guard_hosts: getPassportFrontendDomain(),
        uid,
        keyspace: 'yandex.ru',
        // create_time: ,
        get_safe: 'yes',
        format: 'json',
        userip: '127.0.0.1',
        ttl: 5
        // password_check_time:
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

    return body;
}

module.exports = {
    createSession
};
