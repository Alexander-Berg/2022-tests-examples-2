const FinesPage = require('../../page/FinesPage');

describe('Выбор периода отображения штрафов', () => {
    it('Открыть страницу Штрафы', () => {
        FinesPage.goTo('?date_from=20191203T000000%2B03%3A00&date_to=20191204T235900%2B03%3A00');
    });

    it('На странице штрафов выбрать 11 дек. 2019 г. – 11 дек. 2019 г. (один день)', () => {
        FinesPage.filtersBlock.calendar.click();
        browser.pause(2000);
        FinesPage.calendarBlock.december11Year2019.click();
        FinesPage.calendarBlock.december11Year2019.click();
        FinesPage.calendarBlock.applyButton.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        browser.pause(2000);
        expect(FinesPage.resultTable.firstUniqueIdentificator).toHaveTextEqual('18824177777772222224');
    });

    it('На странице штрафов выбрать 1 дек. 2019 г. – 29 февр. 2020 г.', () => {
        FinesPage.goTo();
    });

    it('Отображение штрафов после фильтрации', () => {
        FinesPage.resultTable.thirdUniqueIdentificator.waitForDisplayed();
        expect(FinesPage.resultTable.thirdUniqueIdentificator).toHaveTextEqual('18824178978995888880');
    });

    it('На странице штрафов выбрать 1 февр. 2020 г. – 31 мар. 2020 г.', () => {
        FinesPage.filtersBlock.calendar.click();
        FinesPage.calendarBlock.nextMonth[1].click();
        FinesPage.calendarBlock.nextMonth[1].click();
        FinesPage.calendarBlock.february1Year2020.click();
        FinesPage.calendarBlock.nextMonth[1].click();
        FinesPage.calendarBlock.march31Year2020.click();
        FinesPage.calendarBlock.applyButton.click();
        browser.pause(2000);
    });

    it('Отображение штрафов после фильтрации', () => {
        FinesPage.resultTable.the50thUniqueIdentificator.waitForDisplayed();
        expect(FinesPage.resultTable.the50thUniqueIdentificator).toHaveTextEqual('18824472772735662629');
    });

    it('Нажать на кнопку "Загрузить еще"', () => {
        FinesPage.loadMoreButton.click();
    });

    it('Отображение штрафов после фильтрации', () => {
        FinesPage.resultTable.the100thUniqueIdentificator.waitForDisplayed();
        expect(FinesPage.resultTable.the100thUniqueIdentificator).toHaveTextEqual('18824673773786483917');
    });

});
