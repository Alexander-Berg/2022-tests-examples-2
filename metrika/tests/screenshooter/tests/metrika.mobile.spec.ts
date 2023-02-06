import { test, expect, Page } from "@playwright/test";
import { dashboards, reports, metrikaIgnoreElements } from "../data";
import { waitForReport } from "../lib";

let page: Page;

test.beforeAll(async ({ browser }) => {
    // const context = await browser.newContext({
    //     ignoreHTTPSErrors: true,
    //     viewport: { width: 411, height: 1600 },
    // });
    const context = await browser.newContext({ 
        storageState: 'state.json', 
        ignoreHTTPSErrors: true,
        viewport: { width: 411, height: 1600 }
     });
    page = await context.newPage();
});

test.afterAll(async () => {
    await page.close();
});

test.describe.parallel("Метрика: мобильная версия. ", () => {
    dashboards.forEach((dashboard, index) => {
        test(`Дашборд ${index}`, async () => {
            await page.goto(dashboard.url);
            await page
                .locator(dashboard.mobileSelector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, dashboard.mobileLoaderSelector);
            const ignoreElements = [];
            metrikaIgnoreElements.forEach(e => {
                ignoreElements.push(page.locator(e));
            });
            expect(await page.screenshot({ fullPage: false, 
                                           animations: 'disabled', 
                                           mask: ignoreElements }))
                .toMatchSnapshot(`dash-${index}.png`,{ threshold: 0.4, maxDiffPixelRatio: 0.002 });
        });
    });

    reports.filter((r) => r.isMobile !== false).forEach((report, index) => {
        test(`Отчет ${report.name}`, async () => {
            await page.goto(report.url);
            await page
                .locator(report.mobileSelector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, report.mobileLoaderSelector);
            const ignoreElements = [];
            metrikaIgnoreElements.forEach(e => {
                ignoreElements.push(page.locator(e));
            });
            expect(await page.screenshot({ fullPage: false, 
                                           animations: 'disabled', 
                                           mask: ignoreElements }))
                .toMatchSnapshot(`report-${index}.png`, { threshold: 0.4, maxDiffPixelRatio: 0.002 });
            });
        });
});
