const SupportMessagesList = require('../../page/SupportMessagesList.js');

const testData = {
    phoneNumber: '+70001259508',
    name: 'Иванов Иван Иванович',
    email: 'dptest1@yandex.ru',
};

describe('Заказ обратного звонка: создать обращение с данными по умолчанию', () => {
    it('Нажать на иконку телефонной трубки в заголовке страницы', () => {
        SupportMessagesList.goTo();
        SupportMessagesList.phoneBtn.waitForDisplayed();
        SupportMessagesList.phoneBtn.click();
        SupportMessagesList.createMessageForm.waitForDisplayed();
    });

    it('Проверить данные сотрудника', () => {
        expect(SupportMessagesList.email).toHaveValue(testData.email);
        expect(SupportMessagesList.selectedPhone).toHaveTextIncludes(testData.phoneNumber);
        expect(SupportMessagesList.selectedName).toHaveTextEqual(testData.name);
    });

    it('Отправить обращение не заполняя остальные поля', () => {
        SupportMessagesList.sendIssueAndCheckResponse();
        SupportMessagesList.alert.waitForDisplayed();
        expect(SupportMessagesList.alert).toHaveText('Ваше обращение зарегистрировано');
    });

    it('Нажать на данное обращение в списке обращений', () => {
        $('tr td').click();
        $('div[class*="SupportChat_container"]').waitForDisplayed();
    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChat.infoMessage.email).toHaveTextIncludes(testData.email);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextIncludes(testData.phoneNumber);
    });
});
