const request = require('requestretry');
const {QA_PROXY_HOST, getBlackboxHost} = require('../../../testEnvironmentConfig');
const tvm = require('../../tvmTicketsProvider');

const ATTRIBUTES = {
    FIRSTNAME: '27',
    LASTNAME: '28'
};

async function getUserinfo(user, options) {
    const queryArgs = {
        method: 'userinfo',
        userip: '127.0.0.1',
        format: 'json',
        find_by_phone_alias: 'force_on',
        aliases: 'all_with_hidden',
        emails: 'getall',
        get_public_id: 'yes',
        get_public_name: 'yes',
        regname: 'yes',
        attributes: [ATTRIBUTES.FIRSTNAME, ATTRIBUTES.LASTNAME].join(',')
    };

    if (user.uid) {
        queryArgs.uid = user.uid;
    } else if (user.login) {
        queryArgs.login = user.login;
    } else {
        throw new Error(`Не передан идентификатор аккаунта ${user}`);
    }
    Object.assign(queryArgs, options);

    return await request({
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
    })
        .then((response = {}) => response.body.users[0])
        .catch((error = {}) => error);
}

module.exports = {
    ATTRIBUTES,
    getUserinfo
};
