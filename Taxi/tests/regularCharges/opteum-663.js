const RegularCharges = require('../../page/RegularCharges');

const link = '/regular-charges?limit=40';

const expStatus = {
    new: 'Предложено',
    active: 'Действующее',
    completed: 'Завершено',
    rejected: 'Отклонено',
    termByFleet: 'Прекращено парком',
    termByDriver: 'Прекращено водителем',
};

describe('Периодические списания: фильтрация по Статусу', () => {
    Object.keys(expStatus).forEach((key, i) => {

        describe(expStatus[key], () => {

            it('Открыт раздел "Периодические списания"', () => {
                RegularCharges.open(link);
                RegularCharges.addChargesButton.waitForDisplayed();
            });

            it(`Выбрать статус ${expStatus[key]}`, () => {
                RegularCharges.statusFilter.click();
                RegularCharges.selectList[i].click();
            });

            it(`В таблице отображаются списания ТОЛЬКО со статусом ${expStatus[key]}`, () => {
                browser.pause(1000);

                if (RegularCharges.nothingFound.isExisting()) {
                    expect(RegularCharges.nothingFound).toHaveTextEqual('Пока ничего нет');
                    return;
                }

                RegularCharges.firstChargeInList.waitForDisplayed();

                for (let y = 0; y < RegularCharges.allRows.length; y++) {
                    expect(RegularCharges.getRow(y + 1).status).toHaveTextEqual(expStatus[key]);
                }
            });

        });

    });
});
