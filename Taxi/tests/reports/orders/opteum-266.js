const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsOrders = require('../../../page/ReportsOrders');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по заказам. Асинхронная выгрузка. Скачивание пустого файла', () => {

    const DATA = {
        file: 'report_orders.csv',
        report: [
            [
                'ID',
                'Статус',
                'Код заказа',
                'Водитель',
                'Водитель',
                'Автомобиль',
                'Автомобиль',
                'Дата подачи',
                'Дата завершения',
                'Адрес',
                'Категория',
                'Пробег, км',
                'Сумма при завершении на таксометре',
                'Наличные',
                'Оплата по карте',
                'Корпоративная оплата',
                'Чаевые',
                'Промоакции',
                'Бонусы',
                'Комиссия сервиса',
                'Комиссия парка',
                'Прочие платежи',
                'Платежи по поездкам парка',
            ],
        ],
    };

    let data;

    it('Открыть страницу отчёта по заказам', () => {
        ReportsOrders.goTo(
            '?date_from=20300731T000000%2B03%3A00&date_to=20300731T235900%2B03%3A00',
            {skipWait: true},
        );
    });

    it('Нажать на кнопку скачивания отчета', () => {
        ReportsOrders.table.buttons.download.click();
    });

    it('Открылся диалог сохранения отчёта', () => {
        expect(ReportDownloadDialog.title).toHaveElemVisible();
    });

    it('Переключить кодировку на utf8', () => {
        ReportDownloadDialog.radio.utf8.click();
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportDownloadDialog.buttons.download.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте корректные данные', () => {
        expect(data).toEqual(DATA.report);
    });

});
