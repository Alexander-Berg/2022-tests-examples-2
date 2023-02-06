const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 10_000;

const testData = {
    details: {
        phone: '+70001134561',
        status: 'Работает',
    },
    instantPayouts: '10',
    workRules: {
        workRules: '11111',
        limit: '10',
        dateStart: '15.10.2021',
        checkBoxPlatformOrders: false,
        checkBoxPartnerOrders: true,
        checkBoxCashlessRides: true,
        checkBoxReceipts: true,
    },
    personalDetails: {
        emergencyContact: '+70001134560',
        email: 'test@yandex.ru',
        address: '1',
        driverFeedback: '1',
        birthday: '15.10.2021',
        paymentsID: '395750',
        notes: '1',
    },
    passportDetails: {
        type: 'Национальный паспорт',
        country: 'Азербайджан',
        issuedBy: '1',
        address: '1',
        inn: '1',
        numberAndSeries: '1',
        postIndex: '1',
        dateStart: '14.10.2021',
        dateEnd: '13.10.2021',
        ogrn: '1',
    },
    bankDetails: {
        bic: '1',
        settlementAccount: '1',
        correspondentAccount: '1',
    },
};

const defaultData = {
    details: {
        phone: '+70001134560',
        status: 'Не работает',
    },
    instantPayouts: '1',
    workRules: {
        workRules: '1111',
        limit: '0',
        dateStart: '16.10.2021',
        checkBoxPlatformOrders: true,
        checkBoxPartnerOrders: false,
        checkBoxCashlessRides: false,
        checkBoxReceipts: false,
    },
    personalDetails: {
        emergencyContact: '+70001134561',
        email: 'test1@yandex.ru',
        address: '0',
        driverFeedback: '0',
        birthday: '16.10.2021',
        paymentsID: '395754',
        notes: '0',
    },
    passportDetails: {
        type: 'Международный паспорт',
        country: 'Армения',
        issuedBy: '0',
        address: '0',
        inn: '0',
        numberAndSeries: '0',
        postIndex: '0',
        dateStart: '15.10.2021',
        dateEnd: '16.10.2021',
        ogrn: '0',
    },
    bankDetails: {
        bic: '0',
        settlementAccount: '0',
        correspondentAccount: '0',
    },
};

const driverName = 'opteum-97';

const checkAllChangeFields = data => {
    // details
    assert.equal(DriverCard.phoneNumber.getValue(), data.details.phone);
    assert.equal(DetailsTab.detailsBlock.status.getText(), data.details.status);

    // InstantPayouts
    assert.equal(DetailsTab.instantPayoutsBlock.instantPayouts.dropdown.getText(), data.instantPayouts);

    // WorkRules
    for (const field in DetailsTab.workRulesBlock) {
        if (field.includes('checkBox')) {
            // !FIXME: заиспользовать строгое ===
            // eslint-disable-next-line eqeqeq
            assert.isTrue(DetailsTab.workRulesBlock[field].getProperty('checked') == data.workRules[field]);
            continue;
        }

        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (DetailsTab.workRulesBlock[field].getValue() == undefined) {
            assert.equal(DetailsTab.workRulesBlock[field].getText(), data.workRules[field]);
        } else {
            assert.equal(DetailsTab.workRulesBlock[field].getValue(), data.workRules[field]);
        }
    }

    // PersonalDetails
    DetailsTab.personalDetailsBlock.blockButton.click();

    for (const field in DetailsTab.personalDetailsBlock.fields) {
        assert.equal(DetailsTab.personalDetailsBlock.fields[field].getValue(), data.personalDetails[field]);
    }

    DetailsTab.personalDetailsBlock.blockButton.click();

    // PassportDetails
    DetailsTab.passportDetailsBlock.blockButton.click();

    for (const field in DetailsTab.passportDetailsBlock.fields) {
        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (DetailsTab.passportDetailsBlock.fields[field].getValue() == undefined) {
            assert.equal(DetailsTab.passportDetailsBlock.fields[field].getText(), data.passportDetails[field]);
        } else {
            assert.equal(DetailsTab.passportDetailsBlock.fields[field].getValue(), data.passportDetails[field]);
        }
    }

    DetailsTab.passportDetailsBlock.blockButton.click();

    // BankDetails
    DetailsTab.bankDetailsBlock.blockButton.click();

    for (const field in DetailsTab.bankDetailsBlock.fields) {
        assert.equal(DetailsTab.bankDetailsBlock.fields[field].getValue(), data.bankDetails[field]);
    }

    DetailsTab.bankDetailsBlock.blockButton.click();
};

