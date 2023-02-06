const SupportMessagesList = require('../../page/SupportMessagesList.js');

const selectedDate = '13 янв. 2022 г.';

describe('Фильтрация обращений по периоду', () => {
    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.open('/support?status=all&from=2022-01-13&to=2022-01-16&park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru');
    });

    it('Указать любой период за который есть обращения', () => {
        SupportMessagesList.filters.dateInput.waitForDisplayed();
        SupportMessagesList.filters.dateInput.click();
        SupportMessagesList.datePicker.btnStart.waitForDisplayed();
        SupportMessagesList.datePicker.btnStart.click();
        SupportMessagesList.datePicker.btnStart.click();
        SupportMessagesList.datePicker.btnApply.click();
        browser.pause(2000);
        SupportMessagesList.getRow(1).waitForDisplayed();
    });

    it('отображается список обращений согласно фильтру', () => {
        const dates = SupportMessagesList.getColumn(8)
            .map(elem => elem.getText())
            .filter(elem => elem.includes(selectedDate));

        expect(dates.length).toEqual(SupportMessagesList.getColumn(8).length);
    });

    it('Очистить фильтр', () => {
        SupportMessagesList.filters.dateInputBtnClear.click();
        browser.pause(2000);
        SupportMessagesList.getRow(1).waitForDisplayed();
    });

    it('отображается список всех обращений', () => {
        const dates = SupportMessagesList.getColumn(8)
            .map(elem => elem.getText())
            .filter(elem => !elem.includes(selectedDate));

        expect(dates.length).toBeGreaterThan(0);
    });
});
