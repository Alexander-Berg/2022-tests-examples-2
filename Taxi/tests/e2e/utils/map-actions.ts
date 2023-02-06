import {getDomIdFromEntityId} from 'client/lib/dom-id-converter';
import {MapEntity} from 'client/store/entities/types';
import {ROUTES} from 'constants/routes';

type EntityType = MapEntity.POINT_DRAFTS | MapEntity.ZONE_DRAFTS | MapEntity.WMS_ZONES | MapEntity.WMS_STORES;

export async function openPageAndWaitRendered(
    ctx: Hermione.TestContext,
    queryParams?: Record<string, unknown>,
    uuid?: string
) {
    await ctx.browser.openPage(ROUTES.CLIENT.ROOT, {
        uuid,
        region: 'ru',
        queryParams: {
            z: '15',
            ll: '37.817346618331314,55.91777177683962',
            ...queryParams
        }
    });
    await ctx.browser.waitUntilRendered();
}

export async function clickObjectOnMap(ctx: Hermione.TestContext, entity: EntityType, id: string) {
    const entityLayerId = (() => {
        switch (entity) {
            case MapEntity.WMS_ZONES:
                return 1;
            case MapEntity.ZONE_DRAFTS:
                return 3;
            case MapEntity.WMS_STORES:
                return 2;
            case MapEntity.POINT_DRAFTS:
                return 4;
        }
    })();
    const domId = getDomIdFromEntityId(entity, id);
    await ctx.browser.clickInto(
        {selector: `#ymaps3x0--feature-${entityLayerId}-${domId}`},
        {
            waitRender: true,
            hoverBeforeClick: true
        }
    );
}
