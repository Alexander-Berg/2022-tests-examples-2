import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание прилавков в витрине', function () {
    it('Общий вид формы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Закрытие формы создания прилавка крестом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');

        await this.browser.clickInto(['create-modal', '\\.ant-modal-close'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-modal');
    });

    it('Нельзя создать прилавок с кодом, который уже существует', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'group_code_1_1');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя создать активный прилавок без фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['status', 'active']);
    });

    it('Создать неактивный прилавок с описанием', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.typeInto('description', 'test_group_description');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage('base-layout');
    });

    it('Создать активный прилавок. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img1.png');
        await this.browser.clickInto(['status', 'active']);
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage(['catalog-layout_info', 'status']);
    });

    it('Создание прилавка с названием на разных языках. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.clickInto(['translations', 'ru'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-ru'], 'test_group_long_title_ru');
        await this.browser.clickInto(['translations', 'en'], {waitRender: true});
        await this.browser.typeInto(['translations', 'short-title-en'], 'test_group_short_title_en');
        await this.browser.clickInto(['translations', 'he'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-he'], 'test_group_long_title_he');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.clickInto(['catalog-layout_info', 'translations', 'ru']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'en']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'he']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
    });

    it('Смена фото в форме создания прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img1.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img2.png');
        await this.browser.clickInto(['image_img1.png', 'delete'], {waitRender: true});
        await this.browser.assertImage(['images']);

        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img3.png'));
        await this.browser.waitForTestIdSelectorInDom('image_img3.png');
        await this.browser.assertImage(['images']);

        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');
        await this.browser.assertImage(['catalog-layout_info', 'images']);
    });

    it('Загрузить запрещенный формат фото в форму создания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('images-upload');
    });

    it('Создание прилавка с валидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage(['catalog-layout_info', 'meta']);
    });

    it('Создание прилавка с невалидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('meta_container');
    });

    it('Смена языка интерфейса в форме создания прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {uiLang: 'en'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Новые прилавки не прорастают в другие регионы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_group_code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'), {region: 'fr'});
        await this.browser.typeInto('search', 'test_group_code');
        await this.browser.waitForTestIdSelectorNotInDom('infinite-table_loader');
        await this.browser.waitForTestIdSelectorInDom('empty-placeholder');
    });

    it('Валидация кода при создании прилавка', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('groups'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'bad::code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('code_container');
    });
});
