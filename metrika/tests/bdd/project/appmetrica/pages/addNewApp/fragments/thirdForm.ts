import { Locator } from "playwright-core";
import { BaseComponent, ButtonElement } from "../../../../../lib";

export class ThirdFormComponent extends BaseComponent {
    buttonGoToReports: ButtonElement;

    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);

        this.buttonGoToReports = new ButtonElement(
            this.locator.locator(".sc-laTMn.fLNJyn").nth(1),
            this,
            "Go to reports button"
        );
    }
}
