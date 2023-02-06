import createImageFile from 'tests/e2e/utils/create-image-file';
import getFixturePath from 'tests/e2e/utils/fixture';
import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

describe('Создание категорий в витрине', function () {
    it('Общий вид формы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Закрытие формы создания категории крестом', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');

        await this.browser.clickInto(['create-modal', '\\.ant-modal-close'], {waitRender: true});
        await this.browser.waitForTestIdSelectorNotInDom('create-modal');
    });

    it('Нельзя создать категорию с кодом, который уже существует', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {
            patchStyles: {enableNotifications: true}
        });
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'category_code_1_1');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('notification');
        await this.browser.assertImage('notification', {removeShadows: true});
    });

    it('Нельзя создать активную категорию без фото', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['status', 'active']);
    });

    it('Создать неактивную категорию без deeplink с описанием', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.clickInto(['status', 'disabled']);
        await this.browser.typeInto('description', 'test_category_description');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage('base-layout');
    });

    it('Создать активную категорию с deeplink. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.clickInto(['status', 'active']);
        await this.browser.typeInto('deeplink', 'test_category_deeplink');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.assertImage(['catalog-layout_info', 'status']);
        await this.browser.assertImage(['catalog-layout_info', 'deeplink']);
    });

    it('Нельзя создать категорию с deeplink с русскими буквами. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'fr'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.typeInto('deeplink', 'диплинк_русскими_буквами');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage(['create-modal', 'deeplink_container']);
    });

    it('Создание категории с названием на разных языках. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'il'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.clickInto(['translations', 'ru'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-ru'], 'test_category_long_title_ru');
        await this.browser.clickInto(['translations', 'en'], {waitRender: true});
        await this.browser.typeInto(['translations', 'short-title-en'], 'test_category_short_title_en');
        await this.browser.clickInto(['translations', 'he'], {waitRender: true});
        await this.browser.typeInto(['translations', 'long-title-he'], 'test_category_long_title_he');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});

        await this.browser.clickInto(['catalog-layout_info', 'translations', 'ru']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'en']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
        await this.browser.clickInto(['catalog-layout_info', 'translations', 'he']);
        await this.browser.assertImage(['catalog-layout_info', 'translations']);
    });

    it('Смена фото в форме создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img2.png');
        await this.browser.clickInto(['image-with-formats_img1.png', 'delete'], {waitRender: true});
        await this.browser.assertImage(['images-with-formats']);

        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img3.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img3.png');
        await this.browser.assertImage(['images-with-formats']);

        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');
        await this.browser.assertImage(['catalog-layout_info', 'images-with-formats']);
    });

    it('Загрузить запрещенный формат фото в форму создания', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], getFixturePath('sample.gif'));
        await this.browser.assertImage('images-upload');
    });

    it('Смена формата фото при создании категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img1.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img1.png');
        await this.browser.uploadFileInto(['images-upload', 'file-input'], createImageFile('img2.png'));
        await this.browser.waitForTestIdSelectorInDom('image-with-formats_img2.png');
        await this.browser.clickInto(['image-with-formats_img2.png', 'image-format-4'], {waitRender: true});
        await this.browser.clickInto(['image-with-formats_img2.png', 'image-format-6'], {waitRender: true});
        await this.browser.clickInto(['image-with-formats_img2.png', 'image-format-2'], {waitRender: true});
        await this.browser.assertImage(['images-with-formats']);

        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');
        await this.browser.assertImage(['catalog-layout_info', 'images-with-formats']);
    });

    it('Создание категории с валидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.typeInto('meta', '{"number": 123, "string": "abc"}', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.assertImage(['catalog-layout_info', 'meta']);
    });

    it('Создание категории с невалидным полем мета', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.typeInto('meta', '{"number": 123]]]', {clear: true});
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('meta_container');
    });

    it('Смена языка интерфейса в форме создания категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {uiLang: 'en'});
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorDisabled(['create-modal', 'create-modal__ok_button']);
        await this.browser.assertImage('create-modal', {removeShadows: true});
    });

    it('Новые категории не прорастают в другие регионы', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});
        await this.browser.typeInto('code', 'test_category_code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('catalog-layout_info');

        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'), {region: 'fr'});
        await this.browser.typeInto('search', 'test_category_code');
        await this.browser.waitForTestIdSelectorNotInDom('infinite-table_loader');
        await this.browser.waitForTestIdSelectorInDom('empty-placeholder');
    });

    it('Валидация кода при создании категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CATALOG_TAB('categories'));
        await this.browser.clickInto(['action-bar', 'create-button'], {waitRender: true});

        await this.browser.typeInto('code', 'bad::code');
        await this.browser.clickInto(['create-modal', 'create-modal__ok_button'], {waitRender: true});
        await this.browser.waitForTestIdSelectorInDom('create-modal');
        await this.browser.assertImage('code_container');
    });
});
