import {
    assertMapAndSidebarWithoutControls,
    assertMapWithoutControls,
    toggleLayersMenuFolder
} from 'tests/e2e/utils/common';
import {openPageAndWaitRendered} from 'tests/e2e/utils/map-actions';
import {parseSpreadSheetCSV, parseSpreadSheetJSON} from 'tests/e2e/utils/parse-spreadsheet';
import {describe, expect, it} from 'tests/hermione.globals';

import {STAFF_URL} from '@/src/constants';
import {ROUTES} from '@/src/constants/routes';
import {getDomIdFromEntityId} from 'client/lib/dom-id-converter';
import {MapEntity} from 'client/store/entities/types';
import {authObjectMock} from 'server/middlewares/mocks/auth';
import {config} from 'service/cfg';
import {formatSearchEntityId, SearchEntity} from 'types/search';
import {
    AuthorInfoTestId,
    CreatePointMenuTestId,
    DraftsDescriptionTestId,
    DraftsFolderTestId,
    EditPointMenuTestId,
    ExportIconTestId,
    ExportMenuTestId,
    formatDropdownLoaderTestId,
    formatDropdownMenuTestId,
    formatInputRootTestId,
    formatManagerZoneEditorMapPointTestId,
    formatMapMenuRootTestId,
    formatSelectOptionRootTestId,
    formatSidebarMenuFolderRootTestId,
    formatSidebarMenuFolderVisibleTestId,
    formatTextAreaRootTestId,
    ManagerZoneEditMenuTestId,
    ManagerZoneViewMenuTestId,
    MapControlPlaneTestId,
    MapMenuTestId,
    MapSearchTestId,
    MapTestId,
    SidebarMenuFolderTestId,
    SidebarMenuItemsListTestId,
    SidebarMenuTestId,
    StartrekTicketTestId
} from 'types/test-id';

const ST_TICKET_VALID = 'ORDER-66';
const ST_TICKET_NOT_VALID = 'CRINGE';

