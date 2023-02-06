const PaymentRules = require('../../page/transferRequests/PaymentRules');

const drivers = [
    '2868425375 2868425375',
    '1178579566 1178579566',
];

describe('Правила выплат: Добавление водителей в правило', () => {
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

    it('Найти и выбрать несколько своих водителей', () => {
        for (const driver of drivers) {
            PaymentRules.clearWithBackspace(PaymentRules.driversSideMenu.driversSearchInput);
            PaymentRules.driversSideMenu.driversSearchInput.setValue(driver);
            browser.pause(2000);
            PaymentRules.driversSideMenu.drivers[0].waitForDisplayed();
            expect(PaymentRules.driversSideMenu.drivers[0]).toHaveTextEqual(driver);

            if (PaymentRules.driversSideMenu.checkboxes[0].getAttribute('aria-checked') !== 'false') {
                PaymentRules.driversSideMenu.checkboxes[0].click();
            }

            PaymentRules.driversSideMenu.checkboxes[0].click();
            expect(PaymentRules.driversSideMenu.checkboxes[0]).toHaveAttributeEqual('aria-checked', 'true');
        }

        PaymentRules.clearWithBackspace(PaymentRules.driversSideMenu.driversSearchInput);
    });

    it('Выбрать в сайд-меню таб "Включено"', () => {
        PaymentRules.driversSideMenu.tabs.enabled.click();
    });

    it('в списке присутствуют водители, выбранные на шаге 4', () => {
        for (const driver of drivers) {
            expect(PaymentRules.driversSideMenu.drivers).toHaveTextArrayIncludes(driver);
        }
    });

    it('все водители в списке с галкой', () => {
        expect(PaymentRules.driversSideMenu.checkboxes).toHaveAttributeArrayEachEqual('aria-checked', 'true');
    });
});
