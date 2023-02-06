import {expect} from 'tests/hermione.globals';

import {FilterName} from 'client/scenes/filters-menu';
import {
    FiltersMenuTestId,
    formatFilterMenuCheckboxTestId,
    formatFilterTypesOptionTestId,
    HexagonsLegendTestId,
    MapControlPlaneTestId,
    MenuToggleIconTestId
} from 'types/test-id';
import type {DeliveryType} from 'types/wms';

interface ExpectedFiltersFromURLParams {
    ctx: Hermione.TestContext;
    zoneDeliveryTypes?: DeliveryType[];
    isPublished?: boolean[];
}

export async function hideMapElements(ctx: Hermione.TestContext) {
    await ctx.browser.hideBySelector(HexagonsLegendTestId.ROOT);
    await ctx.browser.hideBySelector({selector: '.ymaps3x0--top-engine-container'});
    await ctx.browser.clickIntoEnsured(MenuToggleIconTestId.ROOT);
}

export async function showMapElements(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MenuToggleIconTestId.ROOT);
    await ctx.browser.showBySelector({selector: '.ymaps3x0--top-engine-container'});
    await ctx.browser.showBySelector(HexagonsLegendTestId.ROOT);
}

export async function checkingExistenceFiltersMenu(ctx: Hermione.TestContext) {
    const filtersMenu = await ctx.browser.checkForExistenceByTestId(FiltersMenuTestId.ROOT);
    expect(filtersMenu).equal(false);
}

export async function clickIntoDeliveryFilter(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
    await ctx.browser.clickIntoEnsured(FiltersMenuTestId.ADD_FILTER_BTN);
    await ctx.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);
    await ctx.browser.clickIntoEnsured(formatFilterTypesOptionTestId(FilterName.ZONE_DELIVERY_TYPES));
}

export async function clickIntoFilterControlsOption(
    ctx: Hermione.TestContext,
    filterName: FilterName,
    deliveryType: string
) {
    await ctx.browser.clickInto(formatFilterMenuCheckboxTestId(filterName, deliveryType), {
        waitRender: true
    });
}

export async function expectedFiltersFromURL({ctx, zoneDeliveryTypes, isPublished}: ExpectedFiltersFromURLParams) {
    const url = new URL(await ctx.browser.getUrl());

    expect(url.searchParams.get('zoneDeliveryTypes')).equal(zoneDeliveryTypes ? zoneDeliveryTypes.join(',') : null);
    expect(url.searchParams.get('isPublished')).equal(isPublished ? isPublished.join(',') : null);
}
