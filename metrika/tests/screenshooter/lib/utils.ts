import { Page } from "@playwright/test";
import { Report } from "./report";

export async function addToLocalStorage(page: Page, params: string[][]) {
    await page.evaluate((params) => {
        params.forEach((param) => {
            window.localStorage.setItem(param[0], param[1]);
        });
    }, params);
}

export async function waitForReport(page: Page, selector: string) {
    let loaders = page.locator(selector);
    let size = await loaders.count();
    for (let i = 0; i < size; i++) {
        if (loaders.nth(i).isVisible) {
            await loaders.nth(i).waitFor({ state: "hidden" });
        }
    }
    // Есть отчеты с большим количеством последовательных загрузок
    // Данный метод позволяет дождаться построения отчетов не прибегая к принудительным паузам
    loaders = page.locator(selector);
    size = await loaders.count();
    for (let i = 0; i < size; i++) {
        if (loaders.nth(i).isVisible) {
            await loaders.nth(i).waitFor({ state: "hidden" });
        }
    }
}

export async function getMocks(page: Page, report: Report) {
    for (const mock of report.mocks) {
        await page.route(mock.request, route => {
            route.fulfill({
                body: JSON.stringify(mock.response)
            });
        });
    }
}
