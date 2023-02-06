import {
    assertMapAndSidebarWithoutControls,
    assertMapWithoutControls,
    hideHexagons,
    openCreatePointMenu,
    toggleLayersMenuFolder,
    toggleLayersMenuItem,
    toggleWmsZoneGroup
} from 'tests/e2e/utils/common';
import {openPageAndWaitRendered} from 'tests/e2e/utils/map-actions';
import {describe, expect, it} from 'tests/hermione.globals';

import {
    DraftsFolderTestId,
    SidebarMenuGroupTestId,
    SidebarTestId,
    WmsStoresFolderTestId,
    WmsZonesFolderTestId
} from 'types/test-id';

import {managerPointsDomId, managerZonesDomId, wmsStoresDomId} from './fixtures';
import {
    assertSelectedEntitiesByDomId,
    clickIntoManagerZoneButtonAction,
    scrollMenuFolderBlock,
    toggleVisibleElement
} from './utils';

describe('Общие сценарии', function () {
    async function checkMapZoom(ctx: Hermione.TestContext) {
        const mapZoom = new URL(await ctx.browser.getUrl()).searchParams.get('z');
        expect(mapZoom).equal('14');
    }

    it('Перейти к редактированию объекта и кликнуть в зону в сайдбаре', async function () {
        await openPageAndWaitRendered(this);
        await hideHexagons(this);

        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerZonesDomId[0]);
        await clickIntoManagerZoneButtonAction(this, managerZonesDomId[0]);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerZonesDomId[1]);
        await assertMapWithoutControls(this);
    });

    it('Открыть создание объекта через карту и клик в стор в сайдбаре', async function () {
        await openPageAndWaitRendered(this);

        await openCreatePointMenu(this);
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerPointsDomId[0]);
        await assertSelectedEntitiesByDomId(this, managerPointsDomId[0]);
    });

    it('Скрыть сущность и обновить страницу', async function () {
        await openPageAndWaitRendered(this);
        await hideHexagons(this);

        await toggleLayersMenuFolder(this, WmsStoresFolderTestId.ROOT);
        await toggleVisibleElement(this, WmsStoresFolderTestId.ROOT, wmsStoresDomId[0]);
        await this.browser.refresh();

        await toggleLayersMenuFolder(this, WmsStoresFolderTestId.ROOT);
        await assertMapAndSidebarWithoutControls(this);
    });

    it('Папки в сайдбаре занимают все предоставленное место и скроллятся по отдельности', async function () {
        await openPageAndWaitRendered(this);

        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuFolder(this, WmsStoresFolderTestId.ROOT);
        await toggleLayersMenuFolder(this, WmsZonesFolderTestId.ROOT);
        await toggleWmsZoneGroup(this, SidebarMenuGroupTestId.WMS_ZONE_ACTIVE);
        await toggleWmsZoneGroup(this, SidebarMenuGroupTestId.WMS_ZONE_DISABLED);
        await this.browser.assertImage(SidebarTestId.ROOT);

        await scrollMenuFolderBlock(this, DraftsFolderTestId.ROOT);
        await scrollMenuFolderBlock(this, WmsStoresFolderTestId.ROOT);
        await scrollMenuFolderBlock(this, SidebarMenuGroupTestId.WMS_ZONE_ACTIVE);
        await scrollMenuFolderBlock(this, SidebarMenuGroupTestId.WMS_ZONE_DISABLED);
        await this.browser.assertImage(SidebarTestId.ROOT);
    });

    it('Клик на зону в сайдбаре выставляет зум в 14 и центрирует карту по зоне', async function () {
        await openPageAndWaitRendered(this, {z: 15.5, ll: '37.5028285,55.9402815'});

        await assertMapWithoutControls(this);
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerZonesDomId[0]);
        await assertMapWithoutControls(this);
        await checkMapZoom(this);
    });

    it('Клик на большую зону в сайдбаре', async function () {
        await openPageAndWaitRendered(this);

        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerZonesDomId[1]);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, managerZonesDomId[2]);
        await assertMapWithoutControls(this);
    });
});
