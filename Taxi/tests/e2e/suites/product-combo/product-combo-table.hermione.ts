import {addDays, format, subDays} from 'date-fns';
import {productCombos} from 'tests/e2e/seed-db-map';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {DbTable} from '@/src/entities/const';
import {SEEDED_CREATED_AT} from 'service/seed-db/fixtures';

describe('Таблица комбинаций', function () {
    const seededAt = subDays(new Date(SEEDED_CREATED_AT), 1);

    it('В поиске комбинаций ничего не найдено', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {queryParams: {search: 'not-exists'}});
        await this.browser.assertImage('product-combo-table');
    });

    it('Скролл таблицы комбинаций', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);

        await this.browser.performScroll(['product-combo-table', 'table-container'], {
            direction: 'down',
            beforeIterationDelay: () => this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner'),
            afterIterationDelay: () => this.browser.waitUntilRendered()
        });

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage(['action-bar', 'pagination-info']);
    });

    it('Поиск комбинаций по названию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.typeInto(['action-bar', 'search'], 'Действительно страдание');
        await this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner');

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage(['action-bar', 'pagination-info']);
    });

    it('Поиск комбинаций по id. Франция', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {region: 'fr'});
        await this.browser.typeInto(['action-bar', 'search'], '40fc5285-9ef7-485b-805f-f76cd90e94b2');
        await this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner');

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage(['action-bar', 'pagination-info']);
    });

    it('Фильтр комбинаций по id', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'uuid'], {waitRender: true});
        await this.browser.typeInto('input_list_for_uuid_0', 'pigeon_combo_b6b0eb6f-c701-4aa2-a830-910f5745f6aa');

        await this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner');
        await this.browser.clickInto(['filter-list', 'filter-item-string']);

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтр комбинаций по статусу', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'status'], {waitRender: true});
        await this.browser.clickInto(['select_option_status', 'disabled'], {waitRender: true});

        await this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner');
        await this.browser.clickInto('header-panel', {waitRender: true});

        await this.browser.assertImage('product-combo-table');
    });

    it('Фильтр комбинаций по дате создания. Израиль', async function () {
        const comboId = productCombos.il['218eaddc-149a-4c0a-91aa-088a5bf94242'];
        const createdAt = subDays(seededAt, 2);
        await this.browser.executeSql(`
            UPDATE ${DbTable.HISTORY_SUBJECT}
            SET created_at = '${createdAt.toISOString()}'
            WHERE id = (SELECT history_subject_id FROM ${DbTable.PRODUCT_COMBO} WHERE id = ${comboId});
        `);
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {
            region: 'il',
            queryParams: {
                filters: {
                    created_at: {rule: 'before-data', values: format(subDays(seededAt, 1), 'dd.MM.yyyy')}
                }
            }
        });

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтр комбинаций по дате обновления', async function () {
        const comboId = productCombos.ru['0dd1fb51-36d9-4788-94bf-bd87d311894c'];
        const updatedAt = addDays(seededAt, 2);
        await this.browser.executeSql(`
            UPDATE ${DbTable.HISTORY_SUBJECT}
            SET updated_at = '${updatedAt.toISOString()}'
            WHERE id = (SELECT history_subject_id FROM ${DbTable.PRODUCT_COMBO} WHERE id = ${comboId});
        `);
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {
            queryParams: {
                filters: {
                    updated_at: {rule: 'after-data', values: format(addDays(seededAt, 1), 'dd.MM.yyyy')}
                }
            }
        });

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтр комбинаций по всем условиям открытие по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {
            queryParams: {
                search: 'Действительно страдание',
                filters: {
                    uuid: {
                        rule: 'equal',
                        values: [
                            'pigeon_combo_2fdbcde6-0101-487c-ba03-d3b3acc197fe',
                            'pigeon_combo_0dd1fb51-36d9-4788-94bf-bd87d311894c'
                        ].join()
                    },
                    status: {
                        values: 'disabled'
                    },
                    meta_products: {
                        rule: 'not-null'
                    },
                    updated_at: {
                        rule: 'equal',
                        values: format(seededAt, 'dd.MM.yyyy')
                    },
                    created_at: {
                        rule: 'equal',
                        values: format(seededAt, 'dd.MM.yyyy')
                    }
                }
            }
        });

        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтр комбинаций по мета-товару', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'meta_products'], {waitRender: true});
        await this.browser.clickInto(['filter-list', 'product-combo-option_10000201'], {
            waitRender: true
        });

        await this.browser.clickInto('header-panel', {waitRender: true});
        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Фильтр комбинаций по товарам-опциям', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.clickInto('add-filter', {waitForClickable: true, waitRender: true});
        await this.browser.clickInto(['filters-menu', 'option_products'], {waitRender: true});
        await this.browser.clickInto(['filter-list', 'product-combo-option_10000001'], {
            waitRender: true
        });
        await this.browser.clickInto(['filter-list', 'product-combo-option_10000002'], {
            waitRender: true
        });

        await this.browser.clickInto('header-panel', {waitRender: true});
        await this.browser.assertImage('product-combo-table');
        await this.browser.assertImage('action-bar');
    });

    it('Общий вид таблицы комбинаций', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.assertImage('base-layout');
    });

    it('Открытие комбинации по клику в таблице комбинаций. Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS, {region: 'il'});
        await this.browser.clickInto('^product-combo-table_row', {waitNavigation: true});
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.PRODUCT_COMBO('\\d')));
    });

    it('Фильтр по типу комбинации', async function () {
        await this.browser.openPage(ROUTES.CLIENT.PRODUCT_COMBOS);
        await this.browser.clickInto('add-filter', {waitRender: true});
        await this.browser.clickInto(['filters-menu', 'type'], {waitRender: true});
        await this.browser.clickInto(['select_option_type', 'recipe'], {waitRender: true});

        await this.browser.waitForTestIdSelectorNotInDom('product-combo-table_spinner');
        await this.browser.clickInto('header-panel', {waitRender: true});

        await this.browser.assertImage('product-combo-table');
    });
});
