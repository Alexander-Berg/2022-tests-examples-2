import { Locator } from "playwright-core";
import { BaseElement } from "../element";
import { Clickable } from "./interfaces";

export class ButtonElement extends BaseElement implements Clickable {
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
    }

    async click(): Promise<void> {
        await this.locator.click({ timeout: global.clickTimeout });
    }
}
