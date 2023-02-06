import { Locator } from "playwright-core";
import { Collection } from "./collection";

export class BaseComponent {
    parent: any;
    locator: Locator;
    name: string | null;
    constructor(locator: Locator, parent: any, name?: string) {
        this.locator = locator;
        this.parent = parent;
        this.name = name ? name : null;
    }

    async get() {
        return this.locator;
    }

    async click() {
        await this.locator.click({ timeout: global.clickTimeout });
    }

    async getText() {
        return await this.locator.textContent();
    }

    async getElementByText(text: string) {
        return new BaseComponent(
            this.locator.locator(`text=${text}`),
            this,
            `Element "${text}"`
        );
    }

    async getElementsByText(text: string, child: any) {
        return new Collection(
            this.locator.locator(`text=${text}`),
            this,
            child,
            `Elements "${text}"`
        );
    }

    async isVisible() {
        return this.locator.isVisible();
    }

    async waitForVisible() {
        await this.locator.waitFor({ state: "visible" });
    }

    async delay(time: number) {
        return new Promise((resolve) => {
            setTimeout(resolve, time);
        });
    }
}
