const PaymentRules = require('../../page/transferRequests/PaymentRules');

let checkboxNumber;

const getCheckedCheckbox = () => {
    const checkboxes = PaymentRules.getCheckboxesColumn();

    for (let i = 0; i <= checkboxes.length; i++) {
        if (checkboxes[i].getAttribute('checked')) {
            return i;
        }
    }
};

describe('Правила выплат: Деактивация правила', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Убрать галку у активной записи правила (в колонке "Название")', () => {
        checkboxNumber = getCheckedCheckbox();

        if (checkboxNumber === undefined) {
            checkboxNumber = 0;
            PaymentRules.getCheckboxesColumn()[checkboxNumber].click();
        }

        PaymentRules.getCheckboxesColumn()[checkboxNumber].click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        $('tbody tr').waitForDisplayed();
    });

    it('правило осталось деактивировано', () => {
        expect(PaymentRules.getCheckboxesColumn()[checkboxNumber].getAttribute('checked')).toEqual(null);
    });
});
