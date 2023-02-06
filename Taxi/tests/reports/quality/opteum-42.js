const ReportsQuality = require('../../../page/ReportsQuality');

const columnList = [
    'Колонки таблицы',
    'Водитель',
    'Позывной',
    'Телефон',
    'Условие работы',
    'ВУ',
    'Тариф',
    'Рейтинг на конец периода',
    'Изменение рейтинга за период',
    'Предложено заказов',
    'Жалобы на вынужденные отмены',
    'Успешно завершённые заказы',
    'Заказы с оценкой 1–3',
    'Основные жалобы пассажиров',
    'Нарушения стандартов сервиса',
    'Отлично выполненные заказы',
];

describe('Скрытие столбцов в таблице Качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Нажать на кнопку редактирования колонок таблицы', () => {
        ReportsQuality.editTableButton.click();
    });

    it('Отобразился список колонок таблицы', () => {
        expect(ReportsQuality.tableColumnsList).toHaveTextEqual(columnList);
    });

    it('Колонку "Водитель" нельзя скрыть', () => {
        const disabledColumnsCounter = 2;
        expect(ReportsQuality.tableColumnsListDisabledItems).toHaveElemLengthEqual(disabledColumnsCounter);
    });

    it('Поочередно скрыть все колонки таблицы', () => {
        for (let i = 2; i < ReportsQuality.tableColumnsList.length; i++) {
            if (ReportsQuality.tableColumnsListCheckboxes[i].isDisplayed()) {
                ReportsQuality.tableColumnsList[i].click();
            }
        }
    });

    it('Все колонки таблицы, кроме колонки "Водитель", скрыты', () => {
        const visibleColumnsCounter = 1;
        expect(ReportsQuality.tableHeaders).toHaveElemLengthEqual(visibleColumnsCounter);
    });

});
