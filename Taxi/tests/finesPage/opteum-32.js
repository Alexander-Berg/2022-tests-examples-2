const FinesPage = require('../../page/FinesPage');

describe('Фильтрация по статусу оплаты', () => {
    it('Открыть страницу Штрафы', () => {
        FinesPage.goTo();
    });

    it('Выбрать фильтр "Оплачен"', () => {
        FinesPage.filtersBlock.filterPaid.waitForDisplayed();
        FinesPage.filtersBlock.filterPaid.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        FinesPage.placeholderNothingFound.waitForDisplayed();
        expect(FinesPage.placeholderNothingFound).toHaveTextEqual('Пока ничего нет');
    });

    it('Выбрать фильтр "Не оплачен"', () => {
        FinesPage.filtersBlock.filterNotPaid.waitForDisplayed();
        FinesPage.filtersBlock.filterNotPaid.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        FinesPage.resultTable.thirdUniqueIdentificator.waitForDisplayed();
        expect(FinesPage.resultTable.thirdUniqueIdentificator).toHaveTextEqual('18824178978995888880');
    });

});
