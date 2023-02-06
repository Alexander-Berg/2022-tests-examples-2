const FinesPage = require('../../page/FinesPage');

describe('Поиск по гос. номеру или СТС', () => {
    it('Открыть страницу Штрафы', () => {
        FinesPage.goTo();
    });

    it('В поле поиска ввести гос. номер "000" и выбрать любую найденную машину', () => {
        FinesPage.filtersBlock.searchField.setValue('000');
        FinesPage.filtersBlock.thirdDriverInSearch.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        browser.pause(2000);
        expect(FinesPage.resultTable.firstUniqueIdentificator).toHaveTextEqual('18824100000015707723');
    });

    it('Очистить поле поиска', () => {
        FinesPage.filtersBlock.clearSearchField.click();
    });

    it('В поле поиска ввести СТС "2839" и выбрать любую найденную машину', () => {
        FinesPage.filtersBlock.searchField.setValue('2839');
        FinesPage.filtersBlock.the7thDriverInSearch.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        browser.pause(2000);
        expect(FinesPage.resultTable.firstUniqueIdentificator).toHaveTextEqual('18824182882839623295');
    });

    it('Очистить поле поиска', () => {
        FinesPage.filtersBlock.clearSearchField.click();
    });

    it('В поле поиска ввести "852258" и проверить результат', () => {
        FinesPage.filtersBlock.searchField.setValue('852258');
        expect(FinesPage.filtersBlock.firstDriverInSearch).toHaveTextEqual('Нет совпадений');
    });

});
