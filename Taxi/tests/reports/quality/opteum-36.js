const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

describe('Выбор периода в разделе Качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo('?date_from=20190923T000000%2B03%3A00&date_to=20190929T000000%2B03%3A00');
    });

    it('Выбрать в календаре неделю с 02.09.2019 по 08.09.2019', () => {
        ReportsQuality.filtersBlock.calendar.waitForDisplayed();
        ReportsQuality.filtersBlock.calendar.click();
        ReportsQuality.calendarBlock.september2Year2019.waitForDisplayed();
        ReportsQuality.calendarBlock.september2Year2019.click();
        ReportsQuality.calendarBlock.september8Year2019.click();
    });

    it('Нажать кнопку Применить', () => {
        ReportsQuality.calendarBlock.applyButton.click();
        const calendar = ReportsQuality.filtersBlock.calendar.getValue().replace(/ /g, '');
        assert.include(calendar, '2сент.2019г.–8сент.2019г.');
        assert.equal(ReportsQuality.driversCount.getText(), 'Количество водителей: 210');
    });

});
