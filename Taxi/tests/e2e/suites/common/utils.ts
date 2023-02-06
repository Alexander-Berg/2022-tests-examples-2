import {
    formatMapMenuRootTestId,
    formatSidebarMenuFolderRootTestId,
    formatSidebarMenuFolderVisibleTestId,
    ManagerZoneViewMenuTestId,
    MapTestId,
    MenuFolderTestId,
    SidebarMenuFolderTestId,
    SidebarMenuGroupTestId,
    SidebarMenuItemsListTestId,
    WmsZoneGroupTestId
} from 'types/test-id';

export async function assertSelectedEntitiesByDomId(ctx: Hermione.TestContext, domId: string) {
    await ctx.browser.assertImage(formatMapMenuRootTestId(domId));
}

export async function toggleWmsZoneGroup(ctx: Hermione.TestContext, group: WmsZoneGroupTestId) {
    await ctx.browser.clickIntoEnsured([group, SidebarMenuGroupTestId.TOGGLE]);
}

export async function toggleLayersMenuFolder(ctx: Hermione.TestContext, folderType: MenuFolderTestId) {
    await ctx.browser.clickIntoEnsured([folderType, SidebarMenuFolderTestId.HEADER]);
}

export async function toggleLayersMenuItem(ctx: Hermione.TestContext, folderType: MenuFolderTestId, domId: string) {
    await ctx.browser.clickIntoEnsured([folderType, formatSidebarMenuFolderRootTestId(domId)]);
}

export async function toggleVisibleElement(ctx: Hermione.TestContext, folderType: MenuFolderTestId, domId: string) {
    await ctx.browser.clickIntoEnsured([folderType, formatSidebarMenuFolderVisibleTestId(domId)]);
}

export async function clickIntoManagerZoneButtonAction(ctx: Hermione.TestContext, domId: string) {
    await ctx.browser.clickIntoEnsured([
        MapTestId.ROOT,
        formatMapMenuRootTestId(domId),
        ManagerZoneViewMenuTestId.BUTTON_ACTION
    ]);
}

export async function scrollMenuFolderBlock(
    ctx: Hermione.TestContext,
    entitiesBlock: MenuFolderTestId | WmsZoneGroupTestId
) {
    await ctx.browser.performScroll([entitiesBlock, SidebarMenuItemsListTestId.ITEMS_LIST], {
        direction: 'down'
    });
}
