import type {OpenPageOptions} from 'tests/e2e/config/commands/open-page';

import {ROUTES} from '@/src/constants/routes';

export async function openChangeAttributesBulkPage(
    ctx: Hermione.TestContext,
    productIdentifiers: number[] | 'all',
    options?: OpenPageOptions
) {
    await ctx.browser.openPage(ROUTES.CLIENT.PRODUCTS, options);
    if (productIdentifiers === 'all') {
        await ctx.browser.clickInto('select-all-checkbox');
    } else {
        for (const productIdentifier of productIdentifiers) {
            await ctx.browser.clickInto([`products-table-row_${productIdentifier}`, 'checkbox']);
        }
    }
    await ctx.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
    await ctx.browser.clickInto('change-attributes-values');
}

export async function openChangeMasterCategoryBulkPage(
    ctx: Hermione.TestContext,
    productIdentifiers: number[] | 'all',
    options?: OpenPageOptions
) {
    await ctx.browser.openPage(ROUTES.CLIENT.PRODUCTS, options);
    if (productIdentifiers === 'all') {
        await ctx.browser.clickInto('select-all-checkbox');
    } else {
        for (const productIdentifier of productIdentifiers) {
            await ctx.browser.clickInto([`products-table-row_${productIdentifier}`, 'checkbox']);
        }
    }
    await ctx.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
    await ctx.browser.clickInto('change-master-category');
}

export async function openChangeFrontCategoryBulkPage(
    ctx: Hermione.TestContext,
    productIdentifiers: number[] | 'all',
    action: 'add' | 'remove',
    options?: OpenPageOptions
) {
    await ctx.browser.openPage(ROUTES.CLIENT.PRODUCTS, options);
    if (productIdentifiers === 'all') {
        await ctx.browser.clickInto('select-all-checkbox');
    } else {
        for (const productIdentifier of productIdentifiers) {
            await ctx.browser.clickInto([`products-table-row_${productIdentifier}`, 'checkbox']);
        }
    }
    await ctx.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
    await ctx.browser.clickInto(`${action}-front-category`);
}

export async function openChangeStatusBulkPage(
    ctx: Hermione.TestContext,
    productIdentifiers: number[] | 'all',
    options?: OpenPageOptions
) {
    await ctx.browser.openPage(ROUTES.CLIENT.PRODUCTS, options);
    if (productIdentifiers === 'all') {
        await ctx.browser.clickInto('select-all-checkbox');
    } else {
        for (const productIdentifier of productIdentifiers) {
            await ctx.browser.clickInto([`products-table-row_${productIdentifier}`, 'checkbox']);
        }
    }
    await ctx.browser.clickInto(['products-bottom-panel', 'bulk-edit'], {waitRender: true, waitNavigation: true});
    await ctx.browser.clickInto('change-status');
}

export async function selectAttribute(ctx: Hermione.TestContext, code: string) {
    await ctx.browser.clickInto('add-attribute', {waitForClickable: true, waitRender: true});
    await ctx.browser.typeInto(['select-user-attributes', 'search'], code, {clear: true});
    await ctx.browser.clickInto(['select-user-attributes', code], {waitRender: true, waitForClickable: true});
    await ctx.browser.clickInto(['select-user-attributes', 'confirm-select']);
}
