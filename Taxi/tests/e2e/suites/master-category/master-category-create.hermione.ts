import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание мастер-категории', function () {
    it('Дефолтное состояние формы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage('master-category-view');
    });

    it('Клик в "Отмена" до внесения изменений возвращает к таблице мастер-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto(['header-panel', 'cancel-button'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(`${ROUTES.CLIENT.MASTER_CATEGORIES}$`));
    });

    it('Клик в поле "Родительская категория" открывает модал "Создать категорию"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.assertImage('parent-category-modal', {removeShadows: true});
    });

    it('При вводе валидных данных в поле "Код" активируется кнопка "Создать"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);
        await this.browser.typeInto('code', 'new_mc_code');
        await this.browser.waitForTestIdSelectorEnabled(['header-panel', 'submit-button']);
        await this.browser.assertImage(['header-panel', 'submit-button']);
    });

    it('Валидация поля "Код"', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', '666');
        await this.browser.assertImage(['code-parameter_container']);
        await this.browser.waitForTestIdSelectorDisabled(['header-panel', 'submit-button']);
        await this.browser.assertImage(['header-panel', 'submit-button']);
    });

    it('Клик в поле "Укажите инфомодель" открывает список ИМ', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto('info-model-select', {waitRender: true});
        // В дропдауне есть вертикальный сколлбар, который пропадает спустя некоторое время
        await this.browser.assertImage('info-model-select_dropdown-menu', {screenshotDelay: 2500});
    });

    it('Создание активной рутовой категории с наследуемой инфомоделью', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);

        const code = 'some_code';

        await this.browser.typeInto('code', code);
        await this.browser.typeInto('name', 'some name');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORY('\\d+')));

        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});

        await this.browser.waitForTestIdSelectorInDom(`mc_row_${code}`);
        await this.browser.assertImage('base-layout-content');
    });

    it('Создание неактивной подкатегории с назначенной инфомоделью', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);

        await this.browser.clickInto('disabled_label');

        const parentCode = 'master_category_code_1_0';
        const code = 'some_code';

        await this.browser.clickInto('parent-category-modal__input');
        await this.browser.waitForTestIdSelectorInDom(['parent-category-modal__tree-list', `row_${parentCode}`]);
        await this.browser.clickInto(['parent-category-modal__tree-list', `row_${parentCode}`]);
        await this.browser.clickInto('parent-category-modal__ok-button');

        await this.browser.typeInto('code', code);

        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.clickInto('im_node_compatible_info_model_code_1_1', {waitRender: true});

        await this.browser.typeInto('name', 'some name');

        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORY('\\d+')));
        await this.browser.assertImage('base-layout-content');

        await this.browser.clickInto('close-button', {waitNavigation: true, waitRender: true});

        await this.browser.clickInto([`mc_row_${parentCode}`, 'expand_icon'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom(`mc_row_${code}`);

        await this.browser.assertImage('base-layout-content');
    });

    it('Поиск инфомодели из выпадающего списка по названию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.clickInto('info-model-select', {waitRender: true});
        await this.browser.typeInto(['info-model-select', '\\input'], 'человек');
        await this.browser.assertImage('info-model-select_dropdown-menu');

        await this.browser.typeInto(['info-model-select', '\\input'], '12345');
        await this.browser.assertImage('info-model-select_dropdown-menu');
    });

    it('Отмена в попапе при создании подкатегории в мастер-категории с товаром', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);

        await this.browser.clickInto('parent-category-modal__input', {waitRender: true});
        await this.browser.clickInto(
            ['parent-category-modal__tree-list', 'row_master_category_code_1_0', '\\[class*=switcher]'],
            {waitRender: true}
        );
        await this.browser.clickInto(
            ['parent-category-modal__tree-list', 'row_master_category_code_5_0', '\\[class*=switcher]'],
            {waitRender: true}
        );
        await this.browser.clickInto(['parent-category-modal__tree-list', 'row_master_category_code_25_0', 'title'], {
            waitRender: true
        });

        await this.browser.clickInto('parent-category-modal__ok-button');
        await this.browser.typeInto('code', 'some_code');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.assertImage('confirmation-modal', {removeShadows: true});
        await this.browser.clickInto('confirmation-modal__cancel-button', {waitRender: true});
        await this.browser.assertImage('header');
    });

    it('Создание в мастер-категории с товаром подкатегории с наследуемой инфомоделью', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto(['list-holder', 'mc_row_master_category_code_25_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'create'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitNavigation: true,
            waitRender: true
        });
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.CREATE_MASTER_CATEGORY));

        await this.browser.typeInto('code', 'some_code');
        await this.browser.clickInto('submit-button', {waitRender: true});
        await this.browser.clickInto('confirmation-modal__ok-button', {waitNavigation: true, waitRender: true});
        await this.browser.clickInto(['default_panel', 'close-button'], {waitNavigation: true, waitRender: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.MASTER_CATEGORIES));
        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.assertImage('tree-table');
    });

    it('Смена языка интерфейса на странице создания мастер-категории (Великобритания)', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY, {region: 'gb', dataLang: 'en', uiLang: 'en'});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.clickInto('ui-lang-select', {waitRender: true});
        await this.browser.clickInto(['ui-lang-select_dropdown-menu', 'ru'], {waitRender: true});
        await this.browser.clickInto('account', {waitRender: true});
        await this.browser.assertImage('base-layout');
    });

    it('Создать МК в корне', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.assertImage('tree-table');
    });

    it('Создать дочернюю категорию у родителя, который уже имеет дочек', async function () {
        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto('expand-all', {waitRender: true});
        await this.browser.clickInto(['list-holder', 'mc_row_master_category_code_1_0', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'create'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('code', 'test_child');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['list-holder', 'mc_row_master_category_code_1_0', 'expand_icon'], {
            waitRender: true
        });
        await this.browser.assertImage('tree-table');
    });

    it('Создать дочернюю категорию у родителя без дочерних', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_MASTER_CATEGORY);
        await this.browser.typeInto('code', 'test_code');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);

        await this.browser.clickInto(['list-holder', 'mc_row_test_code', 'category-row-more-button'], {
            waitRender: true
        });
        await this.browser.clickInto(['more-menu', 'create'], {waitRender: true});
        await this.browser.clickInto(['parent-category-modal', 'parent-category-modal__ok-button'], {
            waitNavigation: true,
            waitRender: true
        });
        await this.browser.typeInto('code', 'test_child');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.openPage(ROUTES.CLIENT.MASTER_CATEGORIES);
        await this.browser.clickInto(['list-holder', 'mc_row_test_code', 'expand_icon'], {
            waitRender: true
        });
        await this.browser.assertImage('tree-table');
    });
});
