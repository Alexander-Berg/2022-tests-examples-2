const PaymentsCalendar = require('../../../../page/PaymentsCalendar');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Отслеживание сдаваемости авто', () => {

    const DATA = {
        elemsAtTable: 25,
    };

    let savedCar;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Отображаются данные в колонке "Сдаваемость"', () => {
        expect(ReportsSummary.getCells({td: 3})).toHaveTextOk();
    });

    it('Сохранить первую машину со списаниями', () => {
        for (let tr = 1; tr <= DATA.elemsAtTable; tr++) {
            const writeDown = ReportsSummary.getCells({tr, td: 3}).getText();

            // если списание начинается с цифры
            if (writeDown.match(/^\d+/)) {
                [, savedCar] = ReportsSummary.getCells({tr, td: 1}).getText().split('\n');
                break;
            }
        }

        if (!savedCar) {
            throw new Error('Не найдена машина со списаниями');
        }
    });

    it('Открыть календарь списаний', () => {
        PaymentsCalendar.goTo(`?search=${savedCar}`);
    });

    it('В календаре списаний отображается найденная машина', () => {
        const vehicleTitle = PaymentsCalendar.vehicleTitle.getText();
        // вырезаем лишние пробелы в номере машины, которых нет на странице сводного отчёта
        expect(vehicleTitle.replace(/\s+/g, '')).toContain(savedCar);
    });

});
