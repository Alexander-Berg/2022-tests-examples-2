import {assertMapWithoutMapElements} from 'tests/e2e/utils/common';
import {expect} from 'tests/hermione.globals';

import {HexagonsLegendTestId, MapControlPlaneTestId, MapLayersMenuAnalyticsTestId} from 'types/test-id';

export async function checkHexagonsForExistence(ctx: Hermione.TestContext) {
    const hexagonsSelector = await ctx.browser
        .$('ymaps.ymaps3x0--top-engine-container')
        .$('ymaps.ymaps3x0--tile-layer__container');
    expect(await hexagonsSelector.isExisting()).equal(true);
}

export async function checkHexagonsLegendForExistence(ctx: Hermione.TestContext, hasHexagonsLegend: boolean) {
    const hexagonsLegend = await ctx.browser.checkForExistenceByTestId(HexagonsLegendTestId.ROOT);
    expect(hexagonsLegend).equal(hasHexagonsLegend);
}

export async function switchIntoHexagonsLegend(ctx: Hermione.TestContext) {
    await ctx.browser.clickInto(MapLayersMenuAnalyticsTestId.SWITCH_LEGEND, {waitRender: true});
}

export async function scrollAndAssertAnalyticsMenuFilters(ctx: Hermione.TestContext) {
    await ctx.browser.performScroll(
        [MapLayersMenuAnalyticsTestId.DROPDOWN_MENU, {selector: '.rc-virtual-list-holder'}],
        {
            direction: 'down'
        }
    );
    await ctx.browser.assertImage([MapLayersMenuAnalyticsTestId.DROPDOWN_MENU, {selector: '.rc-virtual-list-holder'}]);
}

export async function assertMapWithoutObjectsAndLegend(ctx: Hermione.TestContext) {
    await ctx.browser.hideBySelector(HexagonsLegendTestId.ROOT);
    await assertMapWithoutMapElements(ctx);
    await ctx.browser.showBySelector(HexagonsLegendTestId.ROOT);
}

export async function openCreateZoneMenu(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapControlPlaneTestId.EDIT_ZONE);

    await ctx.browser.clickIntoEnsured('map', {
        x: 0,
        y: 100
    });
    await ctx.browser.clickIntoEnsured('map', {
        x: 20,
        y: 40
    });
    await ctx.browser.clickIntoEnsured('map', {
        x: 10,
        y: 10
    });
}
