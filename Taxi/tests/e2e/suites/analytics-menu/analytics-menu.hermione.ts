import {
    assertMapWithoutSidebar,
    openCreatePointMenu,
    toggleLayersMenuFolder,
    toggleLayersMenuItem
} from 'tests/e2e/utils/common';
import {clickObjectOnMap, openPageAndWaitRendered} from 'tests/e2e/utils/map-actions';
import {describe, expect, it} from 'tests/hermione.globals';

import {getDomIdFromEntityId} from 'client/lib/dom-id-converter';
import {MapEntity} from 'client/store/entities/types';
import {AnalystEntity} from 'types/analyst';
import {
    CitySelectTestId,
    CreatePointMenuTestId,
    DraftsFolderTestId,
    formatCitySelectOptionTestId,
    formatMapLayersMenuAnalyticsFilterOptionTestId,
    formatNoAnalyticsMenuTestId,
    LayersMenuButtonTestId,
    MapControlPlaneTestId,
    MapLayersMenuAnalyticsTestId,
    MapLayersMenuTestId,
    MapTestId,
    SidebarMenuFolderTestId,
    WmsStoresFolderTestId,
    WmsZonesFolderTestId
} from 'types/test-id';

import {
    assertMapWithoutObjectsAndLegend,
    checkHexagonsForExistence,
    checkHexagonsLegendForExistence,
    openCreateZoneMenu,
    scrollAndAssertAnalyticsMenuFilters,
    switchIntoHexagonsLegend
} from './utils';

describe('Меню аналитики', function () {
    afterEach(async function (this) {
        await this.browser.execute('window.localStorage.clear()');
    });

    it('Клик в X закрывает окно настройки слоев', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuTestId.CLOSE);
        await this.browser.assertImage(LayersMenuButtonTestId.ROOT);
    });

    it('При выключении показа на карте, исчезает аналитический слой, состояние сохраняется', async function () {
        await openPageAndWaitRendered(this, {z: 12});

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
        await assertMapWithoutSidebar(this);
        await checkHexagonsLegendForExistence(this, false);

        await this.browser.refresh();
        await assertMapWithoutSidebar(this);
    });

    it('При включении показа на карте включаются гексы и появляется легенда, состояние сохраняется', async function () {
        await openPageAndWaitRendered(this, {z: 12});

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
        await assertMapWithoutSidebar(this);

        await checkHexagonsForExistence(this);
        await checkHexagonsLegendForExistence(this, true);
        await this.browser.clickIntoEnsured(CitySelectTestId.ROOT);
        await this.browser.clickIntoEnsured(formatCitySelectOptionTestId(2));

        await assertMapWithoutSidebar(this);
    });

    it('Клик в селект открывает список аналитики для выбора, список скроллится', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.FILTERS);
        await scrollAndAssertAnalyticsMenuFilters(this);
    });

    it('Выключение легенды убирает легенду с карты, стейт сохраняется', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await switchIntoHexagonsLegend(this);
        await assertMapWithoutSidebar(this);

        await this.browser.clickIntoEnsured(MapLayersMenuTestId.CLOSE);
        await this.browser.clickIntoEnsured(CitySelectTestId.ROOT);
        await this.browser.clickIntoEnsured(formatCitySelectOptionTestId(2));

        await assertMapWithoutSidebar(this);
    });

    it('Аналитика не исчезает при выключении отображения легенды', async function () {
        await openPageAndWaitRendered(this, {z: 12});

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await switchIntoHexagonsLegend(this);
        await checkHexagonsForExistence(this);

        await this.browser.clickIntoEnsured([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE]);
        await this.browser.clickIntoEnsured([WmsStoresFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE]);
        await this.browser.clickIntoEnsured([WmsZonesFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE]);
        await assertMapWithoutSidebar(this);
    });

    it('Включение другой аналитики не включает показ выключенной легенды', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await switchIntoHexagonsLegend(this);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.FILTERS);
        await this.browser.clickIntoEnsured(
            formatMapLayersMenuAnalyticsFilterOptionTestId(AnalystEntity.SOCDEM_P4P5RES)
        );
        await checkHexagonsLegendForExistence(this, false);

        await assertMapWithoutSidebar(this);
    });

    it('Клик в пустую карту при выключенной аналитике открывает окно создания стора', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
        await openCreatePointMenu(this);
        const createPointMenu = await this.browser.checkForExistenceByTestId(CreatePointMenuTestId.ROOT);
        expect(createPointMenu).equal(true);

        await this.browser.assertImage(CreatePointMenuTestId.MAP_MENU);
    });

    it('Клик в зону при включенном меню слоев не сворачивает это меню и открывает карточку зоны', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Клик в стор в сайдбаре при включенном меню слоев не сворачивает это меню', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1'));
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Клик в черновик зоны в сайдбаре при включенном меню слоев не сворачивает это меню', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await toggleLayersMenuItem(this, DraftsFolderTestId.ROOT, getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '4'));
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Клик в черновик стора на карте не сворачивает меню аналитики и открывает карточку стора', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await clickObjectOnMap(this, MapEntity.POINT_DRAFTS, '9');
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Клик в поиск при включенном меню слоев сворачивает это окно', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.MAP_SEARCH);
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Создание черновика зоны при включенном меню слоев не сворачивает это меню', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await openCreateZoneMenu(this);
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Создание черновика стора при включенном меню слоев не сворачивает это меню', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await openCreatePointMenu(this);
        await assertMapWithoutObjectsAndLegend(this);
    });

    it('Выбор слоя аналитики в селекторе отображает соответствующие гексы и легенду', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.FILTERS);
        await this.browser.clickIntoEnsured(
            formatMapLayersMenuAnalyticsFilterOptionTestId(AnalystEntity.SOCDEM_P4P5RES)
        );
        await assertMapWithoutSidebar(this);

        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.FILTERS);
        await this.browser.clickIntoEnsured(
            formatMapLayersMenuAnalyticsFilterOptionTestId(AnalystEntity.TAXI_ORDERS_COUNT)
        );
        await assertMapWithoutSidebar(this);
    });

    it('Смена слоя аналитики после создания стора меняет выбранный слой в окне гексагонов', async function () {
        await openPageAndWaitRendered(this);

        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await this.browser.clickIntoEnsured(MapLayersMenuAnalyticsTestId.SWITCH);
        await this.browser.clickIntoEnsured(MapTestId.ROOT);
        await this.browser.assertImage(MapLayersMenuTestId.ROOT);
        await this.browser.clickIntoEnsured(formatNoAnalyticsMenuTestId(AnalystEntity.TAXI_ORDERS_COUNT));
        await assertMapWithoutSidebar(this);
    });
});
