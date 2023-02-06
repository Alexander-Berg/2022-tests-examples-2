const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

let balance;

describe('Просмотр баланса счета в банке', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('Проверить, что на странице присутствует информация о балансе счёта в банке', () => {
        expect(TransferRequests.balance).toBeDisplayed();
        expect(TransferRequests.balance).toHaveTextMatch(/\d+/g);
    });

    it('Запомнить цифру в балансе', () => {
        balance = TransferRequests.balance.getText();
        balance = balance.slice(0, -2); // убираем символ рубля и лишний пробел
    });

    it('Открыть раздел "Управление счетами"', () => {
        TransferRequests.open('/account-management');
        TransferRequests.getRow(1).waitForDisplayed();
    });

    it('Баланс у активного счёта в разделе "Управление счетами" совпадает с балансом из раздела "Заявки на перевод средств"', () => {
        const checkBoxes = $$('input[type="checkbox"]');
        let checkedNumber;

        for (const [i, checkBox] of checkBoxes.entries()) {

            if (checkBox.getProperty('checked')) {
                checkedNumber = i;
                break;
            }
        }

        if (checkedNumber === undefined) {
            throw new Error('No active bank');
        }

        expect(TransferRequests.getColumn(2)[checkedNumber]).toHaveTextIncludes(balance);
    });
});
