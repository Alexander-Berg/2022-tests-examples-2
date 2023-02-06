import {ROUTES} from '@/src/constants/routes';
import type {AttributeType} from 'types/attribute';

export async function createAttribute(
    ctx: Hermione.TestContext,
    options: {type: AttributeType; max?: number; isImmutable?: true; isConfirmable?: true}
) {
    await ctx.browser.openPage(ROUTES.CLIENT.CREATE_ATTRIBUTE);
    await ctx.browser.clickInto('attribute-type', {waitRender: true});
    await ctx.browser.clickInto(options.type, {waitRender: true});
    await ctx.browser.typeInto('code', `test_${options.type}_attribute_code`);
    await ctx.browser.typeInto('ticket-parameter', 'https://st.yandex-team.ru/LAVKACONTENT-666');

    if (options.max) {
        await ctx.browser.clickInto('is-array');
        await ctx.browser.typeInto('max-array-size', options.max.toFixed(0), {clear: true});
    }

    if (options.isImmutable) {
        await ctx.browser.clickInto('is-immutable');
    }

    if (options.isConfirmable) {
        await ctx.browser.clickInto('is-confirmable');
    }

    await ctx.browser.clickInto('submit-button', {waitRender: true});
    await ctx.browser.waitForTestIdSelectorNotInDom(['header-panel', 'submit-button']);

    const currentUrl = await ctx.browser.getUrl();
    const urlParts = currentUrl.split('/');
    const attributeId = Number.parseInt(urlParts[urlParts.length - 1]);

    return {id: attributeId};
}
