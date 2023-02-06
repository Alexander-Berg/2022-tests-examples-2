const ReportsSegments = require('../../../page/ReportsSegments');

describe('Скрытие и отображение полей в таблице сегменты водителей', () => {

    const DATA = {
        table: {
            columns: [
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
            ],
        },
        dropdown: {
            header: 'Колонки таблицы',
            itemsOff: [
                'Дата блокировки',
                'Причина блокировки',
            ],
        },
    };

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Отображаются корректные колонки таблицы', () => {
        expect(ReportsSegments.reportTable.header.columns).toHaveTextEqual(DATA.table.columns);
    });

    it('Открыть редактирование колонок', () => {
        ReportsSegments.table.columns.button.click();
    });

    it('Отображается корректный список колонок в дропдауне', () => {
        expect(ReportsSegments.reportTable.dropdown.list).toHaveTextEqual([
            DATA.dropdown.header,
            ...DATA.table.columns,
            ...DATA.dropdown.itemsOff,
        ].join('\n'));
    });

    it('При скрытии колонки она пропадает из таблицы', () => {
        ReportsSegments.reportTable.dropdown.checkedNotDisabled.forEach((elem, i, arr) => {
            ++i;

            elem.click();

            if (i < arr.length) {
                // т.к. кликаем на каждый элемент по очереди, значит из таблицы должны пропадать колонки начиная с первой
                // сравниваем с массивом всех колонок, вырезая из него ещё не нажатые колонки с начала массива
                expect(ReportsSegments.reportTable.header.columns).toHaveTextEqual(DATA.table.columns.slice(i));
            } else {
                // при скрытии последнего элемента таблица пропадает — проверяем, что её нет
                expect(ReportsSegments.getCells()).toHaveTextEqual('');
            }
        });
    });

    it('При выборе колонки она появляется в таблице', () => {
        ReportsSegments.reportTable.dropdown.itemNotDisabled.forEach((elem, i) => {
            ++i;

            elem.click();

            // т.к. кликаем на каждый элемент по очереди, значит в таблице должны появляться колонки начиная с первой
            // сравниваем с массивом всех колонок, вырезая из него ещё не нажатые колонки с конца массива
            expect(ReportsSegments.reportTable.header.columns).toHaveTextEqual([
                ...DATA.table.columns,
                ...DATA.dropdown.itemsOff,
            ].slice(0, i));
        });
    });

});
