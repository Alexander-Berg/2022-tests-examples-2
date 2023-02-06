const SupportMessagesList = require('../../page/SupportMessagesList.js');

describe('Поиск обращений: по заказу', () => {

    const orderNumber = '123';
    const criterion = 'По заказу';

    it('Открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('В критерии поиска выбрать "По заказу"', () => {
        SupportMessagesList.filters.criterion.click();
        SupportMessagesList.selectDropdownItem(criterion);
    });

    it(`В поле поиска указать номер заказа ${orderNumber}`, () => {
        SupportMessagesList.filters.searchInput.setValue(orderNumber);
    });

    it('Открыть первое обращение', () => {
        browser.pause(2000);
        SupportMessagesList.getRow(1).click();
    });

    it('В сайдбаре отображается номер обращения', () => {
        SupportMessagesList.supportChatBlock.waitForDisplayed();
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(orderNumber);
    });

});
