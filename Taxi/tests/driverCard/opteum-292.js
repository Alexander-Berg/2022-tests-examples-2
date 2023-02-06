const SupportMessagesList = require('../../page/SupportMessagesList.js');

const timeToWaitElem = 15_000;

const testData = {
    theme: 'Вопросы о водителе',
    subTheme1: 'Обновить информацию о водителе',
    subTheme2: 'Редактирование карточки водителя',
    driverLicense: '5555566610',
    issueMessage: 'test message',
};

describe('Редактирование данных профиля водителя: создание обращения в техподдержку', () => {
    it('Создать новое обращение (кнопка + в левом верхнем углу раздела)', () => {
        SupportMessagesList.goTo();
        SupportMessagesList.addButton.waitForDisplayed({timeout: timeToWaitElem});
        SupportMessagesList.addButton.click();
        SupportMessagesList.createMessageForm.waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Создать обращение', () => {
        SupportMessagesList.createIssue(testData);
    });

    it('Нажать на данное обращение в списке обращений', () => {
        const firstIssue = $('tr td');
        firstIssue.click();
        SupportMessagesList.supportChatBlock.waitForDisplayed();

    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChatHeaders.status).toHaveText('В работе');
        expect(SupportMessagesList.supportChatHeaders.id).toBeDisplayed();
        expect(SupportMessagesList.supportChat.infoMessage.theme).toHaveTextContaining(testData.theme);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextContaining(testData.subTheme2);
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(testData.driverLicense);
        expect(SupportMessagesList.supportChat.imageMessage.img).toBeDisplayed();
        expect(SupportMessagesList.supportChat.imageMessage.text).toHaveTextContaining(testData.issueMessage);
    });
});
