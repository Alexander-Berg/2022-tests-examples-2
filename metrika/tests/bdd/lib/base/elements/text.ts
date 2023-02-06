import { Locator } from "playwright-core";
import { BaseElement } from "../element";

export class TextElement extends BaseElement {
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
    }
}
