const ListStatementsPage = require('../../page/ListStatementsPage');
const Selenoid = require('../../../../utils/api/Selenoid');
const StatementPage = require('../../page/StatementPage');
const {xlsParseToArray} = require('../../../../utils/files');

const xlsxFileName = 'financial-statement-37.xlsx';

const expectReport = [
    ['ID', 'ФИО', 'Телефон', 'Условия работы', 'Статус', 'Баланс', 'Выплата', 'Чистая выплата', 'Комиссия банка', 'Комиссия банка %', 'Комиссия банка не менее'],
    ['d6e8e8837d3017887d1fc359a8a5405e', 'Арсений Кабанчиков', '+79164563322', '4Q', 'Не работает', 0, 0, 0, 0, 0, 0],
    ['c5024efcb8c48e60d6500728802de1d2', 'Эдуард Ширяев', '+79937581199', '4Q', 'Не работает', 0, 0, 0, 0, 0, 0],
    ['baff42aa2af35e2d7b78c117c1082363', 'Андрей Егунов', '+79269873041', '4Q', 'Не работает', 0, 0, 0, 0, 0, 0],
    ['7cc559587389420db2002826c7f34e5e', 'Атанов Тест Пётр Оглы', '+70004520452', '4Q', 'Не работает', -75_443.3488, 0, 0, 0, 0, 0],
    ['7a43a051ea3949774629aba50a1b5046', 'G G G', '+70006810900', '4Q', 'Не работает', 0, 0, 0, 0, 0, 0],
    ['7531efd4070f40b3b8d18e6cd6a3e2a6', '111 111', '+111', '4Q', 'Не работает', 99, 0, 0, 0, 0, 0],
    ['6966cfa876cceb4a224b9e6448eb89ac', 'Тестер Тестерович Чебоксаров КвардратичноЦикличный', '+79871217838', '4Q', 'Не работает', 0, 0, 0, 0, 0, 0],
    ['542be2db474845ec965913e1d1ad7016', '111 111', '+111123', '4Q', 'Не работает', -300, 0, 0, 0, 0, 0],
    ['505450b5e4b743e180a9dd5743919a87', 'Авилов Владимир', '+79105866668', '4Q', 'Не работает', 100, 0, 0, 0, 0, 0],
    ['40fccb833da34c7095dff3bdf8c32de5', 'Минскмй # 100', '+70009001300', '4Q', 'Не работает', 84.8038, 0, 0, 0, 0, 0],
    ['0466f55911794f70a1e7ea0617f18a36', 'Усков1 Сергей Сергеевич', '+79267051276', '4Q', 'Не работает', -204_466, 0, 0, 0, 0, 0],
];

let data;

describe('Выгрузка ведомости в файл', () => {
    it('Открыть черновик ведомости с количеством водителей менее 1000, например "Ведомость #37" и нажать кнопку выгрузки файла', () => {
        ListStatementsPage.open('/financial-statements/a043f8ec-9e4f-404c-b20f-9ad320343372');

        StatementPage.waitingLoadThisPage(60_000);

        // в ведомости количество записей менее или равно 1000
        expect(
            Number.parseInt(StatementPage
                .getColumn(1)[0]
                .getText()
                .replace(/[^\d+]/g, '')),
        ).toBeLessThanOrEqual(1000);

    });

    it('Выбрать "Скачать XLSX"', () => {
        StatementPage.btnDownload.downloadIcon.click();
        StatementPage.btnDownload.xlsx.click();
    });

    it('скачивается файл в формате xlsx', () => {
        data = Selenoid.getDownloadedFile(xlsxFileName);
    });

    it('Открыть скаченный файл', () => {
        data = xlsParseToArray(data);
    });

    it('Данные в файле совпадают с данными в разделе', () => {
        expect(data).toEqual(expectReport);
    });
});
