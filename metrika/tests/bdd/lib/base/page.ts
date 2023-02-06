import { Page } from "playwright-core";
import { BaseComponent } from "./component";

export class BasePage {
    name: string;
    path: string;
    page: Page;
    constructor(page: Page, name: string, path: string) {
        this.page = page;
        this.name = name;
        this.path = path;
    }
    async goto(url: string) {
        await this.page.goto(url);
    }

    async get() {
        return this.page;
    }

    async getElementByText(text: string) {
        return new BaseComponent(
            this.page.locator(`text=${text}`),
            this,
            `Element "${text}"`
        );
    }

    async waitForReport(selector?: string) {
        if (!selector){
            selector = ".spin2";
        }
        let loaders = this.page.locator(selector);
        let size = await loaders.count();
        for (let i = 0; i < size; i++) {
            if (await loaders.nth(i).isVisible) {
                await loaders.nth(i).waitFor({state: "hidden"});
            }
        }
        // Есть отчеты с большим количеством последовательных загрузок
        // Данный метод позволяет дождаться построения отчетов не прибегая к принудительным паузам
        loaders = this.page.locator(selector);
        size = await loaders.count();
        for (let i = 0; i < size; i++) {
            if (await loaders.nth(i).isVisible) {
                await loaders.nth(i).waitFor({state: "hidden"});
            }
        }
    }
}
