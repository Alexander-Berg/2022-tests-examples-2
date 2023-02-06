
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, Collection, InputElement} from "../../../../../../../lib";

export class MetricWithEventsPopupFragment extends BaseComponent {
    eventsList: Collection<ButtonElement>;
    applyChangesButton: ButtonElement;
    searchField: InputElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Picker for loyal users metric");

        this.eventsList = new Collection<ButtonElement>(
            this.locator.locator(".sc-iRbamj.blSEcj"),
            this,
            ButtonElement,
            "Events list"
        );
        this.applyChangesButton = new ButtonElement(
            this.locator.locator(".sc-erOsFi.cMMMdG button"),
            this,
            "Apply changes"
        );
        this.searchField = new InputElement(
            this.locator.locator(".textinput__control"),
            this,
            "Search field"
        );
    }
}
