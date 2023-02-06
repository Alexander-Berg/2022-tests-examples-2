const moment = require('moment');
const PaymentRules = require('../../page/transferRequests/PaymentRules');

moment.locale('ru');

const columnList = [
    'Колонки таблицы',
    'название',
    'комиссия парка, %',
    'Мин. комиссия,  ₽',
    'мин. сумма',
    'макс. сумма',
    'Макс. сумма вывода в день, ₽',
    'Минимальный баланс',
    'дата создания',
    'дата изменения',
];

const columnsWithSort = [
    'комиссия парка, %',
    'макс. сумма',
    'дата создания',
    'дата изменения',
];

// получаем даты, парсим их по маске, получаем эпохальное время
// количество миллисекунд с 1970 года до полученной даты в колонке
const getDatesColumn = columnNumber => PaymentRules
    .getColumn(columnNumber)
    .map(elem => moment(elem.getText(), 'D MMM YYYY г., HH:mm').valueOf());

const checkDateSort = (sortSymbolNumber, columnNumber) => {
    PaymentRules.tableSortSymbols[sortSymbolNumber].click();
    // проверяем что полученный массив равен тому же массиву с сортировкой от меньшего к большему
    expect(getDatesColumn(columnNumber)).toEqual(getDatesColumn(columnNumber).sort((a, b) => a - b));

    // сортируем в другую сторону
    PaymentRules.tableSortSymbols[sortSymbolNumber].click();
    // проверяем что полученный массив равен тому же массиву с сортировкой от большего к меньшему
    expect(getDatesColumn(columnNumber)).toEqual(getDatesColumn(columnNumber).sort((a, b) => b - a));
};

const getNumbersFromColumn = columnNumber => PaymentRules
    .getColumn(columnNumber)
    .map(elem => Number(elem.getText().replace(',', '.')));

const checkNumbersSort = (sortSymbolNumber, columnNumber) => {
    PaymentRules.tableSortSymbols[sortSymbolNumber].click();
    // проверяем что полученный массив равен тому же массиву с сортировкой от меньшего к большему
    expect(getNumbersFromColumn(columnNumber)).toEqual(getNumbersFromColumn(columnNumber).sort((a, b) => a - b));

    // сортируем в другую сторону
    PaymentRules.tableSortSymbols[sortSymbolNumber].click();
    // проверяем что полученный массив равен тому же массиву с сортировкой от большего к меньшему
    expect(getNumbersFromColumn(columnNumber)).toEqual(getNumbersFromColumn(columnNumber).sort((a, b) => b - a));
};

describe('Сортировка таблицы с правилами по колонкам', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('нажать на кнопку редактирования колонок таблицы', () => {
        PaymentRules.btnEditTable.click();
    });

    it('отобразился список колонок таблицы', () => {
        expect(PaymentRules.tableColumnsList).toHaveTextEqual(columnList);
    });

    it('отобразить все колонки таблицы', () => {
        for (let i = 2; i < PaymentRules.tableColumnsList.length; i++) {
            if (!PaymentRules.tableColumnsListCheckboxes[i].isDisplayed()) {
                PaymentRules.tableColumnsList[i].click();
            }
        }
    });

    it('отображаются все колонки таблиц', () => {
        expect(PaymentRules.tableHeaders).toHaveElemLengthEqual(columnList.length);
    });

    it(`Проверить, что столбцы имеют возможность сортировки: ${columnsWithSort.join()}`, () => {
        expect(PaymentRules.tableSortSymbols).toHaveElemLengthEqual(columnsWithSort.length);
        expect(PaymentRules.tableSortSymbols).toBeDisplayed();
    });

    for (const [i, column] of columnsWithSort.entries()) {
        it(`Проверить сортировку в столбце "${column}"`, function() {
            switch (column) {
                case 'комиссия парка, %':
                    // https://st.yandex-team.ru/FLEETWEB-2434
                    this.skip();
                    checkNumbersSort(i, 2);
                    break;
                case 'макс. сумма':
                    // https://st.yandex-team.ru/FLEETWEB-2434
                    this.skip();
                    checkNumbersSort(i, 5);
                    break;
                case 'дата создания':
                    checkDateSort(i, 8);
                    break;
                case 'дата изменения':
                    checkDateSort(i, 9);
                    break;
                default:
                    throw new Error(`unexpected column: ${column}`);
            }
        });
    }
});
