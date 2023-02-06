import { Locator } from "playwright-core";
import { BaseElement } from "../element";
import { Clickable, Fillable } from "./interfaces";

export class InputElement extends BaseElement implements Clickable, Fillable {
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
    }
    async click(): Promise<void> {
        await this.locator.click({ timeout: global.clickTimeout });
    }

    async fill(value: string): Promise<void> {
        await this.locator.fill(value);
    }

    async getText() {
        return await this.locator.inputValue();
    }
}
