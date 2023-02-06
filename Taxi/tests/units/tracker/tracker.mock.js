const config = require('../../../server/config');

const randomNumber = Date.now();

module.exports = {
    editTicket: [
        'FMTAXIRELTEST-63',
        {
            description: randomNumber,
        },
    ],
    sendComment: [
        'FMTAXIRELTEST-63',
        randomNumber,
    ],
    editComment: {
        key: 'FMTAXIRELTEST-63',
        text: randomNumber,
        commentId: '5f9a910ea9cd950f76f19623',
    },
    searchTask: {
        key: 'FMTAXIRELTEST-63',
    },
    transfer: [
        ['FMTAXIRELTEST-63'],
    ],
    testTicket: 'FMTAXIRELTEST-63',
    wrongTestTicket: 'FMTAXIRELTEST123-63',
    testService: 'test-service',
    TEFBoard: 5314,
};
