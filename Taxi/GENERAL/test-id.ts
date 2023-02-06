import type {FilterName} from 'client/scenes/filters-menu';

import type {AnalystEntity} from './analyst';

export enum AnalyticsTooltipTestId {
    ROOT = 'analytics-tooltip',
    CONTENT = 'analytics-tooltip__content',
    ICON = 'analytics-tooltip__icon'
}

export enum MapMenuAnalyticTestId {
    ROOT = 'map-menu-analytic',
    PANEL_HEADER = 'map-menu-analytic__panel-header',
    PANEL_HEADER_AUDIENCE = 'map-menu-analytic__panel-header_audience',
    PANEL_HEADER_TAXI = 'map-menu-analytic__panel-header_taxi',
    PANEL_HEADER_LAVKA = 'map-menu-analytic__panel-header_lavka',
    PANEL_HEADER_EDA = 'map-menu-analytic__panel-header_eda',
    ITEM_VALUE = 'map-menu-analytic__item-value',
    ITEM_VALUE_TARGET_AUDIENCE = 'map-menu-analytic__item-value_target-audience',
    ITEM_VALUE_TOTAL_AUDIENCE = 'map-menu-analytic__item-value_total-audience',
    ITEM_VALUE_COST_ON_METER = 'map-menu-analytic__item-value_cost-on-meter',
    ITEM_VALUE_TAXI_ORDERS = 'map-menu-analytic__item-value_taxi-orders',
    ITEM_VALUE_TAXI_AVERAGE_RECEIPT = 'map-menu-analytic__item-value_taxi-average-receipt',
    ITEM_VALUE_DELI_ORDERS = 'map-menu-analytic__item-value_deli-orders',
    ITEM_VALUE_DELI_AVERAGE_RECEIPT = 'map-menu-analytic__item-value_deli-average-receipt',
    ITEM_VALUE_MEAL_ORDERS = 'map-menu-analytic__item-value_meal-orders',
    ITEM_VALUE_MEAL_AVERAGE_RECEIPT = 'map-menu-analytic__item-value_meal-average-receipt',
    ITEM_VALUE_LAVKA_AVERAGE_CTE = 'map-menu-analytic__item-value_lavka-average-cte',
    ITEM_VALUE_SERVED_AUDIENCE = 'map-menu-analytic__item-value_served-audience'
}

export enum MapControlPlaneTestId {
    ROOT = 'map-control-plane',
    MAP_SEARCH = 'map-control-plane__map-search',
    EDIT_ZONE = 'map-control-plane__edit-zone',
    EDIT_POINT = 'map-control-plane__edit-point',
    FILTERS_MENU = 'map-control-plane__filters-menu',
    CALCULATIONS_MENU = 'map-control-plane__calculations-menu'
}

export enum MapSearchTestId {
    ROOT = 'map-search',
    SELECT = 'map-search__select',
    SEARCH_BUTTON = 'map-search__search-button',
    CLOSE_BUTTON = 'map-search__close-button'
}

export enum MapTestId {
    ROOT = 'map'
}

export enum MenuToggleIconTestId {
    ROOT = 'menu-toggle-icon'
}

export enum MapControlsTestId {
    ROOT = 'map-controls'
}

export enum HexagonsLegendTestId {
    ROOT = 'hexagons-legend'
}

export enum SidebarTestId {
    ROOT = 'sidebar'
}

export enum LogoTestId {
    ROOT = 'logo'
}

export enum SidebarMenuFolderTestId {
    ROOT = 'sidebar-menu-folder',
    HEADER = 'sidebar-menu-folder__header',
    VISIBLE = 'sidebar-menu-folder__visible'
}

export enum SidebarMenuGroupTestId {
    ROOT = 'sidebar-menu-group',
    TOGGLE = 'sidebar-menu-group__toggle',
    WMS_ZONE_ACTIVE = 'sidebar-menu-group_wms_zone_active',
    WMS_ZONE_DISABLED = 'sidebar-menu-group_wms_zone_disabled'
}

export enum MapMenuTestId {
    ROOT = 'map-menu',
    CLOSE = 'map-menu__close'
}

export enum ManagerZoneViewMenuTestId {
    ROOT = 'manager-zone-view-menu',
    BUTTON_ACTION = 'manager-zone-view-menu__button-action'
}

export enum SidebarMenuItemsListTestId {
    ROOT = 'sidebar-menu-items-list',
    ITEMS_LIST = 'sidebar-menu-items-list__items-list'
}

export enum DraftsFolderTestId {
    ROOT = 'drafts-folder'
}

export enum WmsStoresFolderTestId {
    ROOT = 'wms-stores-folder'
}

export enum WmsZonesFolderTestId {
    ROOT = 'wms-zones-folder'
}

export enum SidebarMenuTestId {
    ROOT = 'sidebar-menu'
}

export enum ExportIconTestId {
    ROOT = 'export-icon'
}

export enum ExportMenuTestId {
    ROOT = 'export-menu',
    ITEM_GEO_JSON = 'export-menu__item_geo-json',
    ITEM_ANALYTICS = 'export-menu__item_analytics'
}

export enum ManagerZoneEditorTestId {
    ROOT = 'manager-zone-editor',
    MAP_POINT = 'manager-zone-editor__map-point'
}

export enum ManagerZoneEditMenuTestId {
    ROOT = 'manager-zone-edit-menu',
    BUTTON_ACTION = 'manager-zone-edit-menu__button-action'
}

export enum CreatePointMenuTestId {
    ROOT = 'create-point-menu',
    MAP_MENU = 'create-point-menu__map-menu',
    ACTION_SAVE = 'create-point-menu__action_save'
}

