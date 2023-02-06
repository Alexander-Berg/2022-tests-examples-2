const CameraList = require('../../page/signalq/CameraList');

describe('SignalQ. Все камеры. Изменение столбцов таблицы.', () => {

    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('Нажимаем на кнопку настройки колонок', () => {
        CameraList.columnsSelectorButton.click();
    });

    it('поочередно скрыть все колонки таблицы', () => {
        let columnCount = CameraList.allColumns.length;

        CameraList.columnsEditSVG.forEach(element => {

            if (element.getCSSProperty('opacity').value === 0) {
                return;
            }

            element.click();
            columnCount--;
            expect(columnCount).toEqual(CameraList.allColumns.length);
        });
    });

    it('поочередно отобразить все колонки таблицы', () => {
        let columnCount = CameraList.allColumns.length;

        CameraList.columnsEditButtons.forEach((element, i) => {

            if (i === 0) {
                columnCount++;
                return;
            }

            element.click();
            expect(columnCount).toEqual(CameraList.allColumns.length);
            columnCount++;
        });
    });
});
