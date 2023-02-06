const MonitoringCenter = require('../../page/signalq/MonitoringCenter');
const Selenoid = require('../../../../utils/api/Selenoid');
const {xlsParseToArray} = require('../../../../utils/files');

describe('SignalQ. Центр мониторинга. Выгрузка отчёта: фильтрация по дате (негатив)', () => {

    const DATA = {
        file: 'events_7ad36bc7560449998acbe2c57a75c293_2021-12-11T21_00_00+0000_2021-12-12T20_59_59.999+0000.xlsx',
        report: [
            ['Время события', 'Тип события', 'Скорость', 'Водитель', 'Серийный номер', 'Резолюция', 'Гос. номер', 'Позывной', 'Ссылка на событие'],
        ],
    };

    let data;

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Нажать на кнопку "Отчёт по всему транспорту"', () => {
        MonitoringCenter.allVehicleReportButton.click();
    });

    it('Выбрать дату за которую небыло событий', () => {
        MonitoringCenter.getReport().dateInputFrom.click();
        MonitoringCenter.getReport().dateInputFrom.addValue(12_122_021);

        MonitoringCenter.getReport().dateInputTo.click();
        MonitoringCenter.getReport().dateInputTo.addValue(12_122_021);
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

    it('В сохраненном отчёте отображаются корректные данные (Отчёт пустой)', () => {
        expect(data).toEqual(DATA.report);
    });

});
