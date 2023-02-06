const SignalQDrivers = require('../../page/signalq/SignalQDrivers');
const {nanoid} = require('nanoid');

describe('SignalQ: водители: Поиск: негатив', () => {

    const str = `opt533${nanoid(10)}`;

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Ввести в строку поиска Текст не соответствющий ВУ/ФИО/телефону ни одного водителя в списке', () => {

        SignalQDrivers.searchInput.click();
        SignalQDrivers.searchInput.addValue(str);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('Отобразился плейсхолдер "тут ничего нет"', () => {
        expect(SignalQDrivers.noDataAvailable).toHaveTextEqual('Тут ничего нет');
        expect(SignalQDrivers.resetFilters).toExist();
    });

    it('Сбросить фильтр', () => {
        SignalQDrivers.resetFilters.click();
        SignalQDrivers.searchInput.click();
        expect(SignalQDrivers.searchInput.getAttribute('value')).toEqual('');
    });

});
