const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Выгрузка отчета в файл', () => {

    const DATA = {
        file: {
            name: 'summary_cars',
            ext: '.csv',
        },
        title: 'Выберите кодировку, в которой хотите сохранить отчёт',
        button: 'Скачать',
        report: [
            'ID автомобиля',
            'Автомобиль',
            'Водители со списаниями',
            'Успешно выполненные заказы',
            'Км на заказах',
            'Наличные',
            'Безналичные',
            'Аренда',
            'Удержано с СМЗ/ИП за аренду',
            'Было запланировано к списанию',
            'Отмена удержания аренды',
            'Ожидается к удержанию с СМЗ/ИП',
            'Сдаваемость',
            'Дни со списанием аренды',
        ],
        encodings: ['cp1251', 'utf8', 'mac'],
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/cars?date_from=2022-02-14&date_to=2022-02-14');
    });

    it('Дождаться отображения таблицы', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).waitForDisplayed();
    });

    DATA.encodings.forEach((elem, i) => {

        describe(`Кодировка "${elem}"`, () => {

            it('Нажать на кнопку сохранения отчёта', () => {
                ReportsSummary.table.buttons.download.click();
            });

            it('Открылся диалог сохранения отчёта', () => {
                expect(ReportDownloadDialog.title).toHaveTextEqual(DATA.title);
            });

            it(`Переключить кодировку на "${elem}"`, () => {
                ReportDownloadDialog.radio[elem].click();
            });

            it(`Отображается кнопка "${DATA.button}"`, () => {
                expect(ReportDownloadDialog.buttons.download).toHaveTextEqual(DATA.button);
            });

            it(`Нажать на кнопку "${DATA.button}"`, () => {
                ReportDownloadDialog.buttons.download.click();
            });

            it('Отчёт сохранился', () => {
                // при следующих сохранениях файла с тем же названием, браузер добавляет в имя индекс
                // summary_report (1).csv
                // summary_report (2).csv
                const fileName = i > 0
                    ? `${DATA.file.name} (${i})`
                    : DATA.file.name;

                data = Selenoid.getDownloadedFile(fileName + DATA.file.ext);
            });

            it('Распарсить отчёт', () => {
                data = csvUtf8ParseToArray(data);
            });

            it('В сохраненном отчёте есть данные', () => {
                expect(data.length).toBeGreaterThan(1);
            });

            // русский текст проверяем только в "нормальной" utf-8 кодировке
            if (elem === 'utf8') {
                it('В сохраненном отчёте отображаются корректные столбцы', () => {
                    expect(data[0]).toEqual(DATA.report);
                });
            }

        });

    });

});
