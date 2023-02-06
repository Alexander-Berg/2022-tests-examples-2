import {
    formatSidebarMenuFolderRootTestId,
    HexagonsLegendTestId,
    LayersMenuButtonTestId,
    MapControlPlaneTestId,
    MapControlsTestId,
    MapLayersMenuAnalyticsTestId,
    MapLayersMenuTestId,
    MapTestId,
    MenuFolderTestId,
    MenuToggleIconTestId,
    SidebarMenuFolderTestId,
    SidebarMenuGroupTestId,
    SidebarTestId,
    WmsZoneGroupTestId
} from 'types/test-id';

export async function openCreatePointMenu(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapControlPlaneTestId.EDIT_POINT);
    await ctx.browser.clickIntoEnsured(MapTestId.ROOT);
}

export async function toggleLayersMenuFolder(ctx: Hermione.TestContext, folderType: MenuFolderTestId) {
    await ctx.browser.clickIntoEnsured([folderType, SidebarMenuFolderTestId.HEADER]);
}

export async function toggleWmsZoneGroup(ctx: Hermione.TestContext, group: WmsZoneGroupTestId) {
    await ctx.browser.clickIntoEnsured([group, SidebarMenuGroupTestId.TOGGLE]);
}

export async function toggleLayersMenuItem(ctx: Hermione.TestContext, folderType: MenuFolderTestId, domId: string) {
    await ctx.browser.clickIntoEnsured([folderType, formatSidebarMenuFolderRootTestId(domId)]);
}

export async function assertMapWithoutSidebar(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MenuToggleIconTestId.ROOT);
    await ctx.browser.assertImage(MapTestId.ROOT);
    await ctx.browser.clickIntoEnsured(MenuToggleIconTestId.ROOT);
}

export async function hideHexagons(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
    await ctx.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
    await ctx.browser.clickIntoEnsured(MapLayersMenuTestId.CLOSE);
}

export async function assertMapAndSidebarWithoutControls(ctx: Hermione.TestContext) {
    await ctx.browser.hideBySelector(MapControlPlaneTestId.ROOT);
    await ctx.browser.hideBySelector(MapControlsTestId.ROOT);
    await ctx.browser.hideBySelector(HexagonsLegendTestId.ROOT);
    await ctx.browser.assertImage(MapTestId.ROOT);
    await ctx.browser.showBySelector(MapControlPlaneTestId.ROOT);
    await ctx.browser.showBySelector(MapControlsTestId.ROOT);
    await ctx.browser.showBySelector(HexagonsLegendTestId.ROOT);
}

export async function assertMapWithoutControls(ctx: Hermione.TestContext) {
    await ctx.browser.hideBySelector(SidebarTestId.ROOT);
    await ctx.browser.hideBySelector(MapControlPlaneTestId.ROOT);
    await ctx.browser.hideBySelector(MapControlsTestId.ROOT);
    await ctx.browser.hideBySelector(HexagonsLegendTestId.ROOT);
    await ctx.browser.assertImage(MapTestId.ROOT);
    await ctx.browser.showBySelector(SidebarTestId.ROOT);
    await ctx.browser.showBySelector(MapControlPlaneTestId.ROOT);
    await ctx.browser.showBySelector(MapControlsTestId.ROOT);
    await ctx.browser.showBySelector(HexagonsLegendTestId.ROOT);
}

export async function assertMapWithoutMapElements(ctx: Hermione.TestContext) {
    await ctx.browser.hideBySelector({selector: '.ymaps3x0--top-engine-container'});
    await assertMapWithoutSidebar(ctx);
    await ctx.browser.showBySelector({selector: '.ymaps3x0--top-engine-container'});
}
