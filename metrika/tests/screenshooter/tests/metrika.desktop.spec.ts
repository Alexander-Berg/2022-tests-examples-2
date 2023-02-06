import { test, expect, Page } from "@playwright/test";
import { dashboards, reports, metrikaIgnoreElements } from "../data";
import { waitForReport } from "../lib";

let page: Page;

test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext({ storageState: 'state.json', ignoreHTTPSErrors: true });
    page = await context.newPage();
});

test.afterAll(async () => {
    await page.close();
});

test.describe.parallel("Метрика: десктопная версия", () => {
    dashboards.forEach((dashboard, index) => {
        test(`Дашборд ${index}`, async () => {
            await page.goto(dashboard.url);
            await page
                .locator(dashboard.selector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, dashboard.loaderSelector);
            await page.waitForTimeout(dashboard.pause ? dashboard.pause : 0);
            const ignoreElements = [];
            metrikaIgnoreElements.forEach(e => {
                ignoreElements.push(page.locator(e));
            });
            expect(await page.locator(dashboard.selector).screenshot({ animations: 'disabled', 
                                                                       mask: ignoreElements }))
                .toMatchSnapshot(`dash-${index}.png`, { threshold: 0.4, maxDiffPixelRatio: 0.002 });
        });
    });

    reports.forEach((report, index) => {
        test(`Отчет ${report.name}`, async () => {
            await page.goto(report.url);
            await page
                .locator(report.selector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, report.loaderSelector);
            await page.waitForTimeout(report.pause ? report.pause : 0);
            const ignoreElements = [];
            metrikaIgnoreElements.forEach(e => {
                ignoreElements.push(page.locator(e));
            });
            expect( await page.locator(report.selector).screenshot({ animations: 'disabled', 
                                                                     mask: ignoreElements }))
                .toMatchSnapshot(`report-${index}.png`, { threshold: 0.4, maxDiffPixelRatio: 0.002 });
        });
    });
});
