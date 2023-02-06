const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const timeToWaitElem = 30_000;
const deltaPayment = 100;
let driverInfo, total;

const checkPayment = () => {
    assert.equal(Number.parseInt(StatementPage.getRowInTable(1).payment.getText().slice(0, Math.max(0, StatementPage.getRowInTable(1).payment.getText().indexOf(','))).replace(/\s+/g, '')), driverInfo.payment + deltaPayment);
};

const checkTotal = () => {
    if (StatementPage.total.getText().includes(',')) {
        assert.equal(
            Number.parseInt(
                StatementPage.total
                    .getText().slice(0, Math.max(0, StatementPage.total.getText().indexOf(',')))
                    .replace(/\s+/g, '')
                    .replace(/[^\d+]/g, ''),
            ),
            total + deltaPayment,
        );
    } else {
        assert.equal(
            Number.parseInt(
                StatementPage.total
                    .getText()
                    .replace(/\s+/g, '')
                    .replace(/[^\d+]/g, ''),
            ),
            total + deltaPayment,
        );
    }
};

const checkMoney = () => {
    checkPayment();
    checkTotal;
};

describe('Редактирование суммы к выплате у конкретного водителя в конкретной ведомости', () => {
    it('Перейти в ведомость со статусом "Черновик"', () => {
        ListStatementsPage.goTo(true, true, '/fce94468-7c14-4cd4-98f6-be695189d166');
        StatementPage.waitingLoadThisPage(timeToWaitElem);
    });

    it('Запомнить данные о редактируемом водителе и значение "Итого"', () => {
        driverInfo = StatementPage.mapSelectorsToText(StatementPage.getRowInTable(1));

        driverInfo.payment = driverInfo.payment.includes(',')
            ? Number.parseInt(driverInfo.payment.slice(0, Math.max(0, driverInfo.payment.indexOf(','))).replace(/\s+/g, ''))
            : Number.parseInt(driverInfo.payment.replace(/\s+/g, ''));

        total = StatementPage.total.getText().includes(',')
            ? Number.parseInt(StatementPage.total
                .getText().slice(0, Math.max(0, StatementPage.total.getText().indexOf(',')))
                .replace(/[^\d+]/g, ''))
            : Number.parseInt(StatementPage.total.getText().replace(/[^\d+]/g, ''));
    });

    it('Нажать на кнопку редактирования в строке любого водителя', () => {
        StatementPage.getRowBtns(1).btnEdit.moveTo();
        StatementPage.getRowBtns(1).btnEdit.click();
        StatementPage.editWindow.modalWindow.waitForDisplayed({timeout: timeToWaitElem});
        assert.equal(StatementPage.editWindow.driverInput.getValue(), driverInfo.name);
        assert.equal(Number.parseInt(StatementPage.editWindow.paymentInput.getValue()), driverInfo.payment);
        assert.isTrue(!StatementPage.editWindow.driverInput.isClickable());
    });

    it('Изменить сумму в поле "К выплате" на любую валидную', () => {
        StatementPage.editWindow.paymentInput.click();
        StatementPage.clearWithBackspace(StatementPage.editWindow.paymentInput);
        StatementPage.type(StatementPage.editWindow.paymentInput, (driverInfo.payment + deltaPayment).toString());
    });

    it('Нажать на кнопку "Сохранить"', () => {
        StatementPage.editWindow.btnSave.click();

        assert.isTrue(StatementPage.editWindow.modalWindow.waitForDisplayed({reverse: true}));
        StatementPage.editWindow.tostUpdateStatement.waitForDisplayed({timeout: timeToWaitElem});
        StatementPage.waitingLoadThisPage(25_000);
        checkMoney();
    });

    it('Обновить страницу, проверить, что данные совпадают с данными из предыдущего шага', () => {
        browser.refresh();
        StatementPage.waitingLoadThisPage(25_000);
        checkMoney();
    });
});
