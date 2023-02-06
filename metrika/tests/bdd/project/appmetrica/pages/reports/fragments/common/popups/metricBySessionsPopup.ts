
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, InputElement} from "../../../../../../../lib";

export class MetricBySessionsPopupFragment extends BaseComponent {
    numberOfSessions: InputElement;
    applyChangesButton: ButtonElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Picker for loyal users metric");

        this.numberOfSessions = new InputElement(
            this.locator.locator(".sc-hmyDHa.hScwaN input"),
            this,
            "Input number of sessions field"
        );
        this.applyChangesButton = new ButtonElement(
            this.locator.locator(".sc-erOsFi.cMMMdG button"),
            this,
            "Apply changes"
        );
    }
}
