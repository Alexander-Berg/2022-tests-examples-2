import { Locator } from "playwright-core";
import {BasePage, ButtonElement} from "../../../../../lib";

export class ButtonReportElement extends ButtonElement {
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
    }
    async clickAndWait(page: BasePage, selector?: string): Promise<void> {
        await this.locator.click({ timeout: global.clickTimeout });
        await page.waitForReport(selector);
    }
}
