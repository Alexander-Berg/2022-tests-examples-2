const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: настройка колонок: инкремент', () => {

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Открыть настройки колонок и деактивировать все пункты', () => {
        SignalQDrivers.columnsSelector.click();

        SignalQDrivers.columnsSelectorItems.forEach((el, i) => {

            if (i > 1 && SignalQDrivers.columnsSelectorChecks(i + 1).isDisplayed()) {
                el.click();
            }
        });

        SignalQDrivers.columnsSelector.click();
    });

    it('Нажать на кнопку настройки колонок возле кнопки в виде зацикленной стрелки', () => {
        SignalQDrivers.columnsSelector.click();
    });

    it('По очереди нажать на все строки списка колонок', () => {
        SignalQDrivers.columnsSelectorItems.forEach((el, i) => {

            if (i <= 1) {
                expect(el).not.toBeClickable();
            }

            if (i > 1) {
                el.click();
                expect($(`th=${el.getText()}`)).toExist();
            }

            if (i > 0) {
                expect(SignalQDrivers.columnsSelectorChecks(i + 1).isDisplayed()).toBeTruthy();
            }
        });
    });
});
