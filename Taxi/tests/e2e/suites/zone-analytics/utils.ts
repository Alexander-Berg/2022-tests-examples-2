import type {AnalystEntity} from 'types/analyst';
import {Currency} from 'types/common';
import {
    formatAnalyticsTooltipContentTestId,
    formatAnalyticsTooltipIconTestId,
    MapMenuAnalyticTestId
} from 'types/test-id';

export const numberFormatter = new Intl.NumberFormat('RU', {});
export const currencyFormatter = new Intl.NumberFormat('RU', {
    style: 'currency',
    currency: Currency.RUB,
    currencyDisplay: 'narrowSymbol',
    maximumFractionDigits: 2
});

export function replaceNbsp(str: string) {
    return str.replace(new RegExp(`${String.fromCharCode(160)}`, 'g'), ' ');
}

export async function toggleSectionAudience(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapMenuAnalyticTestId.PANEL_HEADER_AUDIENCE);
}

export async function toggleSectionTaxi(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapMenuAnalyticTestId.PANEL_HEADER_TAXI);
}

export async function toggleSectionEda(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapMenuAnalyticTestId.PANEL_HEADER_EDA);
}

export async function toggleSectionLavka(ctx: Hermione.TestContext) {
    await ctx.browser.clickIntoEnsured(MapMenuAnalyticTestId.PANEL_HEADER_LAVKA);
}

export async function assertEntityDescription(ctx: Hermione.TestContext, entity: AnalystEntity) {
    await ctx.browser.moveMouseTo(formatAnalyticsTooltipIconTestId(entity));
    await ctx.browser.waitForTestIdSelectorDisplayed(formatAnalyticsTooltipContentTestId(entity));
    await ctx.browser.assertImage(formatAnalyticsTooltipContentTestId(entity), {snapshotName: entity});
}
