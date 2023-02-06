const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const testData = [
    {
        percent: '10',
        rubles: '100',
    },
    {
        percent: '20',
        rubles: '100',
    },
];

const defaultData = {
    percent: '0',
    rubles: '0',
};

const timeToWaitElem = 30_000;

const checkTotal = () => {
    StatementPage.totalTooltip.icon.moveTo();
    StatementPage.totalTooltip.tooltip.waitForDisplayed({timeout: timeToWaitElem});

    const total = Number.parseFloat(StatementPage.total.getText().replace(/s|[^\d,]/g, ''));
    const payment = Number.parseFloat(StatementPage.totalTooltip.paymentText.getText().replace(/s|[^\d,]/g, ''));
    const commission = Number.parseFloat(StatementPage.totalTooltip.commissionText.getText().replace(/s|[^\d,]/g, ''));
    assert.equal(payment + commission, payment + commission, total);
};

const setCommissionInputs = (percent, rubles) => {
    StatementPage.commissionInputs.commission[0].click();
    ListStatementsPage.clearWithBackspace(StatementPage.commissionInputs.commission[0]);
    ListStatementsPage.type(StatementPage.commissionInputs.commission[0], percent);
    StatementPage.commissionInputs.commission[1].click();
    ListStatementsPage.clearWithBackspace(StatementPage.commissionInputs.commission[1]);
    ListStatementsPage.type(StatementPage.commissionInputs.commission[1], rubles);
};

describe('Указание комиссии', () => {
    it('Открыть черновик ведомости', () => {
        const statementNumber = '10';
        const lastStatementInList = $('tbody tr:last-child a');

        ListStatementsPage.goTo();
        ListStatementsPage.type(ListStatementsPage.searchField, statementNumber);
        ListStatementsPage.statusDropdown.click();
        ListStatementsPage.statusDropdownItems.draft.click();

        ListStatementsPage.goThroughPaginations(rows => {
            try {
                for (let i = 1; i <= rows.length - 1; i++) {
                    if (rows[i].getText() === statementNumber) {
                        return true;
                    }
                }
            } catch {
                return false;
            }
        }, 1, 5000);

        lastStatementInList.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
    });

    it('На странице черновика ведомости, справа от суммы "Итого" навести курсор на "?"', () => {
        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (StatementPage.commissionInputs.commission[0].getValue() != '0' || StatementPage.commissionInputs.commission[1].getValue() != '0') {
            setCommissionInputs(defaultData.percent, defaultData.rubles);
            StatementPage.commissionInputs.btnApply.waitForDisplayed({timeout: timeToWaitElem});
            StatementPage.commissionInputs.btnApply.click();
            browser.pause(500);
        }

        checkTotal();
    });

    it('В поле "Вкл. комиссия банка, %" указать 10, В поле "Но не менее (₽)" указать 100', () => {
        setCommissionInputs(testData[0].percent, testData[0].rubles);
    });

    it('Нажать кнопку "Применить"', () => {
        StatementPage.commissionInputs.btnApply.waitForDisplayed({timeout: timeToWaitElem});
        StatementPage.commissionInputs.btnApply.click();
    });

    it('Справа от суммы "Итого" навести курсор на "?"', () => {
        checkTotal();
    });

    it('Изменить комиссию на 20', () => {
        setCommissionInputs(testData[1].percent, testData[1].rubles);
    });

    it('Нажать кнопку "Применить"', () => {
        StatementPage.commissionInputs.btnApply.waitForDisplayed({timeout: timeToWaitElem});
        StatementPage.commissionInputs.btnApply.click();
    });

    it('Справа от суммы "Итого" навести курсор на "?"', () => {
        browser.pause(500);
        checkTotal();
    });

    it('Вернуть дефолтные значения для следующих тестовых прогонов', () => {
        // !FIXME: константа уже есть выше
        // eslint-disable-next-line no-shadow
        const defaultData = {
            percent: '0',
            rubles: '0',
        };

        setCommissionInputs(defaultData.percent, defaultData.rubles);
        StatementPage.commissionInputs.btnApply.waitForDisplayed({timeout: 1000});
        StatementPage.commissionInputs.btnApply.click();
        browser.pause(500);
    });
});
