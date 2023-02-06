import {masterCategories} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {USER_LOGIN} from 'service/seed-db/fixtures';

describe('Просмотр и редактирование мастер-категории', function () {
    it('Заголовок страницы мастер-категории в режиме просмотра', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.assertImage('header-panel');
    });

    it('Просмотр мастер-категории не доступен в другом регионе', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        const path = await this.browser.getPath();
        await this.browser.openPage(path, {region: 'il'});
        await this.browser.assertImage('base-layout');
    });

    it('Клик в "Закрыть" возвращает к таблице мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORIES));
    });

    it('Шапка страницы мастер-категории в режиме редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.typeInto('name', 'dirty name');

        await this.browser.assertImage('header-panel');
    });

    it('Изменить название мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.typeInto('name', 'some name', {clear: true});

        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.assertImage('entity-header-info-title');
    });

    it('Клик на "Отмена" в режиме редактирования вызывает модал "Отмена изменений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.typeInto('name', 'some name');

        await this.browser.clickInto('cancel-button', {waitRender: true});

        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    it('Смена региона на странице категории открывает таблицу категорий выбранного региона', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));

        await this.browser.clickInto('region-switcher', {waitRender: true});
        await this.browser.clickInto('IL', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp('il' + ROUTES.CLIENT.MASTER_CATEGORIES));
    });

    it('Клик в количество товаров открывает таблицу товаров этой Мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
        await this.browser.assertImage(['products-table', 'table-container', '\\tbody']);
    });

    // eslint-disable-next-line max-len
    it('Клик в количество заполненных товаров открывает таблицу активных заполненных товаров этой Мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('filled-products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    // eslint-disable-next-line max-len
    it('Клик в количество не заполненных товаров открывает таблицу активных незаполненных товаров этой Мастер-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_25_0));
        await this.browser.clickInto('not-filled-products-count-link', {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.assertImage('filter-list');
    });

    it('Клик в хлебные крошки возвращает к таблице мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.clickInto('breadcrumb_part_0', {waitRender: true, waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORIES));
    });

    it('Клик в категорию в хлебных крошках открывает эту категорию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_5_0));
        await this.browser.clickInto('breadcrumb_part_1', {waitRender: true, waitNavigation: true});
        await this.browser.assertImage('entity-header-info');
    });

    it('Инфо о категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.assertImage('entity-header-info');
    });

    it('Клик в автора МК ведет на его стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
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

    it('Поле "Код" недоступно для редактирования', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.waitForTestIdSelectorDisabled('code');
        await this.browser.assertImage('code-parameter_container');
    });

    it('Клик в поле выбора ИМ открывает список ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.assertImage('info-model-select_dropdown-menu');
    });

    it('Проверки инпута "Порядок сортировки"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
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
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.typeInto('sort-order', '5', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.assertImage('table-body');
    });

    it('Проверка истории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.typeInto('sort-order', '5', {clear: true});
        await this.browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorClickable('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Переместить мастер-категорию через карточку этой категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal');
        await this.browser.typeInto('search_input', 'Примером физическими');
        await this.browser.clickInto('row_master_category_code_27_0');
        await this.browser.clickInto('parent-category-modal__ok-button');
        await this.browser.clickInto('submit-button');

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.typeInto('search', 'Примером физическими');
        await this.browser.assertImage('table-body');
    });

    // eslint-disable-next-line max-len
    it('Запись о смене родительской мастер-категории через интерфейс при изменении через карточку мк', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORY(masterCategories.ru.master_category_code_1_0));
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal');
        await this.browser.typeInto('search_input', 'Примером физическими');
        await this.browser.clickInto('row_master_category_code_27_0');
        await this.browser.clickInto('parent-category-modal__ok-button');
        await this.browser.clickInto('submit-button');

        await this.browser.waitForTestIdSelectorClickable('\\#rc-tabs-0-tab-history-of-changes-tab');
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitRender: true});
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });
});
