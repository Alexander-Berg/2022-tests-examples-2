const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const timeouts = require('../../../../utils/consts/timeouts');
const {nanoid} = require('nanoid');
const {randomNumLength} = require('../../../../utils/number.js');

describe('Создание нового курьера', () => {

    const id = nanoid(7);

    const testData = {
        lastName: 'autotest',
        firstName: `courier test ${id}`,
        middleName: `testovich ${id}`,
        birthday: '01.01.1980',
        workRules: '4Q',
        instantPayments: '10',
        phoneNumber: `+7${randomNumLength(10)}`,
    };

    it('Открыть список водителей', () => {
        DriversPage.goTo();
    });

    it('Нажать "+" в заголовке списка водителей', () => {
        DriversPage.addDriverButton.waitForDisplayed();
        DriversPage.addDriverButton.click();
    });

    it('В форме "Создание профиля" перейти во вкладку "Курьер"', () => {
        const courierTab = $('span=Курьер');
        courierTab.waitForDisplayed();
        courierTab.click();
    });

    it('Заполнить все поля формы любыми случайными данными', () => {
        for (const field in DriverCard.courierForm.fields) {
            DriverCard.courierForm.fields[field].click();

            const value = testData[field].replace(/^\+/, '');

            if (['workRules', 'instantPayments'].includes(field)) {
                DriverCard.selectDropdownItem(value);
            } else {
                DriverCard.courierForm.fields[field].setValue(value);
            }
        }
    });

    it('Нажать кнопку "Сохранить"', () => {
        DriverCard.courierForm.btnSave.click();
        DriverCard.doneAlert.waitForDisplayed();
        DriversPage.getRowInTable().fullName.waitForDisplayed();
    });

    it('Найти созданного курьера в списке водителей', () => {
        DriversPage.goTo(`?search=${testData.phoneNumber}`, {skipWait: true});

        browser.waitUntil(() => {
            try {
                return $(`span=${testData.lastName} ${testData.firstName} ${testData.middleName}`)
                    .waitForDisplayed({timeout: timeouts.waitUntilShort});
            } catch {
                browser.refresh();
                return false;
            }
        }, {
            timeout: timeouts.waitUntil,
            timeoutMsg: `Курьер с телефоном "${testData.phoneNumber}" не найден`,
        });
    });

    it('Перейти в карточку созданного курьера', () => {
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(15_000);
    });

    it('Сравнить данные с данными из шага 3', () => {
        for (const field in testData) {
            if (field in DetailsTab.detailsBlock) {
                expect(DetailsTab.detailsBlock[field]).toHaveValue(testData[field]);
            }

            if (field in DetailsTab.workRulesBlock) {
                expect(DetailsTab.workRulesBlock[field]).toHaveText(testData[field]);
            }

            if (field in DetailsTab.personalDetailsBlock.fields) {
                DetailsTab.personalDetailsBlock.blockButton.click();
                expect(DetailsTab.personalDetailsBlock.fields[field]).toHaveValue(testData[field]);
            }
        }
    });
});
