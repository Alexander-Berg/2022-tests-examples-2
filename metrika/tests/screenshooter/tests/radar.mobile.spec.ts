import { test, expect, Page } from "@playwright/test";
import { radar_reports } from "../data";
import {  waitForReport } from "../lib";

let page: Page;

test.use({ viewport: { width: 428, height: 926 } });
test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    page = await context.newPage();
    await page.goto("/");
});

test.afterAll(async () => {
    await page.close();
});

test.describe.parallel("Радар: мобильная версия", () => {
    radar_reports.forEach((report, index) => {
        test(`Отчет ${report.name}`, async () => {
            await page.goto(report.url);
            await page
                .locator(report.mobileSelector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, report.mobileLoaderSelector);
            expect(await page.screenshot({ fullPage: false,
                                           animations: 'disabled'}))
                .toMatchSnapshot(`report-${index}.png`, { threshold: 0.4, maxDiffPixelRatio: 0.002 });
        });
    });
});