describe('Черновики', function () {
    it('Скролл списка черновиков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.performScroll([DraftsFolderTestId.ROOT, SidebarMenuItemsListTestId.ITEMS_LIST], {});
        await this.browser.assertImage(SidebarMenuTestId.ROOT);
    });

    it('Развернуть-свернуть раздел черновиков в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage([SidebarMenuTestId.ROOT]);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage(SidebarMenuTestId.ROOT);
    });

    it('Смена видимости всех черновиков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
        await assertMapWithoutControls(this);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
        await assertMapWithoutControls(this);
    });

    it('Смена видимости черновика зоны', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderVisibleTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderVisibleTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);
    });

    it('Смена видимости черновика стора', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderVisibleTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderVisibleTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);
    });

    it('Ховер на черновик в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domIdZone = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '3');
        const domIdPoint = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.moveMouseTo([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domIdPoint)]);
        await assertMapAndSidebarWithoutControls(this);
        await this.browser.moveMouseTo([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domIdZone)]);
        await assertMapAndSidebarWithoutControls(this);
    });

    it('Клик в черновик зоны в сайдбаре открывает его на карте', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });
        await assertMapWithoutControls(this);
    });

    it('Клик в черновик стора в сайдбаре открывает его на карте', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });
        await assertMapWithoutControls(this);
    });

    it('Повторный клик в черновик зоны закрывает его', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.moveMouseTo(MapTestId.ROOT);

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.moveMouseTo([MapTestId.ROOT]);

        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);
    });

    it('Повторный клик в черновик стора закрывает его', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '3');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.moveMouseTo([MapTestId.ROOT]);
        await this.browser.assertImage([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)]);
        await assertMapWithoutControls(this);
    });

    it('Открытие черновика зоны по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                selectedDomIds: 'zone_drafts-1'
            }
        });

        await this.browser.waitUntilRendered();

        await assertMapWithoutControls(this);
    });

    it('Открытие черновика стора по прямой ссылке', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                selectedDomIds: 'point_drafts-2'
            }
        });

        await assertMapWithoutControls(this);
    });

    it('Выгрузка geojson по черновикам из сайдбара', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.moveMouseTo([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER, ExportIconTestId.ROOT], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.clickInto([ExportMenuTestId.ITEM_GEO_JSON], {
            waitForClickable: true,
            waitRender: true
        });

        const file = await this.browser.getDownloadedFile('drafts.geojson', {purge: true});
        expect(parseSpreadSheetCSV(file)).to.matchSnapshot(this);
    });

    it('По ховеру на раздел Черновиков появляется кнопка Экспорта', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.moveMouseTo([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
        await this.browser.assertImage([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
    });

    it('Экспорт аналитики черновиков', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();
        await this.browser.moveMouseTo([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER]);
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER, ExportIconTestId.ROOT], {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.clickInto([ExportMenuTestId.ITEM_ANALYTICS], {
            waitForClickable: true,
            waitRender: true
        });

        const file = await this.browser.getDownloadedFile('draft_zones_analytics.xlsx', {purge: true});
        expect(parseSpreadSheetJSON(file)).to.matchSnapshot(this);
    });

    it('Переместить точку черновика зоны', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickIntoEnsured({selector: `#ymaps3x0--feature-3-${domId}`});
        await this.browser.clickInto(ManagerZoneViewMenuTestId.BUTTON_ACTION, {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.dragAndDrop(formatManagerZoneEditorMapPointTestId(1), {coordinates: {x: 100, y: -100}});

        await this.browser.clickInto(ManagerZoneEditMenuTestId.BUTTON_ACTION, {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.clickInto(MapMenuTestId.CLOSE, {
            waitForClickable: true,
            waitRender: true
        });

        await assertMapWithoutControls(this);
    });

    it('Добавить тикет черновику зоны', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto(
            [MapTestId.ROOT, formatMapMenuRootTestId(domId), ManagerZoneViewMenuTestId.BUTTON_ACTION],
            {
                waitForClickable: true,
                waitRender: true
            }
        );

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], ST_TICKET_VALID);

        await this.browser.waitForTestIdSelectorClickable(ManagerZoneEditMenuTestId.BUTTON_ACTION);

        await this.browser.clickInto([ManagerZoneEditMenuTestId.BUTTON_ACTION], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.waitForTestIdSelectorInDom([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);
        await this.browser.waitUntilRendered();
        await this.browser.assertImage([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);
    });

    it('Валидный тикет черновика стора меняет цвет иконки тикета на синий', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([MapTestId.ROOT, formatMapMenuRootTestId(domId), EditPointMenuTestId.EDIT_BTN], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], ST_TICKET_VALID);

        await this.browser.assertImage([MapTestId.ROOT, CreatePointMenuTestId.MAP_MENU]);
    });

    it('Невалидный тикет черновика зоны меняет цвет иконки тикета на серый', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto(
            [MapTestId.ROOT, formatMapMenuRootTestId(domId), ManagerZoneViewMenuTestId.BUTTON_ACTION],
            {
                waitForClickable: true,
                waitRender: true
            }
        );

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], ST_TICKET_NOT_VALID);

        await this.browser.assertImage(ManagerZoneEditMenuTestId.ROOT);
    });

    it('Клик в тикет черновика стора открывает трекер', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([MapTestId.ROOT, formatMapMenuRootTestId(domId), EditPointMenuTestId.EDIT_BTN], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], ST_TICKET_VALID);

        await this.browser.clickInto([MapTestId.ROOT, `${CreatePointMenuTestId.ACTION_SAVE}`], {
            waitForClickable: true,
            waitRender: true
        });

        const link = await this.browser.assertBySelector([MapTestId.ROOT, StartrekTicketTestId.ROOT]);
        const url = await link.getProperty('href');
        expect(url).to.equal(`${config.app.trackerBaseUrl}${ST_TICKET_VALID}`);
    });

    it('Клик в автора черновика стора открывает стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1');

        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        const link = await this.browser.assertBySelector([MapTestId.ROOT, AuthorInfoTestId.LINK]);
        const url = await link.getProperty('href');
        expect(url).to.equal(`${STAFF_URL}${authObjectMock.login}`);
    });

    it('Клик в автора черновика зоны открывает стафф', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');

        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        const link = await this.browser.assertBySelector([MapTestId.ROOT, AuthorInfoTestId.LINK]);
        const url = await link.getProperty('href');
        expect(url).to.equal(`${STAFF_URL}${authObjectMock.login}`);
    });

    it('Удалить тикет черновика', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto(
            [MapTestId.ROOT, formatMapMenuRootTestId(domId), ManagerZoneViewMenuTestId.BUTTON_ACTION],
            {
                waitForClickable: true,
                waitRender: true
            }
        );

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], ST_TICKET_VALID);

        await this.browser.clickInto([MapTestId.ROOT, ManagerZoneEditMenuTestId.BUTTON_ACTION], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.waitForTestIdSelectorInDom([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);
        await this.browser.waitUntilRendered();

        await this.browser.assertImage([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);

        await this.browser.clickInto(
            [MapTestId.ROOT, formatMapMenuRootTestId(domId), ManagerZoneViewMenuTestId.BUTTON_ACTION],
            {
                waitForClickable: true,
                waitRender: true
            }
        );

        await this.browser.typeInto([MapTestId.ROOT, formatInputRootTestId('ticketSlug')], '', {clear: true});

        await this.browser.clickInto([MapTestId.ROOT, ManagerZoneEditMenuTestId.BUTTON_ACTION], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.assertImage([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);
    });

    it('Добавить url в описанию зоны', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1');
        await this.browser.clickInto([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto([DraftsFolderTestId.ROOT, formatSidebarMenuFolderRootTestId(domId)], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.clickInto(
            [MapTestId.ROOT, formatMapMenuRootTestId(domId), ManagerZoneViewMenuTestId.BUTTON_ACTION],
            {
                waitForClickable: true,
                waitRender: true
            }
        );

        await this.browser.typeInto(
            [MapTestId.ROOT, formatTextAreaRootTestId('description')],
            config.app.yandexMapUrl.ru
        );

        await this.browser.waitForTestIdSelectorClickable(ManagerZoneEditMenuTestId.BUTTON_ACTION);

        await this.browser.clickInto([ManagerZoneEditMenuTestId.BUTTON_ACTION], {
            waitForClickable: true,
            waitRender: true
        });

        await this.browser.waitForTestIdSelectorInDom([MapTestId.ROOT, formatMapMenuRootTestId(domId)]);
        await this.browser.waitUntilRendered();

        await this.browser.clickInto([MapTestId.ROOT, DraftsDescriptionTestId.TEXT_EXPAND], {
            waitForClickable: true,
            waitRender: true
        });

        const handles = await this.browser.getWindowHandles();
        expect(handles.length).to.equal(2);

        await this.browser.switchToWindow(handles[1]);
        expect(await this.browser.getUrl()).to.contain(config.app.yandexMapUrl.ru);

        await this.browser.closeWindow();
        await this.browser.switchToWindow(handles[0]);
    });

    it('Поиск и выбор скрытого черновика зоны делает его видимым', async function () {
        await openPageAndWaitRendered(this, {
            z: '10.75',
            ll: '37.6659794634276,55.84503951076609'
        });
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await this.browser.clickIntoEnsured([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE]);

        await this.browser.clickIntoEnsured(MapControlPlaneTestId.MAP_SEARCH);
        await this.browser.typeInto([MapControlPlaneTestId.MAP_SEARCH, {selector: 'input'}], 'черновик зоны');
        await this.browser.waitForTestIdSelectorNotInDom([formatDropdownLoaderTestId(MapSearchTestId.SELECT)]);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(
            [
                formatDropdownMenuTestId(MapSearchTestId.SELECT),
                formatSelectOptionRootTestId(formatSearchEntityId(SearchEntity.MANAGER_ZONES, '1'))
            ],
            {waitRender: true}
        );
        await this.browser.assertImage(formatMapMenuRootTestId(getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '1')));
        await this.browser.assertImage(DraftsFolderTestId.ROOT);
    });

    it('Поиск и выбор скрытого стора делает его видимым', async function () {
        await openPageAndWaitRendered(this, {
            z: '10.75',
            ll: '37.6659794634276,55.84503951076609'
        });
        await toggleLayersMenuFolder(this, DraftsFolderTestId.ROOT);
        await this.browser.clickIntoEnsured([DraftsFolderTestId.ROOT, SidebarMenuFolderTestId.VISIBLE]);

        await this.browser.clickIntoEnsured(MapControlPlaneTestId.MAP_SEARCH);
        await this.browser.typeInto([MapControlPlaneTestId.MAP_SEARCH, {selector: 'input'}], 'черновик точки');
        await this.browser.waitForTestIdSelectorNotInDom([formatDropdownLoaderTestId(MapSearchTestId.SELECT)]);
        await this.browser.waitUntilRendered();
        await this.browser.clickInto(
            [
                formatDropdownMenuTestId(MapSearchTestId.SELECT),
                formatSelectOptionRootTestId(formatSearchEntityId(SearchEntity.MANAGER_POINTS, '1'))
            ],
            {waitRender: true}
        );
        await this.browser.assertImage(formatMapMenuRootTestId(getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1')));
        await this.browser.assertImage(DraftsFolderTestId.ROOT);
    });
});
