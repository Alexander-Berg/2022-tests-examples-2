const tvm = require('@yandex-int/tvm');

process.env.TVMTOOL_LOCAL_AUTHTOKEN = 'tvmtool-development-access-token';

const tvmClient = new tvm.Client({
    daemonBaseUrl: 'http://localhost:11111',
    serviceTicketCacheEnabled: true
});

const PASSPORT_INTERNAL_DSTS = {
    dev: 'passport-api-test',
    test: 'passport-api-test',
    rc: 'passport-api-prod',
    prod: 'passport-api-prod',
    'team-test': 'passport-api-team-test',
    team: 'passport-api-team'
};

const BLACKBOX_DSTS = {
    dev: 'blackbox-test',
    test: 'blackbox-test',
    rc: 'blackbox-mimino',
    prod: 'blackbox-mimino',
    'team-test': 'blackbox-test',
    team: 'blackbox-team'
};

module.exports.getQAProxyTicket = () => tvmClient.getServiceTicket('passport-qa-proxy');
module.exports.getPassportInternalTicket = () => {
    return tvmClient.getServiceTicket(PASSPORT_INTERNAL_DSTS[process.env.TEST_ENV]);
};
module.exports.getBlackboxTicket = () => tvmClient.getServiceTicket(BLACKBOX_DSTS[process.env.TEST_ENV]);
