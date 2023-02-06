import { test, expect, Page } from "@playwright/test";
import { appmetReports} from "../data";
import { waitForReport, getMocks } from "../lib";

let page: Page;

test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext({ storageState: 'state.json', ignoreHTTPSErrors: true });
    page = await context.newPage();
});

test.afterAll(async () => {
    await page.close();
});

test.describe.parallel("Appmetrica: десктопная версия", () => {
    appmetReports.forEach((report, index) => {
        test(`Отчет ${report.name}`, async () => {
            if (report.mocks){await getMocks(page, report);}
            await page.goto(report.url);
            await page
                .locator(report.selector)
                .waitFor({ state: "visible", timeout: 35000 });
            await waitForReport(page, report.loaderSelector);
            await page.waitForTimeout(report.pause ? report.pause : 0);
            const ignoreElements = [];
            if(report.ignoreElements){report.ignoreElements.forEach(e => {
                ignoreElements.push(page.locator(e));
            });}
            expect( await page.locator(report.selector).screenshot({ animations: 'disabled',
                                                                     mask: ignoreElements}))
                .toMatchSnapshot(`report-${index}.png`, { threshold: 0.4, maxDiffPixelRatio: 0.0015 });
        });
    });
});
