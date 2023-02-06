const Tariffs = require('../../page/Tariffs.js');

const vkoTariffs = ['econom'];
const zvenigorodTariffs = ['courier', 'econom'];

describe('Тарифы. Смена региона', () => {
    it('Открыть раздел "Тарифы"', () => {
        Tariffs.goTo('vko');
    });

    it('На странице присутствует таблица', () => {
        expect(Tariffs.tableHeaders).toBeDisplayed();
        expect(Tariffs.getRow(1)).toBeDisplayed();
        vkoTariffs.forEach(elem => expect(Tariffs.tableTariffs).toHaveTextArrayIncludes(elem));
    });

    it('На странице присутствует кнопки саджеста регионов', () => {
        expect(Tariffs.regionSelector).toBeDisplayed();
        expect(Tariffs.btnEditTable).toBeDisplayed();
    });

    it('Поменять регион с Moscow, на Zvenigorod', () => {
        Tariffs.regionSelector.click();
        Tariffs.selectDropdownItem('Zvenigorod');
        browser.pause(500);
        zvenigorodTariffs.forEach(elem => expect(Tariffs.tableTariffs).toHaveTextArrayIncludes(elem));
    });
});
