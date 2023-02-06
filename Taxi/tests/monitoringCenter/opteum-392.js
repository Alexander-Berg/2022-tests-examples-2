const MonitoringCenter = require('../../page/signalq/MonitoringCenter');
const Selenoid = require('../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../utils/files');

describe('SignalQ. Центр мониторинга. Выгрузка отчёта: фильтрация по дате', () => {

    const DATA = {
        file: 'events_7ad36bc7560449998acbe2c57a75c293_2021-08-23T21_00_00+0000_2021-08-24T20_59_59.999+0000.csv',
    };

    let data;

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Нажать на кнопку "Отчёт по всему транспорту"', () => {
        MonitoringCenter.allVehicleReportButton.click();
    });

    it('Выбрать дату за которую были события', () => {
        MonitoringCenter.getReport().dateInputFrom.click();
        MonitoringCenter.getReport().dateInputFrom.addValue(24_082_021);

        MonitoringCenter.getReport().dateInputTo.click();
        MonitoringCenter.getReport().dateInputTo.addValue(24_082_021);
    });

    it('Выбрать формат CSV', () => {
        MonitoringCenter.getReport().csv.click();
    });

    it('Нажать кнопку "загрузить"', () => {
        MonitoringCenter.getReport().downloadButton.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте отображаются корректные даты', () => {
        data.forEach((el, i) => {
            if (i === 0) {
                return;
            }

            expect(el[0]).toContain('2021-08-24');
        });
    });

});
