import {infoModels} from 'tests/e2e/seed-db-map';

import {ROUTES} from '@/src/constants/routes';
import type {RegionCode} from 'types/region';

export async function addAttributeToInfomodelByCode(
    ctx: Hermione.TestContext,
    options: {code: string; infomodelId?: number; region?: Lowercase<RegionCode>}
) {
    await ctx.browser.openPage(ROUTES.CLIENT.INFOMODEL(options.infomodelId ?? infoModels.ru.info_model_code_1_14), {
        region: options.region ?? 'ru'
    });
    await ctx.browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
    await ctx.browser.clickInto(['attributes-search']);
    await ctx.browser.typeInto('attributes-search', options.code);
    await ctx.browser.waitUntilRendered();
    await ctx.browser.waitForTestIdSelectorInDom(options.code);
    await ctx.browser.clickInto(['attribute-select-virtual-list', options.code]);
    await ctx.browser.clickInto('im-user_attributes-table', {
        waitRender: true
    });
    await ctx.browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
    await ctx.browser.clickInto([`im_attribute_row_${options.code}`, 'switch-important']);
    await ctx.browser.clickInto('submit-button');
    await ctx.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);
}
