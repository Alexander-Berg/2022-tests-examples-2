const RegularCharges = require('../../page/RegularCharges');

describe('Периодическое списание: Прекратить списание', () => {

    const cancelCount = 5;

    for (let suite = 1; suite <= cancelCount; suite++) {
        describe(`Списание #${suite}`, () => {

            let id;

            it('Открыть раздел "Периодические списания"', () => {
                RegularCharges.goTo('?limit=40&states=accepted');
            });

            it('Найти любое Действующее списание и прекратить его', () => {
                for (let i = 0; i < RegularCharges.allRows.length; i++) {
                    const row = RegularCharges.getRow(i + 1);

                    if (row.status.getText() === 'Действующее') {
                        id = row.id.getText();
                        return RegularCharges.deleteChargesFromList(i);
                    }
                }

                throw new Error('Не найдено подходящих списаний');
            });

            it('Открыть прекращенное списание', () => {
                RegularCharges.goTo(`/${id}`, {skipWait: true});
                expect(RegularCharges.chargeCardRedText).toHaveTextStartsWith('Прекращено парком:');
            });

        });
    }
});
