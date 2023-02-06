const supportList = require('../../page/SupportMessagesList.js');
const {assert} = require('chai');

describe('Смоук: создать обращение в поддержку', () => {
    it('открыть список обращений', () => {
        supportList.goTo();
    });

    it('открыть и заполнить форму нового обращения', () => {
        supportList.addButton.click();
        supportList.selectDefaultTheme();
        supportList.selectDefaultPhone();
    });

    it('отправить обращение и проверить ответ сервера', () => {
        browser.setupInterceptor();
        supportList.confirmIssueButton.click();
        const requests = browser.getRequests();
        const newIssue = requests.find(el => el.url.includes('/support-chat-api/v2/new'));
        const issueId = newIssue.response.body.chat.id;

        const list = requests.find(el => el.url.includes('/api/support-chat-api/v1/list'));
        const issues = list.response.body.chats;

        let isCreated = false;

        issues.forEach(el => {
            if (el.id === issueId) {
                isCreated = true;
            }
        });

        assert.isTrue(isCreated);
    });
});
