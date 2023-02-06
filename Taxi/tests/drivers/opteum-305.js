const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 10_000;

const testData = () => [
    {
        text: 'Работает',
        dropdown: DriversPage.statusesDropdown,
    },
    {
        text: '000 Рога и копыта',
        dropdown: DriversPage.workConditionsDropdown,
    },
    {
        text: 'Комфорт',
        dropdown: DriversPage.categoriesDropdown.dropdown,
    },
    {
        text: 'Кондиционер',
        dropdown: DriversPage.optionsDropdown.dropdown,
    },
    {
        text: 'Свои водители',
        dropdown: DriversPage.driversDropdown,
    },
    {
        text: 'Отсутствует',
        dropdown: DriversPage.kisArtDropdown,
    },
];

let driverNames;

const checkFiltersAndDrivers = () => {
    DriversPage.statusesDropdown.waitForDisplayed({timeout: timeToWaitElem});
    DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: timeToWaitElem});

    for (const {text, dropdown} of testData()) {
        assert.equal(dropdown.getText(), text);
    }

    const refreshDriverNames = $$('tbody tr [class*=name] span').map(el => el.getText());
    assert.deepEqual(driverNames, refreshDriverNames);
};

const setFilter = (dropdown, filter) => {
    dropdown.click();
    browser.pause(250);
    DriversPage.selectDropdownItem(filter);
};

describe('Cохранение выбранных фильтров', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Применить фильтрацию ("Статусы", "Условия работы", "Категории", "Услуги", "Водители")', () => {
        for (const {text, dropdown} of testData()) {
            setFilter(dropdown, text);
            browser.pause(1500);
        }

        driverNames = $$('tbody tr [class*=name] span').map(el => el.getText());
    });

    it('Обновить страницу', () => {
        browser.refresh();
        browser.pause(2000);
        $('span=Работает').waitForDisplayed();
        checkFiltersAndDrivers();
    });

    it('Перейти в другой раздел, например, автомобили', () => {
        browser.url('https://fleet.tst.yandex.ru/vehicles?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru');
        browser.pause(2000);
    });

    it('Вернуться на страницу водителей', () => {
        browser.back();
        DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: timeToWaitElem});
        checkFiltersAndDrivers();
    });
});
