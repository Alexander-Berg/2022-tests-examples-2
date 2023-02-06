const MonitoringCenter = require('../../page/signalq/MonitoringCenter');
const Selenoid = require('../../../../utils/api/Selenoid');
const {xlsParseToArray} = require('../../../../utils/files');

describe('SignalQ. Центр мониторинга. Выгрузка отчёта событий по всему транспорту', () => {
    const SN = 'У004УУ78';

    const DATA = {
        dates: {
            from: '24082021',
            to: '24082021',
        },
        file: 'events_7ad36bc7560449998acbe2c57a75c293_2021-08-23T21_00_00+0000_2021-08-24T20_59_59.999+0000.xlsx',
        report: {
            title: ['Время события', 'Тип события', 'Скорость', 'Водитель', 'Серийный номер', 'Резолюция', 'Гос. номер', 'Позывной', 'Ссылка на событие'],
        },
    };

    let data;

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Выбрать камеру из списка', () => {
        browser.pause(1000);
        const position = MonitoringCenter.findCameraPositionBySN(SN);
        MonitoringCenter.getSN(position).click();
    });

    it('Нажать на "бургер" расположенный под SN в профиле камеры', () => {
        MonitoringCenter.currentCameraReportButton.waitForDisplayed();
        MonitoringCenter.currentCameraReportButton.click();
    });

    it('Выбрать дату за которую были события', () => {
        MonitoringCenter.getReport().dateInputFrom.setValue(DATA.dates.from);
        MonitoringCenter.getReport().dateInputTo.setValue(DATA.dates.to);
    });

    it('Нажать кнопку "загрузить"', () => {
        MonitoringCenter.getReport().downloadButton.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = xlsParseToArray(data);
    });

    it('В сохраненном отчёте отображаются корректные заголовки', () => {
        expect(data.shift()).toEqual(DATA.report.title);
    });

    it('В сохраненном отчёте отображаются корректные даты', () => {
        data.forEach(elem => expect(String(elem[0])).toMatch(/^\d{5}\.\d{10}$/));
    });

    it('В сохраненном отчёте отображаются корректные события', () => {
        data.forEach(elem => expect(elem[1]).toEqual('sleep'));
    });

    it('В сохраненном отчёте отображаются корректные скорости', () => {
        data.forEach(elem => expect(String(elem[2])).toMatch(/^\d{1,3}$/));
    });

    it('В сохраненном отчёте отображаются корректные серийные номера', () => {
        data.forEach(elem => expect(elem[4]).toBeTruthy());
    });

    it('В сохраненном отчёте отображаются корректные гос номера номера', () => {
        data.forEach(elem => expect(elem[6]).toBeTruthy());
    });

    it('В сохраненном отчёте отображаются корректные позывные', () => {
        data.forEach(elem => expect(elem[7]).toBeTruthy());
    });

    it('В сохраненном отчёте отображаются корректные ссылки', () => {
        data.forEach(elem => expect(elem[8]).toContain('https://fleet.tst.yandex.ru/signalq/stream/fHwwNmM5YTA4ZjgzYWQ0ZjEzYjA1ZTQyOGUxYTRmYjgyMQ/'));
    });

});