const fillDetailsBlock = data => {
    DriverCard.phoneNumber.click();
    DriverCard.clearWithBackspace(DriverCard.phoneNumber);
    DriverCard.type(DriverCard.phoneNumber, data.phone);

    DetailsTab.detailsBlock.status.click();
    DriverCard.selectDropdownItem(data.status);
};

const fillInstantPayoutsBlock = data => {
    DetailsTab.instantPayoutsBlock.instantPayouts.dropdown.click();
    DriverCard.selectDropdownItem(data);

    try {
        DetailsTab.instantPayoutsBlock.instantPayouts.modalWindow.window.waitForDisplayed({timeout: 1000});
        DetailsTab.instantPayoutsBlock.instantPayouts.modalWindow.btnYes.click();
    } catch {
        // skip
    }
};

const fillWorkRulesBlock = data => {
    for (const field in DetailsTab.workRulesBlock) {
        if (field.includes('checkBox')) {
            if (DetailsTab.workRulesBlock[field].getProperty('checked') !== data[field]) {
                DetailsTab.workRulesBlock[field].click();
            }

            continue;
        }

        DetailsTab.workRulesBlock[field].click();

        if (field.includes('workRules')) {
            DriverCard.selectDropdownItem(data.workRules);
            continue;
        }

        DriverCard.clearWithBackspace(DetailsTab.workRulesBlock[field]);
        DriverCard.type(DetailsTab.workRulesBlock[field], data[field]);
    }
};

const fillPersonalDetailsBlock = data => {
    DetailsTab.personalDetailsBlock.blockButton.click();

    for (const field in DetailsTab.personalDetailsBlock.fields) {
        DetailsTab.personalDetailsBlock.fields[field].click();
        DriverCard.clearWithBackspace(DetailsTab.personalDetailsBlock.fields[field]);
        DriverCard.type(DetailsTab.personalDetailsBlock.fields[field], data[field]);
    }
};

const fillPassportDetailsBlock = data => {
    DetailsTab.passportDetailsBlock.blockButton.click();

    for (const field in DetailsTab.passportDetailsBlock.fields) {
        DetailsTab.passportDetailsBlock.fields[field].click();

        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (field == 'type' || field == 'country') {
            DriverCard.selectDropdownItem(data[field]);
        } else {
            DriverCard.clearWithBackspace(DetailsTab.passportDetailsBlock.fields[field]);
            DriverCard.type(DetailsTab.passportDetailsBlock.fields[field], data[field]);
        }
    }
};

const fillBankDetailsBlock = data => {
    DetailsTab.bankDetailsBlock.blockButton.click();

    for (const field in DetailsTab.bankDetailsBlock.fields) {
        DetailsTab.bankDetailsBlock.fields[field].click();
        DriverCard.clearWithBackspace(DetailsTab.bankDetailsBlock.fields[field]);
        DriverCard.type(DetailsTab.bankDetailsBlock.fields[field], data[field]);
    }
};

const fillAllBlocks = (data, type = 'Отредактировать') => {
    it(`${type} поля вкладки "Детали": details`, () => {
        fillDetailsBlock(data.details);
    });

    it(`${type} поля вкладки "Детали": instantPayouts`, () => {
        fillInstantPayoutsBlock(data.instantPayouts);
    });

    it(`${type} поля вкладки "Детали": workRules`, () => {
        fillWorkRulesBlock(data.workRules);
    });

    it(`${type} поля вкладки "Детали": personalDetails`, () => {
        fillPersonalDetailsBlock(data.personalDetails);
    });

    it(`${type} поля вкладки "Детали": passportDetails`, () => {
        fillPassportDetailsBlock(data.passportDetails);
    });

    it(`${type} поля вкладки "Детали": bankDetails`, () => {
        fillBankDetailsBlock(data.bankDetails);
    });
};

describe('Редактирование карточки водителя: таб Детали', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it(`Открыть карточку водителя ${driverName}`, () => {
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    fillAllBlocks(testData);

    it('Сохранить изменения', () => {
        DriverCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
        checkAllChangeFields(testData);
    });

    fillAllBlocks(defaultData, 'Вернуть дефолтные');

    it('Сохранить данные', () => {
        DriverCard.saveButton.click();
        browser.pause(2000);
    });
});
