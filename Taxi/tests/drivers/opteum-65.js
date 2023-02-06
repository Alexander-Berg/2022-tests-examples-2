const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const testData = {
    status: 'Статус',
    state: 'Состояние',
    codeName: 'Позывной',
    phone: 'Телефон',
    driverTerms: 'Условия работы',
    paymentRules: 'Правила выплат',
    accountBalance: 'Баланс',
    minBalance: 'Лимит',
    driverLicense: 'ВУ',
    vehicle: 'Автомобиль',
    startDate: 'Дата принятия',
    dateFired: 'Дата увольнения',
    notes: 'Прочее',
    kisArtStatus: 'Статус в КИС «АРТ»',
    kisArtId: 'КИС «АРТ» ID',
};

const timeToWaitElem = 5000;

describe('Скрытие и отображение полей в таблице водители', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.getColumnHead('ФИО').waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Проверить, что в списке водителей по умолчанию не отображаются колонки "Дата увольнения" и "Прочее"', () => {
        DriversPage.getColumnHead('Дата увольнения').waitForDisplayed({reverse: true});
        DriversPage.getColumnHead('Прочее').waitForDisplayed({reverse: true});
    });

    it('Открыть управление отображением колонок таблицы', () => {
        DriversPage.editColumns.btnEditColumns.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.editColumns.btnEditColumns.click();
        DriversPage.editColumns.dropdown.btns.status.waitForDisplayed({timeout: timeToWaitElem});

        // у колонок "Дата увольнения" и "Прочее" отсутствует "галка"
        assert.isTrue(!DriversPage.editColumns.dropdown.checkIcons.dateFired.getAttribute('class').includes('checked'));
        assert.isTrue(!DriversPage.editColumns.dropdown.checkIcons.notes.getAttribute('class').includes('checked'));
    });

    it('Скрыть все колонки в списке', () => {
        for (const item in DriversPage.editColumns.dropdown.btns) {
            if (DriversPage.editColumns.dropdown.checkIcons[item].getAttribute('class').includes('checked')) {
                // !FIXME: заиспользовать строгое ===
                // eslint-disable-next-line eqeqeq
                if (item == 'fullName' || item == 'kisArtStatus') {
                    continue;
                }

                DriversPage.selectDropdownItem(testData[item]);
            }
        }

        DriversPage.editColumns.btnEditColumns.click();

        // в списке водителей не отображаются колонки (кроме ФИО и Статус КИС АРТ)
        for (const column in testData) {
            // !FIXME: заиспользовать строгое ===
            // eslint-disable-next-line eqeqeq
            if (column == 'kisArtStatus') {
                continue;
            }

            DriversPage.getColumnHead(testData[column]).waitForDisplayed({reverse: true});
        }
    });

    it('Отобразить все колонки из списка', () => {
        DriversPage.editColumns.btnEditColumns.click();
        DriversPage.editColumns.dropdown.btns.status.waitForDisplayed({timeout: timeToWaitElem});

        for (const item in DriversPage.editColumns.dropdown.btns) {
            if (!DriversPage.editColumns.dropdown.checkIcons[item].getAttribute('class').includes('checked')) {
                DriversPage.selectDropdownItem(testData[item]);
                assert.isTrue(DriversPage.editColumns.dropdown.checkIcons[item].getAttribute('class').includes('checked'));
            }
        }

        DriversPage.editColumns.btnEditColumns.click();

        // в списке водителей отображаются все колонки
        for (const column in testData) {
            DriversPage.getColumnHead(testData[column]).waitForDisplayed();
        }
    });
});
