const DriverCard = require('../../page/driverCard/DriverCard');
const PaymentRules = require('../../page/transferRequests/PaymentRules');

describe('Правила выплат: переход в карточку водителя из таба "Включено"', () => {

    let driverName, link;

    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Навести курсор на запись правила', () => {
        PaymentRules.getRow(1).moveTo();
    });

    it('в строке с правилом отображаются две кнопки действия с правилом: добавление водителя и редактирование правила', () => {
        expect(PaymentRules.editButtons[0]).toBeDisplayed();
        expect(PaymentRules.driversButtons[0]).toBeDisplayed();
    });

    it('Нажать кнопку добавления водителя', () => {
        PaymentRules.driversButtons[0].click();
    });

    it('открылась форма добавления водителя(ей) в правило', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed();
    });

    it('выбран таб "Все"', () => {
        expect(PaymentRules.driversSideMenu.tabs.all).toHaveAttribute('checked');
    });

    it('Включить любого водителя в правило', () => {
        if (PaymentRules.driversSideMenu.checkboxes[1].getAttribute('aria-checked') !== 'true') {
            PaymentRules.driversSideMenu.checkboxes[1].click();
        }
    });

    it('Перейти в таб "Включено"', () => {
        PaymentRules.driversSideMenu.tabs.enabled.click();
        browser.pause(500);
        PaymentRules.driversSideMenu.drivers[0].waitForDisplayed();
    });

    it('Нажать на "стрелку" в строке любого водителя', () => {
        driverName = PaymentRules.driversSideMenu.drivers[0].getText();
        PaymentRules.driversSideMenu.arrows[0].click();
    });

    it('появилась строка "Перейти в профиль" со ссылкой на карточку этого водителя', () => {
        expect(PaymentRules.driversSideMenu.linkToDriver).toBeDisplayed();
        expect(PaymentRules.driversSideMenu.linkToDriver).toHaveTextIncludes('Перейти в профиль');
        expect(PaymentRules.driversSideMenu.linkToDriver).toHaveAttributeContaining('href', '/drivers');
    });

    it('Кликнуть по "Перейти в профиль"', () => {
        link = PaymentRules.driversSideMenu.linkToDriver.getAttribute('href');
        PaymentRules.driversSideMenu.linkToDriver.click();
        PaymentRules.switchTab();
    });

    it('открылась карточка водителя', () => {
        expect(browser).toHaveUrlContaining(link);
    });

    it('данные ФИО водителя в карточке совпадают с данными водителя из шага 4', () => {
        DriverCard.waitingLoadThisPage(15_000);
        expect(driverName).toContain(DriverCard.driverNameAndSoname.getText());
    });
});