export enum EditPointMenuTestId {
    ROOT = 'edit-point-menu',
    EDIT_BTN = 'edit-point-menu__edit-btn'
}

export enum FiltersMenuTestId {
    ROOT = 'filters-menu',
    CLOSE = 'filters-menu__close',
    ADD_FILTER_BTN = 'filters-menu__add-filter-btn',
    DELETE_TYPES_SELECT = 'filters-menu__delete-types-select',
    APPLY_FILTER = 'filters-menu__apply-filter',
    DELETE_FILTER = 'filters-menu__delete-filter',
    ADDITIONAL_FILTER = 'filters-menu__additional-filter',
    FILTER_TYPES = 'filters-menu__filter-types',
    FILTER_TYPES_OPTIONS = 'filters-menu__filter-types-options'
}

export enum InputTestId {
    ROOT = 'input'
}

export enum TextAreaTestId {
    ROOT = 'textarea'
}

export enum StartrekTicketTestId {
    ROOT = 'startrek-ticket'
}

export enum AuthorInfoTestId {
    ROOT = 'author-info',
    LINK = 'author-info__link'
}

export enum DraftsDescriptionTestId {
    ROOT = 'drafts-description',
    TEXT_EXPAND = 'drafts-description__text-expand'
}

export enum LayersMenuButtonTestId {
    ROOT = 'layers-menu-button'
}

export enum MapLayersMenuTestId {
    ROOT = 'map-layers-menu',
    CLOSE = 'map-layers-menu__close'
}

export enum MapLayersMenuAnalyticsTestId {
    ROOT = 'map-layers-menu-analytics',
    SWITCH = 'map-layers-menu-analytics__switch',
    SWITCH_LEGEND = 'map-layers-menu-analytics__switch-legend',
    FILTERS = 'map-layers-menu-analytics__filters',
    DROPDOWN_MENU = 'map-layers-menu-analytics__filters-dropdown-menu'
}

export enum NoAnalyticsMenuTestId {
    ROOT = 'no-analytics-menu'
}

export enum RegionSelectTestId {
    ROOT = 'region-select',
    OPTION = 'region-select__option'
}

export enum CitySelectTestId {
    ROOT = 'city-select',
    OPTION = 'city-select__option'
}

export enum BaseLayoutTestId {
    ROOT = 'base-layout',
    CONTENT = 'base-layout__content'
}

export enum NotificationTestId {
    ROOT = 'notification'
}

export enum MenuInitBodyTestId {
    ROOT = 'menu-init-body',
    BUILD_BUTTON = 'menu-init-body__build-button'
}

export enum SelectOptionTestId {
    ROOT = 'select-option'
}

export type MenuFolderTestId = DraftsFolderTestId.ROOT | WmsStoresFolderTestId.ROOT | WmsZonesFolderTestId.ROOT;

export type WmsZoneGroupTestId = SidebarMenuGroupTestId.WMS_ZONE_ACTIVE | SidebarMenuGroupTestId.WMS_ZONE_DISABLED;

export function formatAnalyticsTooltipIconTestId(type: string) {
    return `${AnalyticsTooltipTestId.ICON}_${type}`;
}

export function formatLayersMenuGroupRootTestId(groupType: string) {
    return `${SidebarMenuGroupTestId.ROOT}_${groupType}`;
}

export function formatInputRootTestId(name: string) {
    return `${InputTestId.ROOT}_${name}`;
}

export function formatTextAreaRootTestId(name: string) {
    return `${TextAreaTestId.ROOT}_${name}`;
}

export function formatSidebarMenuFolderRootTestId(domId: string) {
    return `${SidebarMenuFolderTestId.ROOT}_${domId}`;
}

export function formatSidebarMenuFolderVisibleTestId(domId: string) {
    return `${SidebarMenuFolderTestId.VISIBLE}_${domId}`;
}

export function formatAnalyticsTooltipContentTestId(type: string) {
    return `${AnalyticsTooltipTestId.CONTENT}_${type}`;
}

export function formatFilterTypesOptionTestId(filterName: FilterName) {
    return `${FiltersMenuTestId.FILTER_TYPES_OPTIONS}_${filterName}`;
}

export function formatFilterDeleteButtonTestId(filterName: FilterName) {
    return `${FiltersMenuTestId.DELETE_FILTER}_${filterName}`;
}

export function formatFilterMenuCheckboxTestId(filterName: FilterName, value: string | boolean) {
    return `${FiltersMenuTestId.ROOT}_${filterName}_${value}`;
}

export function formatNoAnalyticsMenuTestId(entity: AnalystEntity) {
    return `${NoAnalyticsMenuTestId.ROOT}_${entity}`;
}

export function formatManagerZoneEditorMapPointTestId(index: number) {
    return `${ManagerZoneEditorTestId.MAP_POINT}_${index}`;
}

export function formatDropdownMenuTestId(baseTestId: string) {
    return `${baseTestId}-dropdown-menu`;
}

export function formatDropdownLoaderTestId(baseTestId: string) {
    return `${baseTestId}-loader`;
}

export function formatSelectOptionRootTestId(option: string) {
    return `${SelectOptionTestId.ROOT}_${option}`;
}

export function formatMapMenuRootTestId(domId: string) {
    return `${MapMenuTestId.ROOT}_${domId}`;
}

export function formatMapLayersMenuAnalyticsFilterOptionTestId(entity: AnalystEntity) {
    return `${MapLayersMenuAnalyticsTestId}_${entity}`;
}

export function formatCitySelectOptionTestId(id: string | number) {
    return `${CitySelectTestId.OPTION}_${id}`;
}

export function formatRegionSelectOptionTestId(region: string | number) {
    return `${RegionSelectTestId.OPTION}_${region}`;
}
