const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

describe('Просмотр и возможность перейти к редактированию правила моментальных выплат', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.getRowInTable().fullName.waitForDisplayed();
    });

    it('проверить графу "Правила выплат"', () => {
        DriversPage.goThroughPaginations(rows => {
            for (let j = 0; j < rows.length - 1; j++) {
                assert.isTrue(rows[j].getText().length > 0);
            }

            return true;
        }, 7, 2000);
    });

    it('нажать на любое правило выплаты', () => {
        const firtsPayments = $('tbody tr td:nth-child(7) a');
        firtsPayments.click();
        const paymentsHeader = 'span=Правила выплат';
        const paymentsEdit = 'span=Редактирование правила';
        const saveButton = 'button[type="submit"]';
        $(`${paymentsHeader}`).waitForDisplayed();
        $(`${paymentsEdit}`).waitForDisplayed();
        $(`${saveButton}`).waitForDisplayed();
    });
});
