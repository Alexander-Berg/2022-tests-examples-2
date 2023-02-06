const SupportMessagesList = require('../../page/SupportMessagesList.js');

const testData = {
    theme: 'Вопросы о водителе',
    subTheme1: 'Обновить информацию о водителе',
    subTheme2: 'Редактирование карточки водителя',
    driverLicense: '5555566610',
    issueMessage: 'test message',
};

describe('Создание нового обращения: мне и моей роли', () => {
    it('Нажать "+" в заголовке страницы', () => {
        SupportMessagesList.goTo();
        SupportMessagesList.addButton.waitForDisplayed();
        SupportMessagesList.addButton.click();
        SupportMessagesList.createMessageForm.waitForDisplayed();
    });

    it('Создать обращение', () => {
        SupportMessagesList.createIssue(testData);
        SupportMessagesList.alert.waitForDisplayed();
        expect(SupportMessagesList.alert).toHaveText('Ваше обращение зарегистрировано');
    });

    it('Нажать на данное обращение в списке обращений', () => {
        $('tr td').click();
        $('div[class*="SupportChat_container"]').waitForDisplayed();
    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChat.infoMessage.theme).toHaveTextContaining(testData.theme);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextContaining(testData.subTheme2);
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(testData.driverLicense);
        expect(SupportMessagesList.supportChat.imageMessage.img).toBeDisplayed();
        expect(SupportMessagesList.supportChat.imageMessage.text).toHaveTextContaining(testData.issueMessage);
    });
});
