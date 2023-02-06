const issuesList = require('../../page/SupportMessagesList');
const {assert} = require('chai');

describe('Смоук: саппорт: открыть старое обращение', () => {
    it('открыть список водителей', () => {
        issuesList.goTo();
    });

    it('открыть старое обращение в техподдержку', () => {
        issuesList.openIssue();
    });

    it('посчитать количество отправленных сообщений', () => {
        const oMessages = issuesList.outgoingMessages;
        const oCount = oMessages.length;
        assert.equal(oCount, 70);
    });

    it('посчитать количество полученный сообщений чата и проверить последнее сообщение', () => {
        const iMessages = issuesList.incomingMessages;
        const iCount = iMessages.length;
        assert.equal(iCount, 3);
        assert.equal('ТЫц тыц саппорт написал', iMessages[0].getText());
    });
});
