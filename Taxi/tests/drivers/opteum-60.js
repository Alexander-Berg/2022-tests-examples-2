const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const testData = [
    {
        categories: ['Корпоративный'],
    },
    {
        categories: ['Корпоративный', 'Грузовой', 'Старт'],
    },
    {
        categories: ['Грузовой', 'Старт'],
    },
    {
        categories: [],
    },
];

const checkDriversCategories = categories => {
    if (categories.length === 0) {
        return true;
    }

    for (const category of categories) {
        const driverCategories = $(`div*=${category}`).getText();

        if (driverCategories.includes(category)) {
            return true;
        }
    }

    return false;
};

const setCategories = categories => {
    if (DriversPage.categoriesDropdown.btnClear.isDisplayed()) {
        DriversPage.categoriesDropdown.btnClear.click();

        for (const category of categories) {
            const categoryCard = $(`span*=${category}`);

            if (!categoryCard.isDisplayed()) {
                DriversPage.selectDropdownItem(category);
            }
        }
    }

    for (const category of categories) {
        const categoryCard = $(`span*=${category}`);

        if (!categoryCard.isDisplayed()) {
            DriversPage.categoriesDropdown.dropdown.click();
            DriversPage.selectDropdownItem(category);
        }
    }
};

describe('Фильтрация водителей по категориям', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.statusesDropdown.waitForDisplayed({timeout: 5000});
    });

    for (const {categories} of testData) {
        it(`Проверить фильтрацию по категориям "${categories.join()}"`, () => {
            setCategories(categories);
            browser.pause(3000);

            for (let i = 1; i <= 24; i++) {
                if (DriversPage.getRowInTable(i).vehicle.isDisplayed()) {
                    DriversPage.getRowInTable(i).vehicle.isClickable();
                    DriversPage.getRowInTable(i).vehicle.click();
                    browser.pause(250);
                    break;
                }
            }

            assert.isTrue(checkDriversCategories(categories));
            browser.back();
            DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: 5000});
        });
    }
});
