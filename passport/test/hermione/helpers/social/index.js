const _ = require('lodash');

const mailAccountData = [
    {login: 'yndx-social-0001', password: '4cIa)OsAutA7'},
    {login: 'yndx-social-0002', password: '4cIa)OsAutA7'},
    {login: 'yndx-social-0003', password: '4cIa)OsAutA7'},
    {login: 'yndx-social-0004', password: '4cIa)OsAutA7'}
];

async function getMailAccountData() {
    return _.sample(mailAccountData);
}

module.exports = {
    getMailAccountData
};
