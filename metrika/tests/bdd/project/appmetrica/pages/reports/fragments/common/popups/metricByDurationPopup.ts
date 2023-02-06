
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, InputElement} from "../../../../../../../lib";

export class MetricByDurationPopupFragment extends BaseComponent {
    periodButton: ButtonElement;
    durationInput: InputElement;
    applyChangesButton: ButtonElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Picker for duration and period metric");

        this.periodButton = new ButtonElement(
            this.locator.locator(".sc-jTNJqp.kUvLlx button"),
            this,
            "Period button"
        );
        this.durationInput = new InputElement(
            this.locator.locator(".sc-hmyDHa.hScwaN input"),
            this,
            "Input duration field"
        );
        this.applyChangesButton = new ButtonElement(
            this.locator.locator(".sc-erOsFi.cMMMdG button"),
            this,
            "Apply changes"
        );
    }
}
