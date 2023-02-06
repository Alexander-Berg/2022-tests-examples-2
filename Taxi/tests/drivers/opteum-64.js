// !FIXME: использовать brake

const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let rows;

/**
 * @function parseDateToFloat returns date in float format
 * parsed date by:
 * day - parse in format str day to float day * 0.01
 * month - parse in format str month to float month
 * year - parse in format str year to float year
 * result = day + month + year
 * @param {string} date format must be like "1 мая 2021 г." or "21 апр. 2021 г." or "–"
 */
const parseDateToFloat = date => {
    if (date === '–') {
        return 0;
    }

    const months = {
        'янв.': 0,
        'февр.': 1,
        'мар.': 2,
        'апр.': 3,
        'мая': 4,
        'июн.': 5,
        'июл.': 6,
        'авг.': 7,
        'сент.': 8,
        'окт.': 9,
        'нояб.': 10,
        'дек.': 11,
    };

    date = date.slice(-3, 0);

    for (const m in months) {
        if (date.includes(m)) {
            date = date.replace(m, months[m]);
            break;
        }

    }

    let day = 0;
    let month = 0;
    let year = 0;
    let spaceCounter = 0;

    for (const char of date) {
        if (char === ' ') {
            spaceCounter += 1;

            switch (spaceCounter) {
                case 0:
                    day = Number.parseFloat(char) * 0.01;
                    break;
                case 1:
                    month = Number.parseFloat(char);
                    break;
                case 2:
                    year = Number.parseFloat(char);
                    break;
                default:
                    break;
            }

            continue;
        }
    }

    return day + month + year;
};

describe('Сортировка в таблице водители', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('Отсортировать столбец "Позывной" по возрастающей', () => {
        DriversPage.getHeadInTable().codeName.waitForDisplayed({timeout: 5000});
        DriversPage.getHeadInTable().codeName.isClickable();
        DriversPage.getHeadInTable().codeName.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(3);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(rows[i - 1].getText() <= rows[i].getText());
        }
    });

    it('Отсортировать столбец "Позывной" по убывающей', () => {
        DriversPage.getHeadInTable().codeName.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(3);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(rows[i - 1].getText() >= rows[i].getText());
        }

        DriversPage.getHeadInTable().codeName.click();
        browser.pause(2000);
    });

    it('Отсортировать столбец "Баланс" по возрастающей', () => {
        DriversPage.getHeadInTable().accountBalance.isClickable();
        DriversPage.getHeadInTable().accountBalance.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(8);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(Number.parseFloat(rows[i - 1].getText().replace(/\s+/g, '')) <= Number.parseFloat(rows[i].getText().replace(/\s+/g, '')));
        }
    });

    it('Отсортировать столбец "Баланс" по убывающей', () => {
        DriversPage.getHeadInTable().accountBalance.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(8);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(Number.parseFloat(rows[i - 1].getText().replace(/\s+/g, '')) >= Number.parseFloat(rows[i].getText().replace(/\s+/g, '')));
        }

        DriversPage.getHeadInTable().accountBalance.click();
        browser.pause(2000);
    });

    it('Отсортировать столбец "Дата принятия" по возрастающей', () => {
        DriversPage.editColumns.btnEditColumns.click();
        DriversPage.editColumns.dropdown.btns.status.waitForDisplayed();
        DriversPage.selectDropdownItem('Дата принятия');
        DriversPage.editColumns.btnEditColumns.click();

        DriversPage.getHeadInTable().startDate.isClickable();
        DriversPage.getHeadInTable().startDate.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(12);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(parseDateToFloat(rows[i - 1].getText()) <= parseDateToFloat(rows[i].getText()));
        }
    });

    it('Отсортировать столбец "Дата принятия" по убывающей', () => {
        DriversPage.getHeadInTable().startDate.click();
        browser.pause(2000);
        rows = DriversPage.getColumn(12);

        for (let i = 1; i < rows.length - 1; i++) {
            assert.isTrue(parseDateToFloat(rows[i - 1].getText()) >= parseDateToFloat(rows[i].getText()));
        }

        DriversPage.getHeadInTable().startDate.click();
        browser.pause(2000);
    });
});
