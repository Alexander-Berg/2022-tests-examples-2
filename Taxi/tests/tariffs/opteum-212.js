const Tariffs = require('../../page/Tariffs.js');

const columnList = [
    'Колонки таблицы',
    'Название',
    'Посадка',
    'Минимальная стоимость',
    'Бесплатное ожидание(мин)',
    'Платное ожидание',
    'Включено км',
    'Включено мин',
    'Стоимость мин',
    'Стоимость км',
    'Стоимость км за городом',
    'Стоимость мин за городом',
];

describe('Тарифы. Изменение отображаемых столбцов', () => {
    it('Открыть раздел "Тарифы"', () => {
        Tariffs.goTo();
    });

    it('Открылась таблица со всеми столбцами', () => {
        expect(Tariffs.tableHeaders).toHaveElemLengthEqual(columnList.length - 1);
    });

    it('нажать на кнопку редактирования колонок таблицы', () => {
        Tariffs.btnEditTable.click();
    });

    it('отобразился список колонок таблицы', () => {
        expect(Tariffs.tableColumnsList).toHaveTextEqual(columnList);
    });

    it('скрыть все колонки таблицы, кроме "Название"', () => {
        for (let i = 2; i < Tariffs.tableColumnsList.length; i++) {
            if (Tariffs.tableColumnsListCheckboxes[i].isDisplayed()) {
                Tariffs.tableColumnsList[i].click();
            }
        }
    });

    it('Отобразилась таблица со стобцами "Название"', () => {
        const visibleColumnsCounter = 1;
        expect(Tariffs.tableHeaders).toHaveElemLengthEqual(visibleColumnsCounter);
    });
});
