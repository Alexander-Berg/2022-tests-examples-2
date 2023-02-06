const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const timeToWaitElem = 50_000;

let driverInfo,
    total;

const checkTotal = () => {
    if (StatementPage.total.getText().includes(',')) {
        assert.equal(
            Number.parseInt(
                StatementPage.total
                    .getText().slice(0, Math.max(0, StatementPage.total.getText().indexOf(',') - 1))
                    .replace(/\s+/g, '')
                    .replace(/[^\d+]/g, ''),
            ),
            total - Number.parseInt(driverInfo.payment.toString().slice(0, Math.max(0, driverInfo.payment.toString().length - 1))),
        );
    } else {
        assert.equal(
            Number.parseInt(
                StatementPage.total
                    .getText()
                    .replace(/\s+/g, '')
                    .replace(/[^\d+]/g, ''),
            ),
            total - driverInfo.payment,
        );
    }
};

describe('Удаление водителя из списка в ведомости', () => {
    it('Открыть ведомость с водителями в статусе "Черновик"', () => {
        ListStatementsPage.open('/financial-statements/1b51aa36-59cc-438a-8349-8a77ab137905');
        StatementPage.waitingLoadThisPage(timeToWaitElem);
    });

    it('Запомнить данные о редактируемом водителе и значение "Итого"', () => {
        driverInfo = StatementPage.mapSelectorsToText(StatementPage.getRowInTable(1));

        driverInfo.payment = driverInfo.payment.includes(',')
            ? Number.parseInt(driverInfo.payment.slice(0, Math.max(0, driverInfo.payment.indexOf(','))).replace(/\s+/g, ''))
            : Number.parseInt(driverInfo.payment.replace(/\s+/g, ''));

        total = StatementPage.total.getText().includes(',')
            ? Number.parseInt(StatementPage.total
                .getText().slice(0, Math.max(0, StatementPage.total.getText().indexOf(',') - 1))
                .replace(/[^\d+]/g, ''))
            : Number.parseInt(StatementPage.total.getText().replace(/[^\d+]/g, ''));
    });

    it('Нажать на кнопку удаления в строке любого водителя', () => {
        StatementPage.getRowBtns(1).btnRemoveSpan.moveTo();
        StatementPage.getRowBtns(1).btnRemove.click();

        StatementPage.removeWindow.modalWindow.waitForDisplayed({timeout: timeToWaitElem});

        assert.equal(StatementPage.removeWindow.driverInput.getValue(), driverInfo.name);
        assert.isTrue(!StatementPage.removeWindow.driverInput.isClickable());
    });

    it('Нажать на кнопку "Удалить"', () => {
        StatementPage.removeWindow.btnRemove.click();

        assert.isTrue(StatementPage.removeWindow.modalWindow.waitForDisplayed({reverse: true}));
        StatementPage.removeWindow.tostUpdateStatement.waitForDisplayed({timeout: timeToWaitElem});
        StatementPage.waitingLoadThisPage(timeToWaitElem);

        $(`span=*${driverInfo.name}`).waitForDisplayed({reverse: true});
        checkTotal();
    });

    it('Обновить страницу, проверить, что данные совпадают с данными из предыдущего шага', () => {
        browser.refresh();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
        checkTotal();
    });
});
