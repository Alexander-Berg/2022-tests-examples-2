const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsSegments = require('../../../page/ReportsSegments');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Выгрузка сегментов водителей в CSV', () => {

    const DATA = {
        file: {
            name: 'file',
            ext: '.csv',
        },
        title: 'Выберите кодировку, в которой хотите сохранить отчёт',
        button: 'Скачать',
        report: [
            'Статус',
            'Позывной',
            'ФИО',
            'Дата последнего заказа',
            'Дата принятия',
            'Комментарий',
            'Телефон',
            'Email',
            'Баланс',
            'Лимит',
            'Условие работы',
            'Автомобиль',
            'Дата блокировки',
            'Причина блокировки',
        ],
        encodings: ['cp1251', 'utf8', 'mac'],
    };

    let data;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Дождаться отображения таблицы', () => {
        ReportsSegments.getCells({td: 1, tr: 1}).waitForDisplayed();
    });

    DATA.encodings.forEach((elem, i) => {

        describe(`Кодировка "${elem}"`, () => {

            it('Нажать на кнопку сохранения отчёта', () => {
                ReportsSegments.table.report.button.click();
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
                // segments_report (1).csv
                // segments_report (2).csv
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
