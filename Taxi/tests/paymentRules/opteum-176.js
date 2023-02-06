const PaymentRules = require('../../page/transferRequests/PaymentRules');

const testData = {
    name: `autotest-opteum-176-${Math.floor(Math.random() * 9_999_999_999)}`,
    transferFee: '1',
    minFee: '2',
    minRequestAmount: '2',
    maxRequestAmount: '2',
    maxWithdrawalAmount: '2',
    minBalance: '9 999 998',
    checkboxUseByDefault: 'true',
};

describe('Правила выплат: Редактирование правила', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Навести курсор на запись правила', () => {
        PaymentRules.getRow(1).moveTo();
    });

    it('в строке с правилом отображаются две кнопки действия с правилом: добавление водителя и редактирование правила', () => {
        expect(PaymentRules.editButtons[0]).toBeDisplayed();
        expect(PaymentRules.driversButtons[0]).toBeDisplayed();
    });

    it('Нажать кнопку редактирования правила', () => {
        PaymentRules.editButtons[0].click();
    });

    it('открылась форма редактирования правила', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed();
    });

    it('Отредактировать значения правила и сохранить форму', () => {
        PaymentRules.clearSideMenuInputs();
        PaymentRules.fillSideMenuInputs(testData);
        PaymentRules.createSideMenu.btnSave.click();
    });

    it('появился тост "Успешно сохранено"', () => {
        expect(PaymentRules.alert).toHaveTextEqual('Успешно сохранено');
    });

    it('форма редактирования закрылась', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed({reverse: true});
    });

    it('указанные значения сохранились', () => {
        let columnsWithTextCounter = 1;
        const columnsWithText = 7;

        for (const column in testData) {
            if (columnsWithTextCounter <= columnsWithText) {
                break;
            }

            expect(PaymentRules.getColumn(columnsWithTextCounter)[0]).toHaveTextEqual(testData[column]);
            columnsWithTextCounter++;
        }
    });
});
