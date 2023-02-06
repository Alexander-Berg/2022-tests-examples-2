const PaymentRules = require('../../page/transferRequests/PaymentRules');

let checkboxNumber;

const getUncheckedCheckbox = () => {
    const checkboxes = PaymentRules.getCheckboxesColumn();

    for (const [i, checkbox] of checkboxes.entries()) {

        if (!checkbox.getAttribute('checked')) {
            return i;
        }
    }

    return null;
};

describe('Правила выплат: Активация правила', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Найти деактивированную запись правила', () => {
        checkboxNumber = getUncheckedCheckbox();
    });

    it('Деактивировать первую запись правила, если все записи активированы', () => {
        if (checkboxNumber === null) {
            checkboxNumber = 0;

            PaymentRules.getCheckboxesColumn()[checkboxNumber].click();
            PaymentRules.goTo();
        }
    });

    it('Поставить галку у деактивированной записи правила', () => {
        checkboxNumber = getUncheckedCheckbox();
        PaymentRules.getCheckboxesColumn()[checkboxNumber].click();
    });

    it('Обновить страницу', () => {
        PaymentRules.goTo();
    });

    it('правило осталось активированным', () => {
        expect(PaymentRules.getCheckboxesColumn()[checkboxNumber]).toHaveAttribute('checked');
    });
});
