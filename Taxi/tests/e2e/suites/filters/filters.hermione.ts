import {hideHexagons, openCreatePointMenu, toggleLayersMenuFolder, toggleWmsZoneGroup} from 'tests/e2e/utils/common';
import {openPageAndWaitRendered} from 'tests/e2e/utils/map-actions';
import {describe, it} from 'tests/hermione.globals';

import {FilterName} from 'client/scenes/filters-menu';
import {
    DraftsFolderTestId,
    FiltersMenuTestId,
    formatFilterDeleteButtonTestId,
    formatFilterTypesOptionTestId,
    LayersMenuButtonTestId,
    MapControlPlaneTestId,
    MapTestId,
    SidebarMenuGroupTestId,
    WmsZonesFolderTestId
} from 'types/test-id';
import {DeliveryType} from 'types/wms';

import {
    checkingExistenceFiltersMenu,
    clickIntoDeliveryFilter,
    clickIntoFilterControlsOption,
    expectedFiltersFromURL,
    hideMapElements,
    showMapElements
} from './utils';

const FILTERS_FEATURES = {features: 'showStoreRouting,enableFilters'};

describe('Фильтры', function () {
    beforeEach(async function () {
        await openPageAndWaitRendered(this, {...FILTERS_FEATURES, z: '13'}, this.currentTest.uuid);
        await hideMapElements(this);
    });

    afterEach(async function (this) {
        await showMapElements(this);
    });

    it('Иконка фильтра нажимается, отображаются текущие условия если есть активный фильтр', async function () {
        await clickIntoDeliveryFilter(this);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Иконка фильтра нажимается, отображается кнопка "Добавить условие"', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Строка с фильтрами открывается по нажатию на кнопку "Добавить фильтр"', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADD_FILTER_BTN);
        await this.browser.assertImage(MapTestId.ROOT);
    });

    it('Список с возможными фильтрами выпадет по нажатию на строку "Выберите условия"', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADD_FILTER_BTN);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);
        await this.browser.assertImage(MapTestId.ROOT);
    });

    it('Ввод текста в строку – отображаются условия в соответствии с текстом', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADD_FILTER_BTN);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);

        const zoneDeliveryTypes = await this.browser.assertBySelector(
            formatFilterTypesOptionTestId(FilterName.ZONE_DELIVERY_TYPES)
        );
        const innerText = await zoneDeliveryTypes.getText();
        await this.browser.typeInto([FiltersMenuTestId.ROOT, {selector: 'input'}], innerText);
        await this.browser.assertImage(MapTestId.ROOT);
    });

    it('Нажатие на кнопку "Корзина" удаляет условие', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADD_FILTER_BTN);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.DELETE_TYPES_SELECT);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Нельзя нажать "Применить фильтр" если условия не менялись', async function () {
        await clickIntoDeliveryFilter(this);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Фильтр применяется по нажатию на кнопку "Применить фильтр"', async function () {
        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.ROVER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Нельзя нажать "Применить фильтр" если не выбран ни один чекбокс', async function () {
        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.FOOT);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Нажатие на кнопку "Удалить" удаляет условие', async function () {
        await clickIntoDeliveryFilter(this);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
        await this.browser.clickIntoEnsured(formatFilterDeleteButtonTestId(FilterName.ZONE_DELIVERY_TYPES));
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Строка с выбором ещё одного условия появляется по нажатию на кнопку "Ещё условие"', async function () {
        await clickIntoDeliveryFilter(this);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADDITIONAL_FILTER);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Аналитика, Панель расчетов и Поиск перекрывают карточку с фильтром', async function () {
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(LayersMenuButtonTestId.ROOT);
        await checkingExistenceFiltersMenu(this);

        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.MAP_SEARCH);
        await checkingExistenceFiltersMenu(this);

        await this.browser.clickIntoEnsured(MapControlPlaneTestId.FILTERS_MENU);
        await this.browser.clickIntoEnsured(MapControlPlaneTestId.CALCULATIONS_MENU);
        await checkingExistenceFiltersMenu(this);
    });

    it('Создание стора или зоны не перекрывает карточку фильтра', async function () {
        await clickIntoDeliveryFilter(this);
        await openCreatePointMenu(this);
        await this.browser.assertImage(FiltersMenuTestId.ROOT);
    });

    it('Зеленый лейбл у иконки фильтра присутствует если фильтр свернут', async function () {
        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.ROVER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await this.browser.clickIntoEnsured(FiltersMenuTestId.CLOSE);
        await this.browser.assertImage(MapControlPlaneTestId.FILTERS_MENU);
    });

    it('Если одно условие уже выбрано, то по нажатию на "Ещё условие" это условие отсутсвует', async function () {
        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.ROVER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADDITIONAL_FILTER);

        await this.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);
        await this.browser.assertImage(FiltersMenuTestId.ROOT, {
            compositeImage: true
        });
    });

    it('Два вместе выбранных фильтра работают в соответсвии с условиями', async function () {
        await showMapElements(this);
        await hideHexagons(this);

        await toggleLayersMenuFolder(this, WmsZonesFolderTestId.ROOT);
        await toggleWmsZoneGroup(this, SidebarMenuGroupTestId.WMS_ZONE_ACTIVE);
        await toggleWmsZoneGroup(this, SidebarMenuGroupTestId.WMS_ZONE_DISABLED);

        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);

        await this.browser.assertImage(MapTestId.ROOT);

        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.ROVER);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.FOOT);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADDITIONAL_FILTER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);
        await this.browser.clickIntoEnsured(formatFilterTypesOptionTestId(FilterName.IS_PUBLISHED));
        await clickIntoFilterControlsOption(this, FilterName.IS_PUBLISHED, String(true));
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await this.browser.assertImage(MapTestId.ROOT);
    });

    it('После применения фильтра в урл пробрасываются соотв. гет параметры', async function () {
        await clickIntoDeliveryFilter(this);
        await clickIntoFilterControlsOption(this, FilterName.ZONE_DELIVERY_TYPES, DeliveryType.ROVER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await expectedFiltersFromURL({ctx: this, zoneDeliveryTypes: [DeliveryType.FOOT, DeliveryType.ROVER]});

        await this.browser.clickIntoEnsured(FiltersMenuTestId.ADDITIONAL_FILTER);
        await this.browser.clickIntoEnsured(FiltersMenuTestId.FILTER_TYPES);
        await this.browser.clickIntoEnsured(formatFilterTypesOptionTestId(FilterName.IS_PUBLISHED));
        await clickIntoFilterControlsOption(this, FilterName.IS_PUBLISHED, String(false));
        await this.browser.clickIntoEnsured(FiltersMenuTestId.APPLY_FILTER);

        await expectedFiltersFromURL({
            ctx: this,
            zoneDeliveryTypes: [DeliveryType.FOOT, DeliveryType.ROVER],
            isPublished: [true]
        });

        await this.browser.clickIntoEnsured(formatFilterDeleteButtonTestId(FilterName.ZONE_DELIVERY_TYPES));
        await expectedFiltersFromURL({ctx: this, isPublished: [true]});
    });
});
