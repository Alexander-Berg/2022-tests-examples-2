import crypto from 'crypto';
import createImageFile from 'tests/e2e/utils/create-image-file';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';

const FRONT_CATEGORY_ID = 87;
const ROOT_FRONT_CATEGORY_ID = 5;
const FRONT_CATEGORY_ID_IN_IL_REGION = 65;

describe('История изменений фронт-категории', function () {
    async function assertListItemImageStretched(ctx: Hermione.TestContext, selector: string) {
        const initialSize = await ctx.browser.getWindowSize();
        const container = await ctx.browser.findByTestId('history-of-changes_list');

        await container.execute(
            (container, selector) => {
                if (container instanceof HTMLElement) {
                    container.style.removeProperty('height');

                    [...container.querySelectorAll('[data-testid^=list-item')]
                        .filter((it): it is HTMLElement => it instanceof HTMLElement)
                        .filter((it) => it.dataset.testid !== selector)
                        .forEach((it) => it.style.setProperty('display', 'none', 'important'));
                }
            },
            container,
            selector
        );

        await ctx.browser.setWindowSize(initialSize.width, 1500);
        await ctx.browser.assertImage(['history-of-changes_list', selector]);
        await ctx.browser.setWindowSize(initialSize.width, initialSize.height);
    }

    it('Запись о создании пустой фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.CREATE_FRONT_CATEGORY);

        await this.browser.typeInto('code', 'some_front_category_code', {clear: true});
        await this.browser.typeInto(['translations', 'ru', 'name'], 'My front-category');
        await this.browser.clickInto('submit-button', {waitNavigation: true, waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await assertListItemImageStretched(this, 'list-item-2');
    });

    it('Запись о замене названия фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(FRONT_CATEGORY_ID));

        await this.browser.typeInto(['translations', 'ru', 'name'], 'Renamed front-category', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись об удалении описания на английском фронт-категории. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(FRONT_CATEGORY_ID_IN_IL_REGION), {region: 'il'});

        await this.browser.typeInto(['translations', 'en', 'description'], '', {clear: true});
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Запись о смене статуса фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(FRONT_CATEGORY_ID));

        await this.browser.clickInto('disabled_label');
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Поиск по истории изменений фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(FRONT_CATEGORY_ID));

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});
        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.typeInto('history-of-changes_search', 'истин');

        await this.browser.assertImage('query-state-spinner');
    });

    it('Запись о смене всех полей фронт-категорий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(ROOT_FRONT_CATEGORY_ID));

        await this.browser.typeInto('sort-order', '2', {clear: true});
        await this.browser.clickInto('promo');
        await this.browser.typeInto('deeplink', 'new_deeplink', {clear: true});
        await this.browser.typeInto('legal_restrictions', 'New Legal Restrictions', {clear: true});
        await this.browser.clickInto('delete-image');
        await this.browser.uploadFileInto(
            ['category_image', 'file-input'],
            createImageFile('new_front_category_image.png')
        );
        await this.browser.clickInto('submit-button', {waitRender: true});

        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {waitForClickable: true});

        await this.browser.waitForTestIdSelectorInDom(['history-of-changes_list', '^list-item']);
        await this.browser.assertImage(['history-of-changes_list', 'list-item-2']);
    });

    it('Скачивание изображения из истории фронт-категории', async function () {
        await this.browser.openPage(ROUTES.CLIENT.FRONT_CATEGORY(ROOT_FRONT_CATEGORY_ID));
        await this.browser.clickInto('\\#rc-tabs-0-tab-history-of-changes-tab', {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto(['download-image'], {waitRender: true});
        const file = await this.browser.getDownloadedFile('front_category_code_1_0.png', {purge: true});

        const hash = crypto.createHash('md5').update(file);
        expect(hash.digest('hex')).to.matchSnapshot(this);
    });
});
