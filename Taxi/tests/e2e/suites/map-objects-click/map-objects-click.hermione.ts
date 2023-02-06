import {describe, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {getDomIdFromEntityId} from 'client/lib/dom-id-converter';
import {MapEntity} from 'client/store/entities/types';
import {
    formatMapMenuRootTestId,
    LayersMenuButtonTestId,
    MapLayersMenuAnalyticsTestId,
    SidebarMenuFolderTestId,
    SidebarTestId,
    WmsStoresFolderTestId
} from 'types/test-id';

describe('Клик в объекты на карте', function () {
    it('Каждый клик в стор разворачивает список сторов в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                z: '14',
                ll: '37.50987099965221,55.94074826940243'
            }
        });
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.WMS_STORES, '7');
        await this.browser.clickInto(
            {selector: `#ymaps3x0--feature-2-${domId}`},
            {
                hoverBeforeClick: true
            }
        );
        await this.browser.waitForTestIdSelectorInDom(formatMapMenuRootTestId(domId));
        await this.browser.assertImage(SidebarTestId.ROOT);

        await this.browser.clickInto([WmsStoresFolderTestId.ROOT, SidebarMenuFolderTestId.HEADER], {
            waitRender: true,
            waitForClickable: true
        });

        const domId2 = getDomIdFromEntityId(MapEntity.WMS_STORES, '8');
        await this.browser.clickInto(
            {selector: `#ymaps3x0--feature-2-${domId2}`},
            {
                hoverBeforeClick: true
            }
        );
        await this.browser.waitForTestIdSelectorInDom(formatMapMenuRootTestId(domId2));
        await this.browser.assertImage(SidebarTestId.ROOT);
    });

    // eslint-disable-next-line max-len
    it('Клик на зону при выключенном слое аналитики открывает ее меню и подсвечивает эту зону в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                z: '14',
                ll: '37.50987099965221,55.94074826940243'
            }
        });
        await this.browser.waitUntilRendered();

        await this.browser.clickInto(LayersMenuButtonTestId.ROOT, {waitRender: true, waitForClickable: true});
        await this.browser.clickInto(`${MapLayersMenuAnalyticsTestId.SWITCH}`, {
            waitRender: true,
            waitForClickable: true
        });

        const domId = getDomIdFromEntityId(MapEntity.WMS_ZONES, '7');
        await this.browser.clickIntoEnsured({selector: `#ymaps3x0--feature-1-${domId}`});
        await this.browser.assertImage(SidebarTestId.ROOT);
        await this.browser.assertImage(formatMapMenuRootTestId(domId));
    });

    // eslint-disable-next-line max-len
    it('Клик на зону при включенном слое аналитики открывает ее меню и подсвечивает эту зону в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                z: '14',
                ll: '37.50987099965221,55.94074826940243'
            }
        });
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.WMS_ZONES, '7');
        await this.browser.clickIntoEnsured({selector: `#ymaps3x0--feature-1-${domId}`});
        await this.browser.assertImage(SidebarTestId.ROOT);
        await this.browser.assertImage(formatMapMenuRootTestId(domId));
    });

    it('Клик в черновик зоны открывает ее меню и подсвечивает ее в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                z: '14',
                ll: '37.50987099965221,55.94074826940243'
            }
        });
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '4');
        await this.browser.clickIntoEnsured({selector: `#ymaps3x0--feature-3-${domId}`});
        await this.browser.assertImage(SidebarTestId.ROOT);
        await this.browser.assertImage(formatMapMenuRootTestId(domId));
    });

    it('Клик в черновик стора открывает его меню и подсвечивает его в сайдбаре', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {
            region: 'ru',
            queryParams: {
                z: '14',
                ll: '37.50987099965221,55.94074826940243'
            }
        });
        await this.browser.waitUntilRendered();

        const domId = getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '9');
        await this.browser.clickInto(
            {selector: `#ymaps3x0--feature-4-${domId}`},
            {
                waitRender: true,
                hoverBeforeClick: true
            }
        );
        await this.browser.assertImage(SidebarTestId.ROOT);
        await this.browser.assertImage(formatMapMenuRootTestId(domId));
    });
});
