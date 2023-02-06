import {frontCategories} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {USER_LOGIN} from 'service/seed-db/fixtures';

describe('Просмотр и редактирование фронт-категории', function () {
    it('Просмотр фронт-категории недоступен в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        const path = await this.browser.getPath();
        await this.browser.openPage(path, {region: 'il'});
        await this.browser.assertImage('base-layout');
    });

    it('Шапка страницы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.assertImage('header-panel');
    });

    it('Клик на "Закрыть" уводит на страницу с таблицей категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORIES));
    });

    it('Клик в крошки уводит на страницу с таблицей категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.clickInto('breadcrumb_part_0', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORIES));
    });

    it('Заголовок содержит название, количество товаров, автора и дату создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.assertImage('entity-header-info');
    });

    it('Клик в автора открывает его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.clickInto('entity-header-info_author');
        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.contain(
            encodeURIComponent(`https://staff.yandex-team.ru/${USER_LOGIN}`)
        );

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Поле "Родительская категория" недоступно для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.waitForTestIdSelectorDisabled('parent-category-modal__input');
    });

    it('Поле "Код" недоступно для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.waitForTestIdSelectorDisabled('code');
    });

    it('Изменить значение "Промо"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.clickInto('promo');
        await this.browser.clickInto('submit-button');

        await this.browser.assertImage('base-layout-content');
    });

    it('Изменить значение "Deeplink"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto('deeplink', 'test_deeplink', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('base-layout-content');
    });

    it('Изменить значение поля "Юридические ограничения"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto('legal_restrictions', 'test_legal_restrictions', {clear: true});
        await this.browser.clickInto('submit-button');
        await this.browser.assertImage('base-layout-content');
    });

    it('Изменить название категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'New test name', {clear: true});
        await this.browser.clickInto('submit-button');

        await this.browser.assertImage('base-layout-content');
    });

    it('Шапка страницы в режиме редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'New test name');
        await this.browser.assertImage('header-panel');
    });

    it('Клик в "Отмена" после внесения изменений открывает модал "Отмена изменений"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Temp name');
        await this.browser.clickInto('cancel-button', {waitRender: true});

        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Клик в "Вернуться" в модале "Отмена изменений" возвращает к редактированию категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Temp name');
        await this.browser.clickInto('cancel-button');
        await this.browser.clickInto('confirmation-modal__cancel-button');

        await this.browser.assertImage('base-layout');
    });

    it('Клик в "Да, отменить" в модале "Отмена изменений" возвращает к просмотру категории"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Temp name');
        await this.browser.clickInto('cancel-button', {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitRender: true});

        await this.browser.assertImage('base-layout');
    });

    it('Клик в количество товаров открывает таблицу товаров этой Фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0));
        await this.browser.clickInto(['entity-header-info', 'products-count-link'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
        await this.browser.assertImage(['products-table', 'table-container', '\\tbody']);
    });

    it('Проверки инпута "Порядок сортировки"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        // нельзя ввести ничего кроме чисел
        await this.browser.typeInto('sort-order', '+-test!', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('sort-order-wrapper');
        // проверка на максимальное значение по конкретной сортировке
        await this.browser.typeInto('sort-order', '999', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('sort-order-wrapper');
        // проверка на минимальное значение
        await this.browser.typeInto('sort-order', '0', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('sort-order-wrapper');
        // оставить поле пустым
        await this.browser.typeInto('sort-order', '', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.assertImage('sort-order-wrapper');
    });

    it('Смена порядкового номера через ввод в новое поле', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto('sort-order', '5', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.assertImage('table-body');
    });

    it('Проверка истории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto('sort-order', '5', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorClickable('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Заполнить deeplink допустимыми значениями', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_5_0), {
            patchStyles: {enableNotifications: true}
        });
        await this.browser.typeInto('deeplink', '1abc-_0', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
        await this.browser.assertImage('deeplink-parameter_container');
    });

    it('Нельзя удалить название ФК и сохранить', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(frontCategories.ru.front_category_code_1_0));
        await this.browser.typeInto(['translations', 'name'], '', {clear: true});
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.assertImage('submit-button');
    });
});
