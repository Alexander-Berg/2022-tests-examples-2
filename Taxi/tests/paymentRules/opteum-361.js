const PaymentRules = require('../../page/transferRequests/PaymentRules');

const drivers = [
    '2868425375 2868425375',
    '1178579566 1178579566',
];

const searchDriver = driverName => {
    PaymentRules.clearWithBackspace(PaymentRules.driversSideMenu.driversSearchInput);
    PaymentRules.driversSideMenu.driversSearchInput.setValue(driverName);
    browser.pause(1000);
    $(`span=${driverName}`).waitForDisplayed();
};

describe('Правила выплат: Исключение водителей из правила', () => {
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
            searchDriver(driver);

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

    it('Снять галку с водителей из шага 3', () => {
        for (const driver of drivers) {
            searchDriver(driver);
            PaymentRules.driversSideMenu.checkboxes[0].click();
            expect(PaymentRules.driversSideMenu.checkboxes[0]).toHaveAttributeEqual('aria-checked', 'false');
        }

        PaymentRules.clearWithBackspace(PaymentRules.driversSideMenu.driversSearchInput);
    });

    it('Перейти в таб "Все"', () => {
        PaymentRules.driversSideMenu.tabs.all.click();
    });

    it('Найти водителей из шага 3, у водителей не проставлен чекбокс, у водителей отсутствует правило', () => {
        for (const driver of drivers) {
            searchDriver(driver);
            expect(PaymentRules.driversSideMenu.checkboxes[0]).toHaveAttributeEqual('aria-checked', 'false');
        }

        PaymentRules.clearWithBackspace(PaymentRules.driversSideMenu.driversSearchInput);
    });

    it('Перейти в таб "Включено"', () => {
        PaymentRules.driversSideMenu.tabs.enabled.click();
        browser.pause(1000);
    });

    it('водители из шага 3 отсутствуют в списке', () => {
        try {
            PaymentRules.driversSideMenu.drivers[0].waitForDisplayed({timeout: 2000, reverse: true});
        } catch {
            for (const driver of drivers) {
                const driversList = PaymentRules.driversSideMenu.drivers
                    .map(elem => elem.getText())
                    .filter(elem => elem === driver);

                expect(driversList.length).toEqual(0);
            }
        }
    });
});
