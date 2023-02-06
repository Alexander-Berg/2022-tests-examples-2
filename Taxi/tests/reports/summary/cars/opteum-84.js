const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Скрытие и отображение полей в сводном отчете по автомобилям', () => {

    const DATA = {
        table: {
            columns: [
                'Автомобиль',
                'Водители со списаниями',
                'Сдаваемость',
                'Категории',
                'Успешно выполненные заказы',
                'Км на заказах',
                'Наличные',
                'Безналичные',
                'Аренда',
            ],
        },
        dropdown: {
            header: 'Колонки таблицы',
        },
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Отображаются корректные колонки таблицы', () => {
        expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.table.columns);
    });

    it('Открыть редактирование колонок', () => {
        ReportsSummary.table.buttons.columns.click();
    });

    it('Отображается корректный список колонок в дропдауне', () => {
        expect(ReportsSummary.reportTable.dropdown.list).toHaveTextEqual([
            DATA.dropdown.header,
            ...DATA.table.columns,
        ].join('\n'));
    });

    it('При скрытии колонки она пропадает из таблицы', () => {
        ReportsSummary.reportTable.dropdown.checkedNotDisabled.forEach((elem, i, arr) => {
            ++i;

            elem.click();

            if (i < arr.length) {
                // т.к. кликаем на каждый элемент по очереди, значит из таблицы должны пропадать колонки начиная с первой
                // сравниваем с массивом всех колонок, вырезая из него ещё не нажатые колонки с начала массива
                expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.table.columns.slice(i));
            } else {
                // при скрытии последнего элемента таблица пропадает — проверяем, что её нет
                expect(ReportsSummary.getCells()).toHaveTextEqual('');
            }
        });
    });

    it('При выборе колонки она появляется в таблице', () => {
        ReportsSummary.reportTable.dropdown.itemNotDisabled.forEach((elem, i) => {
            ++i;

            elem.click();

            // т.к. кликаем на каждый элемент по очереди, значит в таблице должны появляться колонки начиная с первой
            // сравниваем с массивом всех колонок, вырезая из него ещё не нажатые колонки с конца массива
            expect(ReportsSummary.reportTable.header.columns).toHaveTextEqual(DATA.table.columns.slice(0, i));
        });
    });

});
