import {frontCategoriesDeeplinks} from 'tests/e2e/seed-db-map';
import createImageFile from 'tests/e2e/utils/create-image-file';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание фронт-категории', function () {
    it('Общий вид страницы создания, Россия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.assertImage('base-layout');
    });

    it('Шапка страницы создания фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.assertImage('header-panel');
    });

    it('Основные параметры фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.assertImage(['front-category-view', 'base-params'], {removeShadows: true});
    });

    it('Названия и описания, Великобритания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'gb'});
        await this.browser.assertImage(['front-category-view', 'translations'], {removeShadows: true});
    });

    it('Названия и описания, Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'fr'});
        await this.browser.assertImage(['front-category-view', 'translations'], {removeShadows: true});
    });

    it('Названия и описания, Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'il'});
        await this.browser.assertImage(['front-category-view', 'translations'], {removeShadows: true});
    });

    it('Клик в "Отмена" до внесения изменений возвращает к таблице фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(`${ROUTES.CLIENT.FRONT_CATEGORIES}$`));
    });

    it('Клик в "Отмена" после внесения изменений вызывает модал "Отмена изменений"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_front_category_1');
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitRender: true});

        await this.browser.waitForTestIdSelectorInDom('confirmation-modal');
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
    });

    // eslint-disable-next-line max-len
    it('Подтверждение отмены изменений в модале "Отмена изменений" возвращает к таблице фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_front_category_1');
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitRender: true});

        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(`${ROUTES.CLIENT.FRONT_CATEGORIES}$`));
    });

    // eslint-disable-next-line max-len
    it('Клик в "Вернуться" в модале "Отмена изменений" возвращает к форме создания с сохранением внесенных изменений', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        const currentUrl = await this.browser.getUrl();

        await this.browser.typeInto('code', 'test_front_category_1');
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitRender: true});

        await this.browser.clickInto('confirmation-modal__cancel-button', {waitRender: true});
        expect(await this.browser.getUrl()).to.equal(currentUrl);

        await this.browser.assertImage(['base-params', 'code']);
    });

    it('Клик в поле "Родительская категория" открывает модал "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['base-params', 'parent-category-modal__input'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal');
        await this.browser.assertImage('parent-category-modal', {removeShadows: true});
    });

    it('Ввод валидного кода', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'valid_code_666', {blur: true});
        await this.browser.typeInto(['translations', 'ru', 'name'], 'super mega category');
        await this.browser.waitForTestIdSelectorEnabled(['header-panel', 'submit-button']);
        await this.browser.assertImage(['header-panel', 'submit-button']);
    });

    it('Ввод невалидного кода', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', '666_invalid_code', {blur: true});
        await this.browser.typeInto(['translations', 'ru', 'name'], 'super mega category');
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);
        await this.browser.assertImage(['base-params', 'code-parameter_container']);
    });

    it('Создание категории с неуникальным кодом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {patchStyles: {enableNotifications: true}});
        const currentUrl = await this.browser.getUrl();

        await this.browser.typeInto('code', 'front_category_code_1_0', {clear: true});
        await this.browser.typeInto(['translations', 'ru', 'name'], 'super mega category');
        await this.browser.clickInto('submit-button');
        await this.browser.waitForTestIdSelectorInDom('notification');

        expect(await this.browser.getUrl()).to.equal(currentUrl);
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Создание активной фронт-категории в родительской категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);

        await this.browser.typeInto('code', 'test_front_category_1');
        await this.browser.typeInto('deeplink', 'deeplink');
        await this.browser.typeInto('legal_restrictions', '18+, adults only');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.typeInto(['translations', 'ru', 'description'], 'Super mega category description');
        await this.browser.clickInto('promo');

        await this.browser.waitForTestIdSelectorEnabled(['status', 'active']);
        await this.browser.clickInto(['status', 'active_label']);

        // Загрузка фото для категории доступно если создаем категорию внутри рута
        await this.browser.waitForTestIdSelectorInDom('category_image');

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.clickInto(['parent-category-modal__tree-list', 'row_front_category_code_1_0']);
        await this.browser.clickInto('parent-category-modal__ok-button');

        // Загрузка фото для категории не доступно если создаем категорию внутри подкатегории
        await this.browser.waitForTestIdSelectorNotInDom('category_image');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d+')));

        await this.browser.assertImage('base-layout-content');
    });

    it('Создание в рутовой категории неактивной фронт-категории с изображением', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);

        await this.browser.typeInto('code', 'test_front_category_3');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');

        await this.browser.uploadFileInto(
            ['category_image', 'file-input'],
            createImageFile('test_front_category_3.png')
        );

        await this.browser.waitForTestIdSelectorInDom(['category_image', 'thumbnail', 'image'], {timeout: 30_000});

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d+')));
        await this.browser.assertImage('base-layout-content');
    });

    it('Смена языка интерфейса на странице создания фронт-категории (Израиль)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'il', dataLang: 'he', uiLang: 'en'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Создать ФК в корне', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});
        await this.browser.assertImage('tree-table');
    });

    it('Создать дочернюю категорию у родителя, который уже имеет дочек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto(['list-holder', 'fc_row_front_category_code_1_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'create'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('code', 'test_child');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega child category name');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto(['list-holder', 'fc_row_front_category_code_1_0', 'expand_icon'], {
            waitRender: true
        });
        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.assertImage('tree-table');
    });

    it('Создать дочернюю категорию у родителя без дочерних', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega category name');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.clickInto(['list-holder', 'fc_row_test_code', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'create'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('code', 'test_child');
        await this.browser.typeInto(['translations', 'ru', 'name'], 'Super mega child category name');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORIES);
        await this.browser.clickInto('show-inactive', {waitRender: true});
        await this.browser.clickInto(['list-holder', 'fc_row_test_code', 'expand_icon'], {
            waitRender: true
        });
        await this.browser.performScroll(['tree-table', 'list-holder'], {direction: 'down'});
        await this.browser.assertImage('tree-table');
    });

    it('Создать одинаковые deeplink у фронт-категорий с разными родителями', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_front_category_code');

        await this.browser.typeInto(['translations', 'name'], 'qwerty', {clear: true});

        await this.browser.typeInto('deeplink', frontCategoriesDeeplinks.ru.front_category_code_6_0);
        await this.browser.clickInto('submit-button', {waitRender: true, waitNavigation: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.FRONT_CATEGORY('\\d+')));
        await this.browser.assertImage('deeplink-parameter_container');
    });

    it('Нельзя создать одинаковые deeplink у фронт-категорий с общим родителем', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {patchStyles: {enableNotifications: true}});

        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(['parent-category-modal__tree-list', 'row_front_category_code_1_1'], {
            waitForClickable: true
        });
        await this.browser.clickInto('parent-category-modal__ok-button', {waitRender: true});

        await this.browser.typeInto('code', 'test_front_category_code');
        await this.browser.typeInto(['translations', 'name'], 'qwerty', {clear: true});
        await this.browser.typeInto('deeplink', frontCategoriesDeeplinks.ru.front_category_code_6_0);

        await this.browser.clickInto('submit-button', {waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_FRONT_CATEGORY));
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя вводить в deeplink русские буквы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_front_category_code');
        await this.browser.typeInto(['translations', 'name'], 'qwerty', {clear: true});

        await this.browser.typeInto('deeplink', 'йцукен');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('deeplink-parameter_container');
    });

    it('Нельзя создать ФК без названия', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.assertImage('submit-button');
    });

    it('Нельзя создать подкатегорию ФК без названия в одной из локалей (Франция)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY, {region: 'fr'});
        await this.browser.typeInto('code', 'test_code');
        await this.browser.typeInto(['translations', 'en', 'name'], 'Super mega category name');
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.assertImage('submit-button');
    });

    it('Нельзя создать ФК с названием, состоящим из пробела или двух пробелов', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.typeInto('code', 'test_code');

        await this.browser.typeInto(['translations', 'name'], ' ', {clear: true});
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.assertImage('submit-button');

        await this.browser.typeInto(['translations', 'name'], '  ', {clear: true});
        await this.browser.waitForTestIdSelectorDisabled('submit-button');
        await this.browser.assertImage('submit-button');
    });

    // eslint-disable-next-line max-len
    it('Поиск активной фронт-категории по названию при создании фронт-категории через кнопку "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);
        await this.browser.clickInto(['base-params', 'parent-category-modal__input'], {
            waitRender: true
        });
        await this.browser.waitForTestIdSelectorInDom('parent-category-modal');

        const frontCategoryName = 'Как жизни презирает';

        await this.browser.typeInto('search_input', frontCategoryName);

        await this.browser.assertImage(['parent-category-modal__tree-list', 'row_front_category_code_1_0']);
    });
});
