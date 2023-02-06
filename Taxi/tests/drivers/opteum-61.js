const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const testData = [
    {
        options: ['Перевозка животных'],
    },
    {
        options: ['Перевозка животных', 'WiFi', 'Кондиционер'],
    },
    {
        options: [],
    },
];

const checkDriversOptions = options => {
    if (options.length === 0) {
        return true;
    }

    for (let i = 0; i <= options.length - 1; i++) {
        const driverOptions = $(`div*=${options[i]}`).getText();

        if (driverOptions.includes(options[i])) {
            return true;
        }
    }

    return false;
};

const setOptions = options => {
    if (DriversPage.optionsDropdown.btnClear.isDisplayed()) {
        DriversPage.optionsDropdown.btnClear.click();

        for (let i = 0; i <= options.length - 1; i++) {
            DriversPage.selectDropdownItem(options[i]);
        }
    }

    let optionCard;

    for (let i = 0; i <= options.length - 1; i++) {
        optionCard = $(`span*=${options[i]}`);

        if (!optionCard.isDisplayed()) {
            DriversPage.optionsDropdown.dropdown.click();
            DriversPage.selectDropdownItem(options[i]);
        }
    }

    browser.keys('Escape');
};

describe('Фильтрация водителей по услугам', () => {
    it('61: Открыть страницу водителей ', () => {
        DriversPage.goTo();
    });

    it('Проверить фильтрацию по услугам', () => {
        DriversPage.statusesDropdown.waitForDisplayed({timeout: 5000});

        for (let i = 0; i <= testData.length - 1; i++) {
            setOptions(testData[i].options);
            browser.pause(3000);

            // !FIXME: использовать разные переменные в циклах
            // eslint-disable-next-line no-shadow
            for (let i = 1; i <= 24; i++) {
                if (DriversPage.getRowInTable(i).vehicle.isDisplayed()) {
                    DriversPage.getRowInTable(i).vehicle.isClickable();
                    DriversPage.getRowInTable(i).vehicle.click();
                    browser.pause(250);
                    break;
                }
            }

            assert.isTrue(checkDriversOptions(testData[i].options));
            browser.back();
            DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: 5000});
        }
    });
});
